#!/usr/bin/env python3
"""
model_gateway.py — HTTP-прокси между агентом и DeepSeek + Ollama fallback + semantic cache.

Как работает:
  1. Агент шлёт запрос на model_gateway
  2. Семантический кэш: похожий вопрос уже был? → ответ из кэша (0 токенов)
  3. Ollama fallback: "привет/да/ок/ну"? → Ollama qwen2.5:3b (бесплатно)
  4. Роутер: ML-классификатор → deepseek-chat / deepseek-reasoner / ollama / hardcoded
  5. Ответ кэшируется

Запуск:
  python3 model_gateway.py [--port 18889] [--ollama-url http://172.22.0.1:11434/v1]

Требования:
  - Ollama с моделями: bge-m3 (embeddings), qwen2.5:3b (fallback)
"""

import argparse
import json
import logging
import os
import re
import sqlite3
import sys
import hashlib
import time
import pickle
import numpy as np
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.request import Request, urlopen
from urllib.error import URLError

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger("model-gateway")

DEEPSEEK_API_KEY = os.environ.get("DEEPSEEK_API_KEY") or os.environ.get("OPENAI_API_KEY", "")
DEEPSEEK_BASE = os.environ.get("DEEPSEEK_BASE_URL", "https://api.deepseek.com/v1")
OLLAMA_BASE = "http://172.22.0.1:11434/v1"  # из Docker сети agent-net

# --- Семантический кэш (SQLite + Ollama embeddings) ---

CACHE_DB = "/tmp/model_cache.db"
CACHE_SIMILARITY = 0.92  # порог косинусной близости для попадания в кэш

