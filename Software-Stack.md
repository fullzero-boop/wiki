# Программный стек

## Ядро
- **ОС:** Ubuntu 24.04.4 LTS
- **Docker:** v29.6.2
- **Docker Compose:** v5.3.1
- **Ollama:** 0.32.1 (нативный, не Docker)
- **Python:** 3.12

## Сервисы
| Сервис | Тип | Запуск |
|--------|-----|--------|
| ollama | systemd | native |
| lightrag | systemd | lightrag-api-v2.py |
| docker | systemd | контейнеры |
| ssh | systemd | доступ |

## Docker контейнеры
Все контейнеры стартуют автоматически (`--restart unless-stopped`):

### Боты (8 шт)
- Образ: `bot-qwen3`
- Код: `bell-farben/agents/tg-gateway/app/bot.py`

### Инфраструктура
- `bf_memory_service` — Memory Service (port 8005)
- `bf_postgres` — PostgreSQL (port 5432)
- `bf_redis` — Redis (port 6379)
- `obsidian-box` — Obsidian (port 3001)
- `ai-gateway` — AI Gateway (port 18890)
- `msdl-backend` — MSDL API (port 3002)

## GPU подготовка
Скрипт установки: `/home/evgeniy/gpu_setup.sh`
Пакеты: vllm, unsloth, torch (установлены через pip)
Модели: deepseek-r1:32b (качается), qwen3:8b (готова)
