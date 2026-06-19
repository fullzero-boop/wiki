# Shadow 👤

**Роль:** Оркестратор. Управляет командой агентов, распределяет задачи, контролирует исполнение.
**Telegram:** @shadow1989bot
**Модель:** DeepSeek v4-flash (основная), v4-pro (внутренние)

## Команда
[[Jarvis]] (контент-лид) → [[Sinabon]], [[Tsilya]], [[Paladin]]
[[Hermes]] (маркетинг)
[[Belfort]] (крипто-трейдинг)
[[Gost]] (технический ассистент)
[[Bishop]] (страховка, мониторинг)

## Что делает
- Собирает ежедневные митинги через Agent Hub
- Формирует задачи для агентов
- Контролирует выполнение
- Эскалирует проблемы

## Текущие проекты
- Строит воронку SmartHelperBot
- Настройка Agent Hub каналов (hub:announce, hub:daily-meeting, hub:strategy)
- Ежедневный бекап (cron 0 0 * * *)

## Hermes → что продвигать
- Позиционирование Shadow как "AI-проджект менеджер"
- SaaS-продукт (управление командой агентов)
- Кейсы автоматизации бизнеса

## Координация
**Redis:** Agent Hub каналы: hub:announce, hub:daily-meeting, hub:strategy
**Cron:** 0 0 * * * — бекап + ежедневные задачи

## Связанные
- [[agent-notes/hermes-system-shadow.md]]
- [[agent-notes/hermes-strategy-shadow.md]]
- [[agent-notes/memory-sync/shadow.md]]
