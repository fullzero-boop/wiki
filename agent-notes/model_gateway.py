#!/usr/bin/env python3
"""
model_gateway.py — HTTP-прокси между агентом и DeepSeek.

Как работает:
  1. Агент шлёт запрос на model_gateway вместо DeepSeek API
  2. Gateway анализирует содержимое запроса
  3. Если вопрос простой → deepseek-chat
  4. Если сложный → deepseek-reasoner
  5. Проксирует ответ обратно агенту

Запуск:
  python3 model_gateway.py [--port 18889]

Интеграция:
  В config.yaml агента:
    model:
      provider: openai  # используем openai-совместимый интерфейс
      base_url: http://localhost:18889/v1  # наш gateway
      default: model_router  # любой текст — gateway переопределит
"""

import argparse
import json
import logging
import os
import re
import sys
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.request import Request, urlopen
from urllib.error import URLError

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger("model-gateway")

DEEPSEEK_API_KEY = os.environ.get("DEEPSEEK_API_KEY") or os.environ.get("OPENAI_API_KEY", "")
DEEPSEEK_BASE = os.environ.get("DEEPSEEK_BASE_URL", "https://api.deepseek.com/v1")

# --- Логика роутинга ---

HARD_PATTERNS = re.compile(
    r"(анализ|оптимизируй|оптимизация|рефакторинг|архитектур"
    r"|сравни|сравнение|разбери|разбор|explain|refactor"
    r"|стратеги|расслед|рассужд"
    r"|почему|зачем|как.*работ|debug|отлад"
    r"|security|безопасн|уязвим|vulnerab"
    r"|напиши.*код|code.*review"
    r"|дизайн.*систем|архитектура|trade.?off"
    r")",
    re.I,
)

EASY_WORDS = {
    "привет", "пока", "да", "нет", "ок", "окей", "ок",
    "спасибо", "thanks", "thx", "хорошо", "норм",
    "как дела", "как ты", "что делаешь", "статус",
    "давай", "понял", "ясно", "ага", "принял", "добро",
}


def route_model(messages) -> str:
    """Выбор deepseek-chat или deepseek-reasoner по последнему user-сообщению."""
    # Ищем последнее сообщение от user
    text = ""
    for msg in reversed(messages):
        if msg.get("role") == "user":
            text = msg.get("content", "")
            if isinstance(text, list):
                text = " ".join(p.get("text", "") for p in text if p.get("type") == "text")
            break

    if not text:
        return "deepseek-chat"

    text_lower = text.lower().strip()

    # Короткие сообщения (< 3 слов, < 15 символов) — почти всегда чат
    # Но если короткое сообщение содержит сложное ключевое слово — всё равно reasoner
    if len(text.split()) < 3 and len(text) < 15:
        if not HARD_PATTERNS.search(text):
            return "deepseek-chat"

    # Известные простые фразы — только целые слова
    words = set(re.sub(r"[^\w\s]", "", text_lower).split())
    for phrase in EASY_WORDS:
        if phrase in words:
            return "deepseek-chat"

    if HARD_PATTERNS.search(text):
        return "deepseek-reasoner"

    if (text_lower.endswith("?") or text_lower.endswith("?")):
        return "deepseek-reasoner" if len(text) > 80 else "deepseek-chat"

    if len(text) > 200:
        return "deepseek-reasoner"

    return "deepseek-chat"


# --- HTTP Gateway ---

class RouterHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        if "/chat/completions" not in self.path:
            self._json({"error": "not found"}, 404)
            return

        try:
            length = int(self.headers.get("Content-Length", 0))
            body = json.loads(self.rfile.read(length)) if length else {}
        except Exception as e:
            self._json({"error": f"bad request: {e}"}, 400)
            return

        # Роутинг модели
        messages = body.get("messages", [])
        model = route_model(messages)
        log.info("→ %s | %s...%s", model, messages[-1].get("content", "")[:60] if messages else "")

        # Подменяем модель в запросе
        body["model"] = model

        # Проксируем на DeepSeek
        upstream = f"{DEEPSEEK_BASE}/chat/completions"
        headers = {
            "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
            "Content-Type": "application/json",
        }
        req = Request(upstream, data=json.dumps(body).encode(), headers=headers, method="POST")
        try:
            resp = urlopen(req, timeout=120)
            data = json.loads(resp.read())
            self._json(data, resp.status)
            model_used = data.get("model", "?")
            usage = data.get("usage", {})
            log.info("← %s | in=%s out=%s", model_used, usage.get("prompt_tokens"), usage.get("completion_tokens"))
        except URLError as e:
            log.error("Upstream error: %s", e)
            self._json({"error": str(e)}, 502)

    def _json(self, data, status=200):
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

    def log_message(self, *a):
        pass  # тихо, наш логгер уже пишет

    do_PUT = do_POST


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=18889)
    args = parser.parse_args()

    if not DEEPSEEK_API_KEY:
        log.fatal("DEEPSEEK_API_KEY не задан!")
        sys.exit(1)

    log.info("⚡ Model Gateway на порту %d", args.port)
    log.info("   ⚡ deepseek-chat   — простые вопросы")
    log.info("   ⚡ deepseek-reasoner — сложные вопросы")
    log.info("   upstream: %s", DEEPSEEK_BASE)
    log.info("   В config.yaml агента:")
    log.info("     provider: openai")
    log.info("     base_url: http://localhost:%d/v1", args.port)

    HTTPServer(("0.0.0.0", args.port), RouterHandler).serve_forever()


if __name__ == "__main__":
    main()
