#!/usr/bin/env python3
"""
Model Router — автономный выбор: deepseek-chat vs deepseek-reasoner.

Использование:
  python3 model_router.py <текст сообщения пользователя>
  -> выводит "deepseek-reasoner" или "deepseek-chat"

Логика:
  - Короткие/простые сообщения → чат (дёшево)
  - Сложные запросы (анализ, рефакторинг, код, стратегия) → разумница
  - Русский/английский — без разницы, работаем по ключевым словам
"""

import re
import sys


# Вопросы/задачи, требующие deepseek-reasoner
HARD_PATTERNS = re.compile(
    r"(анализ|оптимизируй|оптимизация|рефакторинг|архитектур"
    r"|сравни|сравнение|разбери|разбор|explain|refactor"
    r"|стратеги|план|расслед|рассужд"
    r"|почему|зачем|как.*работает|debug|отлад"
    r"|security|безопасн|уязвим|vulnerab"
    r"|напиши.*код|code.*review|рецензи"
    r"|дизайн.*систем|архитектура|trade.?off"
    r")",
    re.I,
)

# 100% простые фразы — сразу чат
EASY_WORDS = {
    "привет", "пока", "да", "нет", "ок", "окей", "ок",
    "спасибо", "thanks", "thx", "хорошо", "норм",
    "как дела", "как ты", "что делаешь", "статус",
    "давай", "понял", "ясно", "ага",
    "принял", "добро",
}


def select_model(text: str) -> str:
    if not text:
        return "deepseek-chat"

    text_lower = text.lower().strip()

    # Короткие сообщения — почти всегда чат
    if len(text) < 15:
        return "deepseek-chat"

    # Известные простые фразы — только как целые слова
    words = set(re.sub(r"[^\w\s]", "", text_lower).split())
    for phrase in EASY_WORDS:
        if phrase in words:
            return "deepseek-chat"

    # Содержит сложные ключи → reasoner
    if HARD_PATTERNS.search(text):
        return "deepseek-reasoner"

    # Вопросы (заканчиваются на ?) длиннее 80 символов → может быть сложным
    if text_lower.endswith("?") or text_lower.endswith("?"):
        if len(text) > 80:
            return "deepseek-reasoner"
        return "deepseek-chat"

    # Команды/просьбы с глаголами → смотрим длину
    if any(text_lower.startswith(v) for v in ("сделай", "напиши", "скажи", "дай", "покажи")):
        if len(text) > 100:
            return "deepseek-reasoner"
        return "deepseek-chat"

    # Длинные сообщения (>200 символов) — скорее всего что-то содержательное
    if len(text) > 200:
        return "deepseek-reasoner"

    return "deepseek-chat"


if __name__ == "__main__":
    text = sys.argv[1] if len(sys.argv) > 1 else sys.stdin.read().strip()
    print(select_model(text))