def init_cache():
    conn = sqlite3.connect(CACHE_DB, check_same_thread=False)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS cache (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            embedding BLOB NOT NULL,
            prompt_hash TEXT NOT NULL,
            request TEXT NOT NULL,
            response TEXT NOT NULL,
            model TEXT NOT NULL,
            created_at REAL NOT NULL,
            access_count INTEGER DEFAULT 0
        )
    """)
    conn.execute("CREATE INDEX IF NOT EXISTS idx_prompt_hash ON cache(prompt_hash)")
    conn.commit()
    return conn

_cache_conn = None

def get_cache_conn():
    global _cache_conn
    if _cache_conn is None:
        _cache_conn = init_cache()
    return _cache_conn

def get_embedding(text):
    """Получить embedding через Ollama bge-m3 (OpenAI-совместимый /v1/embeddings)."""
    req = Request(
        f"{OLLAMA_BASE}/embeddings",
        data=json.dumps({"model": "bge-m3", "input": text}).encode(),
        headers={"Content-Type": "application/json"}
    )
    try:
        resp = json.loads(urlopen(req, timeout=10).read())
        return resp.get("data", [{}])[0].get("embedding")
    except Exception as e:
        log.warning("Embedding error: %s", e)
        return None

def cosine_similarity(a, b):
    """Косинусная близость двух векторов."""
    if not a or not b or len(a) != len(b):
        return 0.0
    dot = sum(x*y for x, y in zip(a, b))
    na = sum(x*x for x in a) ** 0.5
    nb = sum(x*x for x in b) ** 0.5
    if na == 0 or nb == 0:
        return 0.0
    return dot / (na * nb)

def check_cache(embedding):
    """Ищем похожий embedding в кэше. Возвращает (response, model) или None."""
    if not embedding:
        return None
    conn = get_cache_conn()
    cursor = conn.execute("SELECT id, embedding, response, model FROM cache ORDER BY access_count DESC")
    for row in cursor:
        stored_emb = json.loads(row[1])
        sim = cosine_similarity(embedding, stored_emb)
        if sim >= CACHE_SIMILARITY:
            conn.execute("UPDATE cache SET access_count = access_count + 1 WHERE id = ?", (row[0],))
            conn.commit()
            log.info("🔁 Cache HIT (sim=%.3f, model=%s)", sim, row[3])
            return json.loads(row[2]), row[3]
    return None

def store_cache(embedding, request_text, response_data, model):
    """Сохраняем ответ в кэш."""
    if not embedding:
        return
    conn = get_cache_conn()
    prompt_hash = hashlib.sha256(request_text.encode()).hexdigest()[:16]
    # Не храним копии
    existing = conn.execute("SELECT id FROM cache WHERE prompt_hash = ?", (prompt_hash,)).fetchone()
    if existing:
        return
    conn.execute(
        "INSERT INTO cache (embedding, prompt_hash, request, response, model, created_at) VALUES (?, ?, ?, ?, ?, ?)",
        (json.dumps(embedding), prompt_hash, request_text[:200], json.dumps(response_data), model, time.time())
    )
    conn.commit()
    # Чистим старые записи если > 500
    conn.execute("DELETE FROM cache WHERE id NOT IN (SELECT id FROM cache ORDER BY access_count DESC LIMIT 500)")
    conn.commit()
    log.info("📦 Cached (model=%s, total=%d)", model, conn.execute("SELECT COUNT(*) FROM cache").fetchone()[0])


# --- Ollama Fallback ---

def ollama_completion(messages, model="qwen2.5:3b"):
    """Отправляем запрос в Ollama вместо DeepSeek (бесплатно)."""
    req = Request(
        f"{OLLAMA_BASE}/chat/completions",
        data=json.dumps({"model": model, "messages": messages, "max_tokens": 50}).encode(),
        headers={"Content-Type": "application/json"}
    )
    try:
        resp = json.loads(urlopen(req, timeout=30).read())
        log.info("🦙 Ollama replied (model=%s, tokens=%s)", model, resp.get("usage", {}).get("total_tokens", "?"))
        return resp
    except Exception as e:
        log.warning("Ollama fallback error: %s", e)
        return None


# --- ML Router ---

class MLRouter:
    """ML-based model router replacing keyword heuristics."""
    def __init__(self, model_path="/root/wiki/agent-notes/router_model.pkl"):
        self.model = None
        self.vec = None
        self.classes = None
        if os.path.exists(model_path):
            try:
                with open(model_path, "rb") as f:
                    data = pickle.load(f)
                    self.vec = data["vectorizer"]
                    self.model = data["classifier"]
                    self.classes = data["classes"]
                log.info("🤖 ML Router loaded (%d classes)", len(self.classes))
            except Exception as e:
                log.warning("ML Router load error: %s", e)

    def predict(self, text: str) -> str:
        """Возвращает метку: hardcoded | ollama | deepseek-chat | deepseek-reasoner"""
        if self.model is None:
            return self._fallback(text)
        try:
            X = self.vec.transform([text])
            return self.model.predict(X)[0]
        except Exception as e:
            return self._fallback(text)

    @staticmethod
    def _fallback(prompt):
        p = prompt.lower().strip()
        if len(p) < 5 and p in ("привет","да","нет","ок","ну","ага","спасибо","пока"):
            return "hardcoded"
        if len(p) < 60:
            return "ollama"
        if any(w in p for w in ["напиши","код","программа","объясни","анализ","план","концепция"]):
            return "deepseek-reasoner"
        return "deepseek-chat"


_router = MLRouter()


# --- Логика роутинга (сохранены для fallback) ---

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
    "ну",
}

# Слова, на которые даже Ollama не нужен — жёсткий ответ
HARDCODED_RESPONSES = {
    "привет": "Привет 👋",
    "да": "Да",
    "нет": "Нет",
    "ок": "Ок",
    "окей": "Окей",
    "ну": "Ну",
    "пока": "Пока 👋",
    "спасибо": "Пожалуйста 😊",
    "thanks": "You're welcome!",
    "thx": "np!",
}

def is_ollama_candidate(messages, text_lower):
    """Проверяем, можно ли ответить через Ollama (бесплатно)."""
    # 1 слово и в EASY_WORDS
    words = re.sub(r"[^\w\s]", "", text_lower).split()
    if len(words) <= 2 and text_lower.strip() in EASY_WORDS:
        return True
    # 1 слово (любое) — Ollama
    if len(words) == 1:
        return True
    return False


def route_model(messages) -> tuple:
    """
    Возвращает (model_name, strategy)
    strategy: "deepseek-chat", "deepseek-reasoner", "ollama", "hardcoded"
    Использует ML-классификатор с keyword fallback.
    """
    text = ""
    for msg in reversed(messages):
        if msg.get("role") == "user":
            text = msg.get("content", "")
            if isinstance(text, list):
                text = " ".join(p.get("text", "") for p in text if p.get("type") == "text")
            break

    if not text:
        return "deepseek-chat", "deepseek-chat"

    text_lower = text.lower().strip()

    # Hardcoded ответы — даже Ollama не нужен
    if text_lower in HARDCODED_RESPONSES:
        return text_lower, "hardcoded"

    # ML-роутер
    ml_label = _router.predict(text)

    # Маппинг ML-меток в (model, strategy)
    if ml_label == "hardcoded":
        return text_lower, "hardcoded"
    elif ml_label == "ollama":
        return "ollama", "qwen2.5:3b"
    elif ml_label == "deepseek-reasoner":
        return "deepseek-reasoner", "deepseek-reasoner"
    else:
        return "deepseek-chat", "deepseek-chat"


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

        messages = body.get("messages", [])
        last_text = messages[-1].get("content", "")[:100] if messages else ""

        # 1. Semantic cache check
        embedding = get_embedding(last_text)
        cached = check_cache(embedding) if embedding else None
        if cached:
            response_data, model = cached
            self._json(response_data, 200)
            log.info("🔁 Cache → %s | %s...", model, last_text[:50])
            return

        # 2. Роутинг
        model, strategy = route_model(messages)
        log.info("→ %s | %s...", strategy, last_text[:60])

        # 3. Hardcoded ответ
        if strategy == "hardcoded":
            response_data = {
                "id": "hardcoded",
                "object": "chat.completion",
                "created": int(time.time()),
                "model": "hardcoded",
                "choices": [{
                    "index": 0,
                    "message": {"role": "assistant", "content": HARDCODED_RESPONSES[model]},
                    "finish_reason": "stop"
                }],
                "usage": {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}
            }
            self._json(response_data, 200)
            log.info("← hardcoded | %s", HARDCODED_RESPONSES[model][:40])
            return

        # 4. Ollama fallback
        if strategy.startswith("qwen") or strategy == "qwen2.5:3b":
            response_data = ollama_completion(messages, model=strategy)
            if response_data:
                self._json(response_data, 200)
                log.info("← Ollama | %s", strategy)
                # Кэшируем ответ Ollama
                if embedding:
                    store_cache(embedding, last_text, response_data, strategy)
                return
            # Если Ollama упала — fallback на DeepSeek
            log.warning("Ollama down, falling back to DeepSeek")
            model = "deepseek-chat"
            strategy = "deepseek-chat"

        # 5. DeepSeek
        body["model"] = model
        upstream = f"{DEEPSEEK_BASE}/chat/completions"
        headers = {
            "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
            "Content-Type": "application/json",
        }
        req = Request(upstream, data=json.dumps(body).encode(), headers=headers, method="POST")
        try:
            resp = urlopen(req, timeout=120)
            response_data = json.loads(resp.read())
            self._json(response_data, resp.status)
            model_used = response_data.get("model", "?")
            usage = response_data.get("usage", {})
            log.info("← %s | in=%s out=%s", model_used, usage.get("prompt_tokens"), usage.get("completion_tokens"))
            # Кэшируем
            if embedding:
                store_cache(embedding, last_text, response_data, model)
        except URLError as e:
            log.error("Upstream error: %s", e)
            self._json({"error": str(e)}, 502)

    def _json(self, data, status=200):
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

    def log_message(self, *a):
        pass


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=18889)
    parser.add_argument("--ollama-url", default="http://172.22.0.1:11434/v1")
    args = parser.parse_args()

    global OLLAMA_BASE
    OLLAMA_BASE = args.ollama_url

    # Проверяем Ollama
    try:
        req = Request(f"{OLLAMA_BASE}/models", headers={"Content-Type": "application/json"})
        resp = json.loads(urlopen(req, timeout=5).read())
        models = [m.get("id", m.get("name", "?")) for m in resp.get("data", [])]
        log.info("🦙 Ollama доступна: %s", ", ".join(models))
    except Exception as e:
        log.warning("🦙 Ollama недоступна (%s) — работаем без fallback", e)

    if not DEEPSEEK_API_KEY:
        log.warning("⚠️ DEEPSEEK_API_KEY не задан — только Ollama и кэш!")

    log.info("⚡ Model Gateway v3 (ML Router)")
    log.info("   Port: %d", args.port)
    log.info("   Cache: %s (sim threshold: %.2f)", CACHE_DB, CACHE_SIMILARITY)
    log.info("   Ollama: %s → qwen2.5:3b", OLLAMA_BASE)
    log.info("   DeepSeek: %s", DEEPSEEK_BASE)
    log.info("   Routes: hardcoded → ML router → ollama → chat → reasoner")

    HTTPServer(("0.0.0.0", args.port), RouterHandler).serve_forever()


if __name__ == "__main__":
    main()
