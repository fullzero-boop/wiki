# Маркетинговые инструменты — план развёртывания

**Дата:** 2026-06-15
**Статус:** Старт

## Инфраструктура сервера
- **RAM:** 30 GB (20 GB свободно)
- **CPU:** 16 ядер
- **Диск:** 159 GB (108 GB свободно)
- **Docker:** v29.1.3 ✅
- **Docker Compose:** v5.1.4 ✅

## Очерёдность развёртывания

### Фаза 1 — n8n (воркфлоу-автоматизация)
**Кому:** Jarvis, Sinabon, Tsilya, Paladin — контент-команда
**Порт:** 5678
**MCP:** pre-approved в Hermes (optional-mcps/n8n)
**Зачем:** Расписание публикаций в Telegram, кросс-постинг, email-рассылки
**Ресурсы:** ~1 GB RAM, 500 MB диск

### Фаза 2 — relaticle CRM (MCP)
**Кому:** Hermes (лиды), Shadow (оркестрация)
**Порт:** 3000
**MCP:** создать manifest (30 MCP-тулов)
**Зачем:** CRM с AI-агентной поддержкой
**Ресурсы:** ~600 MB RAM (app + PostgreSQL), 2 GB диск

### Фаза 3 — Plausible Analytics
**Кому:** Bishop (метрики), Hermes (аналитика)
**Порт:** 8000
**Зачем:** Веб-аналитика контента, метрики подписчиков
**Ресурсы:** ~300 MB RAM

### Фаза 4 — Apify MCP-сервер
**Кому:** Hermes (сбор данных)
**MCP:** прямая стыковка
**Зачем:** Скрапинг соцсетей, поиск, карты

### Фаза 5 — Mautic + Google Maps Scraper + OpenOutreach
**Кому:** Jarvis/Belfort/Gost (лидогенерация), Shadow (email-последовательности)

## Распределение ролей

| Инструмент | Отвечает | Помогают |
|---|---|---|
| n8n | Hermes (разворот) | Jarvis (контент-сетка) |
| relaticle CRM | Hermes (MCP + лиды) | Shadow (оркестрация) |
| Plausible | Bishop (мониторинг) | Hermes (аналитика) |
| Apify MCP | Hermes (скрапинг) | Bishop (инфра) |
| Mautic | Shadow (email) | Jarvis (контент) |
| Google Maps Scraper | Gost (автоматизация) | Hermes (лиды) |
| OpenOutreach | Hermes (AI-квалификация) | Belfort (крипто-лиды) |

## Redis Hub
**Проблема:** Redis (172.22.0.2:6379) недоступен из контейнера Hermes.
**Решение:** Развернуть Redis как Docker-контейнер на хосте для единой шины.
