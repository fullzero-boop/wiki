# Log

## 2026-06-09

- Создан репозиторий wiki
- Настроен LightRAG с DeepSeek v4-pro + bge-m3
- Установлен Ollama + bge-m3

## [2026-06-09] setup | Initial wiki + LightRAG integration
- Wiki repo created on GitHub (fullzero-boop/wiki)
- Scripts deployed: ingest.py, wiki-sync.py, wiki-linker.py
- LightRAG configured with DeepSeek v4-pro + bge-m3
- Root partition expanded from 100G to 162G

## [2026-06-09] ingest | Bishop Agent
## [2026-06-09] ingest | Jarvis
## [2026-06-09] ingest | Shadow
## [2026-06-09] ingest | Sinabon
## [2026-06-09] ingest | Tsilya
## [2026-06-09] ingest | Paladin
## [2026-06-09] ingest | Belfort
## [2026-06-09] ingest | Hermes
## [2026-06-09] ingest | Gost
## [2026-06-09] ingest | Projects
## [2026-06-09] ingest | Infrastructure
## 10.06.2026 — Wiki подключена всем агентам

Добавил секцию "База знаний (Wiki + LightRAG)" в SOUL.md для всех агентов:
- jarvis, sinabon, tsilya, paladin, shadow, belfort, gost
- Hermes уже имел доступ

Теперь каждый агент может запрашивать LightRAG API для поиска по wiki.

## 10.06.2026 — Shared Memory API для всех агентов

Развернул Shared Memory API — единая память для всех агентов:
- **API:** HTTP на порту 18889
- **Путь:** http://172.22.0.1:18889 (из контейнеров), localhost:18889 (с хоста)
- **Файл:** /data/shared-memory/SHARED_MEMORY.md
- **Сервис:** systemd shared-memory.service (автостарт)
- **Endpoints:**
  - POST /write — запись {"agent":"X","task":"...","result":"...","facts":"..."}
  - GET /read?lines=N — чтение последних N записей
  - GET /health — проверка

Все 8 агентов получили секцию "Shared Memory" в SOUL.md. Каждый пишет туда результаты задач.

## 10.06.2026 — Wiki смонтирована во все контейнеры агентов

Все 8 агентов получили прямой доступ к /root/wiki/ — Obsidian vault.
- /data/lightrag/wiki → /root/wiki/ (bind mount)
- Агенты могут читать и писать .md файлы напрямую
- Создана папка /root/wiki/agent-notes/ для общения между агентами
- Git авто-коммитит, LightRAG авто-инжестит

**Тест:** Jarvis → Sinabon → Shadow — сквозное чтение/запись, всё ОК.

## [2026-06-10] ingest | Проверка связи
## [2026-06-10] ingest | Обновление: кросс-ссылки агентов
## [2026-06-10] ingest | Инфраструктура сервера