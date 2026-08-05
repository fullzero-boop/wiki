# Telegram боты

## Инфраструктура
- Все боты — Docker-контейнеры (`bot-qwen3` образ)
- Сеть: `--network host`
- Рестарт: `--restart unless-stopped`
- Health-порты: 8001-8008 (по одному на бота)
- Прокси: SOCKS5 через MacBook (`192.168.50.6:1080`)
- Модель: `qwen2.5:1.5b` (через Ollama на localhost)

## Список ботов
| Бот | Username | Роль | Health порт |
|-----|----------|------|-------------|
| Sinabon | @ElzaAphorismsBot | aphorisms | 8001 |
| Tsilya | @OdesskieMansiBot | odessite | 8002 |
| Paladin | @Paladin3_bot | men-s-community | 8003 |
| Shadow | @shadow1989bot | orchestrator | 8004 |
| Hermes | @Germes159Bot | marketer | 8005 |
| Gost | @Ghost11155bot | assistant | 8006 |
| Belfort | @Belford159bot | crypto-trader | 8007 |
| Jarvis | @Casper135Bot | content-creator | 8008 |

## Персональные профили
Хранятся в `wiki/agents/<bot>.md`.
Каждый содержит: personality, style, memory_preference.

## Jarvis (standalone)
Также работает как отдельный Python-скрипт:
`/home/evgeniy/jarvis_v2.py` — использует DeepSeek API + LightRAG.
