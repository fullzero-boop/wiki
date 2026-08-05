# Система памяти (5 уровней)

## Уровень 1 — In-Context
- Последние 15 сообщений в памяти процесса
- Сброс по команде /clear

## Уровень 2 — LightRAG (граф знаний)
- Порт: 18888
- Модель: qwen2.5:1.5b + bge-m3
- Путь проекта: /data/lightrag/project
- Wiki: /data/lightrag/wiki/
- Эндпоинты: POST /query, POST /insert, GET /health
- Проиндексировано: 105 файлов wiki
- Запуск: systemd сервис (lightrag.service)

## Уровень 3 — Vector Memory (Memory Service)
- Порт: 8005
- Стек: FastAPI + PostgreSQL (pgvector) + Redis
- Эмбеддинги: bge-m3 через Ollama
- Неймспейсы: `shared` (общая) + `personality_<бот>` (личная)
- Таблица: `semantic_memory` с векторным поиском
- Docker: `--network host --restart unless-stopped`

## Уровень 4 — Web Search
- DuckDuckGo Lite через SOCKS5 прокси
- Срабатывает на вопросы длиннее 2 слов

## Уровень 5 — Obsidian Vault
- Путь: /data/lightrag/wiki/ (смонтирован в obsidian-box)
- Директории:
  - conversations/<bot>/ — личные дневники ботов
  - conversations/_all/ — общий лог
  - conversations/_consolidated/ — саммари self-learning
  - agents/ — профили ботов

## Entity Extraction
Каждый диалог парсится через LLM в структурированные факты:
`{"fact": "...", "entities": [...], "type": "preference|fact|action|opinion"}`

## Deduplication
Перед сохранением проверка: score > 0.92 → дубликат, пропуск.

## Self-Learning
- Cron: `0 */1 * * *` (каждый час)
- Скрипт: `/data/lightrag/wiki/self_learn.py`
- Делает:
  1. Web research — каждый бот ищет материалы по своей теме
  2. Consolidation — анализ последних диалогов
- Результат: факты с тегом `[web/<бот>]` или `[consolidated/<бот>]`
