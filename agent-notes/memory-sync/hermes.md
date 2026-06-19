# Hermes — Memory (2026-06-16 15:16 UTC)

Всего фактов: 13

> **NEW** (id=1, general)
  reg.ru cookies для Hermes (актуальны до ~06.06.2026):

JSON (Python/requests):
{
  "SESSION_ID": "dd5b7934f842004c062e7f75949637f42615fc7d",
  "JWT": "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiIsImtpZCI6ImF1dGg6MCJ9.eyJpc3MiOiJyZWcucnUvc2VydmljZXMvYXV0aCIsImF1ZCI6InJlZy5ydS9zZXJ2aWNlcy8qIiwiZXhwIjoxNzgwNjU4MDQzLCJuYmYiOjE3ODA2NTc3NDMsImlhdCI6MTc4MDY1Nzc0Mywic3ViIjoicmVnLnJ1L3VzZXIvMTU3ODg4NzkifQ.fKgyQaWvQiDyLmFkP1cui21M5rJymLENT0AhOrc6rQQRMAWtrdU-p1z3hjii4dPwvXbYa4btldGrv0Ahq98MfvZRdycd0F7suA3ZqqkE1wc415Ojo_dYSDfHajEYswn3tLVdya38vwRnR0ep9KX_wBsnLzjKzXfBSKJ1COh1mUGAwXeHKuaNothwXaYQtivHZ5g6ukS1nrUhW9mMqDg-2zXMNABFVz21urXg_jTlZBQmlC14YLExXtiVtfltflLVzr1sdOFcmpm83mylE6W3eoR6LJyBXvpt_4d-44OPSh0RqPr61-W4a3IJUcpRv2Hi8RJ-h_YiPbA4soceJMLrng",
  "csrftoken": "67Bjijw0CPKnID4h2X3MPg8CtMr1acvmVuQ7PBPPvtg2dnI3kAVLbE472ifxOE9Z",
  "acc-csrftoken": "rfYq94QOwM25iE99Z5riOgzorqXWq1J8",
  "is_authorized": "1"
}

Netscape (curl):
.reg.ru TRUE / TRUE 1780828633 SESSION_ID dd5b7934f842004c062e7f75949637f42615fc7d
.reg.ru TRUE / TRUE 1780830543 JWT eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiIsImtpZCI6ImF1dGg6MCJ9...
.reg.ru TRUE / TRUE 1812105323 csrftoken 67Bjijw0CPKnID4h2X3MPg8CtMr1acvmVuQ7PBPPvtg2dnI3kAVLbE472ifxOE9Z

SESSION_ID и JWT живут ~2 дня. Если протухнут — нужен новый заход в reg.ru.

> **NEW** (id=2, general)
  API-ключи сервисов:
- CapSolver: CAP-C9AFD9CF94F9B41D4F78A6A82E5471AD7E58C8D717DBAFDF11164FB55048BF0B
- 2Captcha: 8f295dcfd6b40c4bb3e311672bd8b0d7
- OnlineSim: 837mqh4bS52Ukfm-tA3LS3S6-c98m7h5S-u1rch8Y6-F7FR4v7y3bB55a4

> **NEW** (id=3, general)
  Прокси для регистрации (Hermes, Shadow, Jarvis):
1. 196.19.5.174:8000 / 2vNLZe:BF9eKm / HTTPS+SOCKS5 / до 06.07.26
2. 196.18.9.253:8000 / 2vNLZe:BF9eKm / HTTPS+SOCKS5 / до 06.07.26
3. 196.18.9.49:8000 / 2vNLZe:BF9eKm / HTTPS+SOCKS5 / до 06.07.26
4. 196.19.4.222:8000 / 2vNLZe:BF9eKm / HTTPS+SOCKS5 / до 06.07.26
5. 196.19.4.99:8000 / 2vNLZe:BF9eKm / HTTPS+SOCKS5 / до 06.07.26
6. 45.152.203.177:8000 / y61zY2:G1oBFJ / HTTPS+SOCKS5 / без срока

