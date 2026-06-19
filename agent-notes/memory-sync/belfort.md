# Belfort — Memory (2026-06-16 17:30 UTC)

Всего фактов: 7

- (id=1, user_pref)
  User Евгений Сергеевич — русскоязычный крипто-трейдер. Обращаться на «ты». Запросил быть его крипто-аналитиком Belfort, предоставлять сводки рынка, входы/выходы, стратегии. Предпочитает получать рыночные данные на русском языке.

- (id=2, general)
  OKX API credentials for Belfort (user: Евгений Сергеевич):
- API Key: 71055e51-9e05-41fd-9b3c-38b6b133642e
- Secret Key: A40EFA4295F34AD400C77AEE5F06DEB9
- Passphrase: (not provided yet — user said "Сохрани себе" but didn't send passphrase, need to ask)
- Whitelisted IPs: 213.226.113.153, 155.212.224.160
- Rights: Read + Trade + Withdraw

- (id=3, general)
  OKX API ключи от пользователя:
- API Key: 71055e51-9e05-41fd-9b3c-38b6b133642e
- Secret Key: A40EFA4295F34AD400C77AEE5F06DEB9
- Passphrase: Bbatkavi4@ (из belfort_monitor.py)
- Права: Read+T+W
- IPs: 213.226.113.153, 155.212.224.160
НО! API Key из монитора (bf49b5de...) не работает — ошибка 50119. Возможно демо-ключ. Нужно использовать продакшн-ключ 71055e51...

- (id=4, user_pref)
  Belfort: всё делаю сам. Без алертов Bishop. Никаких уведомлений другим агентам. Пишу результаты только в этот Telegram-чат (пользователь). Не пишу в shared memory без необходимости.

- (id=5, general)
  Freqtrade переключен на BelfortRegimeStrategy (адаптация RegimeFilterStrategy под OKX SOL/USDT спот). TF 1h, SL 4%, TP 10%, трейлинг включён. Запущен Grid Bot (10 уровней, buy $59-71, sell $77-89). Health Monitor v6 следит за обоими. 2 SOL проданы для USDT баланса ($159.73 USDT). Капитал ~$1,200.

- (id=6, general)
  HTX (Huobi) API ключи от пользователя:
- Access Key: 84080006-dbuqg6hkte-7fa506de-80da3
- Secret Key: 2440e12b-6ccae191-e7ea4cef-a1d23
- IP: 213.226.113.153
- Права: Read + Trade + Withdraw

> **NEW** (id=7, general)
  OKX API Passphrase for Belfort: Bbatkavi4@ по конфигу /root/freqtrade/config.json

## Связанные
- [[agents/Belfort.md]]
- [[agent-notes/hermes-system-belfort.md]]
