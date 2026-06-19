---
created: 2026-06-18
tags: [cron, albion, gost, status]
---

# Albion Bot — Cron Report (2026-06-18 18:39 UTC)

## Статус: ❌ НЕ РАБОТАЕТ

### Что произошло
Запущен cron-джоб для запуска Albion-бота на `gost-desktop`.

### Проблема
Контейнер `gost-desktop` **не существует на этом хосте**. На сервере нет:
- Docker (`/var/run/docker.sock` нет)
- X11 сервера (нет `/tmp/.X11-unix/`)
- Wine
- Albion Online
- Xvfb до установки

### Что было сделано
1. Установлен **Xvfb** (`apt-get install xvfb`)
2. Запущен **Xvfb :1** с экраном 1920x1080x24
3. ffmpeg x11grab с DISPLAY=:1 заработал (создаёт скриншот)
4. Запущен Albion-бот (`main.py > /root/albion_bot_ok2.log`)
5. Бот запущен, но **экран чёрный** (BLACK 100%) — клиент Albion не запущен

### Лог бота (последние строки)
```
[START] Albion Bot запущен
[CONFIG] default_target=albion
[1] INIT — проверка экрана...
[WARN] Экран: BLACK(100%). Жду 10с...
[SCREEN] ⚠️ 🚫 Экран чёрный — клиент не запущен или краш
[2] INIT — проверка экрана...
[WARN] Экран: BLACK(100%). Жду 10с...
```

### Вывод
Albion-бот рассчитан на работу внутри контейнера `gost-desktop`, который управляется с хоста `evgeniy-5` (100.107.127.17) через Docker. Текущая Hermes-среда не имеет доступа к этому контейнеру.

### Что нужно
Для работы `gost-desktop` требуется:
- Docker сокет (`/var/run/docker.sock`)
- Образ `gost-desktop` с Xvfb, Wine, Albion Online
- Или прямой SSH доступ к хосту `100.107.127.17`

### Действие
Пока оставлю Xvfb :1 работающим и бота запущенным — на случай если кто-то поднимет контейнер и подключит к этому хосту.
