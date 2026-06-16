# Belfort — Инфраструктура (актуально)

## 🔧 Система

| Компонент | Статус | Как запущен |
|-----------|--------|-------------|
| Freqtrade | 🟢 Работает | `/root/freqtrade/venv/bin/freqtrade trade ...` |
| Health Monitor | 🟢 Работает | `/root/.hermes/health_monitor.py` (проверка каждые 5 мин) |
| API порт | 🟢 8080 | Логин: belfort / Пароль: Bbatkavi4 |
| Cron | 🟢 Настроен | Проверка каждые 5 мин + автозапуск при @reboot |

## 🤖 Автовосстановление
1. **Cron** — `*/5 * * * * /root/.hermes/start_freq.sh` — проверяет и запускает Freqtrade если упал
2. **Health Monitor** — `health_monitor.py` — живёт в фоне, каждые 5 мин чекает API Freqtrade
3. **@reboot** — crontab запускает всё при перезагрузке сервера

## 📡 Crontab
```
*/5 * * * * /root/.hermes/start_freq.sh > /dev/null 2>&1
@reboot sleep 10 && /root/.hermes/start_freq.sh > /dev/null 2>&1
```

## 📊 Авто-отчёты
- Каждые 6 часов — приходит отчёт о состоянии портфеля и рынка

## 🔑 Ключи
- OKX Key: 71055e51-9e05-41fd-9b3c-38b6b133642e
- OKX Secret: A40EFA4295F34AD400C77AEE5F06DEB9
- OKX Passphrase: Bbatkavi4@
- Freqtrade API: belfort / Bbatkavi4

## 📁 Расположение
- Freqtrade: `/root/freqtrade/`
- Конфиг: `/root/freqtrade/config.json`
- Стратегия: `/root/freqtrade/strategies/BelfortSOLStrategy.py`
- Логи: `/root/.hermes/health_monitor.log`
- Wiki: `/root/wiki/agent-notes/`
