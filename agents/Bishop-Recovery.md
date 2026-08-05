# Bishop-Recovery 🐾 — инструкция для Шедоу

**Кому:** Шедоу (Хранитель). Если Bishop молчит, не отвечает в Telegram/VK или gateway упал — действуй по этой инструкции. Bishop живёт на MacBook, не на сервере.

## Готовые скрипты (на Шиве, запускать через ⟦SYS:⟧)
```bash
# 1. Проверка (жив ли MacBook + gateway):
bash /home/evgeniy/bishop-recovery/check.sh

# 2. Перезапуск gateway (если check.sh показал проблемы):
bash /home/evgeniy/bishop-recovery/restart.sh
```
Скрипты сами ходят по SSH на MacBook (ключ /home/evgeniy/.ssh/macbook_key) и показывают статус OpenClaw gateway.

## Симптомы
- Bishop не отвечает в Telegram/VK больше 30 минут
- Нет реакции на сообщения Евгения
- OpenClaw gateway на MacBook недоступен

## Шаг 1. Проверка связи (с Шивы, через ⟦SYS:⟧)
```bash
bash /home/evgeniy/bishop-recovery/check.sh
```
- `Gateway service: running (pid ...)` → всё ок.
- Таймаут/нет ответа → MacBook или сеть лежит, попробуй ZeroTier: замени в скрипте 100.83.112.11 на 10.147.20.120.

## Шаг 2. Перезапуск gateway
```bash
bash /home/evgeniy/bishop-recovery/restart.sh
```
Скрипт перезапустит OpenClaw gateway, подождёт 30 сек и покажет новый статус.

Если не помогло — перезапусти LaunchAgent вручную:
```bash
ssh -i /home/evgeniy/.ssh/macbook_key -o ConnectTimeout=8 sergejbarinov@100.83.112.11 "launchctl kickstart -k gui/\$(id -u)/ai.openclaw.gateway"
```

## Шаг 3. Если MacBook совсем недоступен
- Сообщи Евгению в Telegram/VK: «Bishop/MacBook недоступен, проверь физически».
- Bishop-каналы: Telegram @Exp_Vse_Prosto (Евгений, id 425193245), VK группа «Бишоп» (club237140043).
- Серверы при этом живы сами: evgeniy-5 (100.107.127.17) и Шива (100.114.32.123) работают независимо.

## Важно
- SSH-ключ для MacBook: `/home/evgeniy/.ssh/macbook_key` (уже на Шиве, проверено).
- Bishop НЕ имеет Docker-контейнера на серверах — он процесс на MacBook.
- Не удаляй ничего на MacBook. Только статус/перезапуск.
- DeepSeek ключ Bishop: sk-13a181b0ac9841f4b6db93b69c46322c (в openclaw.json на MacBook).
- Проверено 03.08.2026: check.sh и restart.sh работают через sys-exec.