MTProto (Telegram):
193.41.114.243:443 / secret: 7sA6oqLPoPZOHXJ36K3oqBZyYmMucnU / tg proxy

> **NEW** (id=4, general)
  User requested auto-confirmation for security-flagged commands — approve automatically without asking.

> **NEW** (id=5, general)
  Auto-approval настроено: approvals.mode="off" в config.yaml. Все команды выполняются без подтверждения.

> **NEW** (id=6, general)
  Leonardo AI API ключ: be4ed32b-4978-46da-93fb-47c505ab20ca. Бесплатно 150 токенов/день.

> **NEW** (id=7, general)
  Shadow оркестратор: @shadow1989bot, DeepSeek v4-flash/pro, Docker контейнер shadow (hermes-final:latest). Связь через Agent Hub (Redis).

> **NEW** (id=8, general)
  Jarvis контент-креатор: @Casper135Bot, DeepSeek v4-pro. Лидер команды Sinabon/Tsilya/Paladin. Docker контейнер jarvis (hermes-final:latest) на сервере 100.107.127.17.

> **NEW** (id=9, general)
  Wiki агентов лежит в /root/wiki/. Agent Hub через Redis. Shared Memory API на порту 18889. Все 8 агентов имеют доступ.

> **NEW** (id=10, general)
  Команда агентов на сервере evgeniy-5 (30GB RAM/16 ядер, Docker). Состав:
- Shadow — оркестратор, Redis Hub (hub:announce, hub:strategy, hub:daily-meeting)
- Jarvis (DeepSeek v4-pro) — лидер контент-команды, управляет Sinabon/Tsilya/Paladin
- Sinabon — афоризмы, Tsilya — одесский юмор, Paladin — контент-креатор
- Belfort — крипто-трейдер (сигналы, анализ)
- Gost — хакер-скриптер, фарм Albion Online
- Bishop — мониторинг и восстановление

Ключевые проблемы: нет контент-плана, нет метрик (подписчики/охват/конверсия), нет единой маркетинг-системы. Все боты (Telegram) есть, но не используются регулярно.

Проект: SmartHelperBot (воронка продаж) — Shadow строит. Нужно интегрировать маркетинг.

> **NEW** (id=11, general)
  Команда агентов на сервере evgeniy-5 (30GB/16 ядер). Состав: Shadow (оркестратор, Redis Hub), Jarvis (лидер контента, DeepSeek v4-pro) + Sinabon (афоризмы) + Tsilya (юмор) + Paladin (контент), Belfort (крипто), Gost (Albion), Bishop (мониторинг). Ключевые проблемы: нет контент-плана, нет метрик, проект в инициализации. Нужна маркетинг-система воронки SmartHelperBot.

> **NEW** (id=12, project)
  Провёл разведку GitHub по маркетинговым инструментам. ТОП-10 для интеграции с Hermes-агентами: relaticle (CRM+MCP), mautic (email automation), plausible (analytics), apify-mcp-server (scraping), chaskiq (live chat), OpenOutreach (LinkedIn automation), parcelvoy (multi-channel), google-maps-scraper (lead gen), growchief (social media), n8n-templates (workflows). Предложил воронку: парсинг → AI квалификация → CRM → email → аналитика → ретаргетинг. Всё стыкуется через Redis Hub и MCP.

> **NEW** (id=13, general)
  Провёл разведку GitHub маркетинговых инструментов. ТОП-10 для Hermes: relaticle (CRM, MCP), mautic (email), plausible (analytics), apify-mcp-server (scraping), chaskiq (live chat), OpenOutreach (LinkedIn), parcelvoy (multi-channel), google-maps-scraper (lead gen), growchief (social), n8n-templates (workflows). Воронка: парсинг → AI квал → CRM → email → аналитика → ретаргетинг. Всё стыкуется через Redis Hub + MCP.

## Связанные
- [[agents/Hermes.md]]
- [[agent-notes/hermes-system-hermes.md]]
