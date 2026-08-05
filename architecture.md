# Архитектура системы

## Видение

### Мини-ПК (evgenyn-5) — Obsidian-сервер
- Intel i7-13620H, 31GB RAM, 954GB NVMe
- **Роль:** Wiki, заметки, документация (Obsidian)
- Лёгкая нагрузка, всегда доступен

### Новый сервер (evgenyn-1) — Вычислительное ядро
- Intel i9-14900, 62GB RAM, 1.83TB NVMe
- **Роль:** Все расчёты, LLM, GPU (когда появится)
- Основная память и данные
- Docker: 8 ботов, инфраструктура
- Ollama: deepseek-r1:32b, qwen3, bge-m3
- LightRAG: память ботов
- Model Router: RAG + маршрутизация

### MacBook Air (Bishop) — Сетевой шлюз
- OpenClaw с DeepSeek API
- SOCKS5 прокси
- Резервный доступ к серверам через Tailscale

## Сеть
```
Telegram / VK
    │
    ├── Лекс (OpenClaw, DeepSeek V4 Flash)
    │       │
    │       └── evgenyn-1 (через Tailscale)
    │               ├── Ollama (локальные модели)
    │               ├── LightRAG :18888
    │               ├── Model Router :18890
    │               └── Docker: 8 ботов
    │
    ├── Бишоп (MacBook, OpenClaw, DeepSeek V4 Flash)
    │       │
    │       ├── VK (через LongPoll)
    │       └── SOCKS5 :1080
    │
    ├── Джарвис (VK LongPoll → DeepSeek)
    └── Остальные боты (Telegram → Ollama/DeepSeek)
```

## Миграция с Beget
- **Текущий:** Beget VPS (SOCKS5)
- **Цель:** Полностью уйти с Beget
- **Альтернатива:** SOCKS5 через Bishop (MacBook) или прямой Tailscale

## Планы
- [ ] GPU на evgenyn-1 (для быстрых LLM)
- [ ] Все боты на VK (онлайн 24/7)
- [x] Лекс на VK (DeepSeek V4 Flash)
- [x] Джарвис на VK (DeepSeek V4 Flash)
- [ ] Бишоп на VK
- [ ] Отказ от Beget
