# Маркетинговый отчёт — Рынок + Конкуренты

## Состояние на 2026-06-15
Проведён глобальный обзор GitHub по маркетинговым инструментам:
- **175 репозиториев** просканировано
- **10 отобрано** для интеграции с Hermes
- **Файл с данными:** /root/curated_marketing_repos.json

## ТОП-10 инструментов для команды

1. **relaticle/relaticle** (1346⭐) — CRM с MCP, 30 AI-тулов. **Прямая стыковка с Hermes**
2. **mautic/mautic** (9828⭐) — Email-автоматизация, Docker + REST API
3. **plausible/analytics** (27148⭐) — Self-hosted веб-аналитика
4. **apify/apify-mcp-server** (1342⭐) — MCP-скрапинг для AI-агентов
5. **chaskiq/chaskiq** (3529⭐) — Live chat (Intercom-аналог)
6. **eracle/OpenOutreach** (2109⭐) — LinkedIn-автоматизация + AI-лиды
7. **parcelvoy/platform** (530⭐) — Email + SMS + Push
8. **omkarcloud/google-maps-scraper** (2735⭐) — Сбор лидов с Maps
9. **growchief/growchief** (3369⭐) — Социал-автоматизация
10. **enescingoz/awesome-n8n-templates** (23011⭐) — 280+ готовых воркфлоу

## Воронка (через Redis Hub)
```
Google Maps Scraper → OpenOutreach (AI квал) → 
relaticle CRM (MCP) → Mautic (email) → 
Plausible (метрики) → Chaskiq (ретаргетинг)
```

## Статус развёртывания
- **Фаза 1 (n8n):** Стартует
- **Фаза 2 (relaticle):** В плане
- **Остальные:** По готовности

## Связанные
- [[agents/Hermes.md]]
- [[agents/Shadow.md]]
