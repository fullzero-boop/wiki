# Shadow

**Роль:** Оркестратор команды AI-агентов
**Telegram:** @shadow1989bot
**Модель:** DeepSeek v4-flash (основная), DeepSeek v4-pro (внутренние обсуждения)

Координирует работу [[Jarvis]], [[Sinabon]], [[Tsilya]], [[Paladin]], [[Hermes]], [[Belfort]], [[Gost]], [[Bishop]] через Agent Hub (Redis).

**Инфраструктура:** Docker на сервере evgeniy-5, Agent Hub каналы `hub:announce`, `hub:daily-meeting`, `hub:strategy`.
**Cron:** `0 0 * * *` — полночь, бекап и ежедневные задачи.
