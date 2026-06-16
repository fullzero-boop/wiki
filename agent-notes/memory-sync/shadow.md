# Shadow — Memory (2026-06-16 15:16 UTC)

Всего фактов: 25

> **NEW** (id=1, general)
  Project: регистрация аккаунтов Instagram через прокси. Используется OnlineSim для получения SMS-кодов. Прокси: 5x UK (proxy6.net, до 06.07), 1x FR (Rapidseedbox), MTProto прокси для Telegram. User: Евгений Сергеевич (Telegram DM).

> **NEW** (id=2, general)
  Project "Social Agent" — мультиплатформенный AI-агент для ведения соцсетей (VK, Telegram, Instagram, Яндекс Дзен). Использует прокси для входа и работы. Цель: отрепетировать вход/авторизацию на всех платформах, сделать стабильный продукт для продажи.

> **NEW** (id=3, project)
  Project "Social Agent" — мультиплатформенный AI-агент для ведения соцсетей

> **NEW** (id=4, tool)
  5 рабочих прокси UK (proxy6.net): 196.19.5.174:8000, 196.18.9.253:8000, 196.18.9.49:8000, 196.19.4.222:8000, 196.19.4.99:8000 — логин 2vNLZe, пароль BF9eKm, HTTPS/SOCKS5, истекают 06.07.26

> **NEW** (id=5, tool)
  Прокси FR: 45.152.203.177:8000 — логин y61zY2, пароль G1oBFJ, HTTP/SOCKS5

> **NEW** (id=6, general)
  Social Agent проект: /root/social-agent. Node.js + Playwright. Прокси-мост (Node.js HTTP forward proxy) решает проблему авторизации Playwright на прокси. Модули: VK, Instagram, Telegram Web, Яндекс Дзен. Прокси: 5 UK + 1 FR — все рабочие.

> **NEW** (id=7, tool)
  Telegram бот @SmartHelper579Bot (ID: 8656563898) — точка продаж Social Agent. Токен сохранён. Вебхук не установлен, сервер пустой. Надо прикрутить криптокошелёк и логику продаж.

> **NEW** (id=8, user_pref)
  User: Евгений Сергеевич. Telegram DM @Evgeny_Sergeevich (username inferred). Партнёр по проекту Social Agent. Русскоязычный.

> **NEW** (id=9, user_pref)
  Евгений Сергеевич — Telegram ID 425193245, username @Exp_Vse_Prosto. Админ проекта Social Agent.

> **NEW** (id=10, general)
  Интеграции Social Agent: CapSolver (CAP-C9AF...BF0B), 2Captcha (8f295...0d7), OnlineSim (837mq...5a4), HTX биржа. Файл: /root/social-agent/.env.services

> **NEW** (id=11, general)
  Bot @SmartHelper579Bot на Node.js + Telegraf. Проблема: HTTP_PROXY окружения Docker блокировал подключение к Telegram API. Фикс: bot.js чистит proxy-переменные при старте. Работает через polling.

> **NEW** (id=12, tool)
  HTX API: рекомендуется привязка к IP сервера (155.212.224.160). Без привязки ключ с торговыми правами деактивируется через 90 дней бездействия. При регулярном использовании продлевается автоматически.

> **NEW** (id=13, general)
  HTX API credentials: Access Key 0373b67c-afc12d2c-bgrveg5tmn-8cde5, Secret Key 02ba6013-660e647c-49f1dd0f-f36b9, IP bound to 155.212.224.160, permissions: Read, Withdraw, Trade

> **NEW** (id=14, tool)
  User provided USDT TRC20 wallet address for receiving payments: TSs5NbAozMW6vy3mNt493nAGK86AVrDMKL

> **NEW** (id=15, general)
  test

> **NEW** (id=16, general)
  SmartHelper Bot @SmartHelper579Bot запущен через PM2 (pid 13162). Токен обновлён. Прокси настроен: PROXY_HOST=172.22.0.1:18119 (HttpsProxyAgent). Исправлена ошибка импорта 'telegraf/filters.js' → 'telegraf/filters'. Исправлена структура .env. SVG-баннеры сконвертированы в PNG. Исправлена welcomeMessage — убрана ссылка на несуществующую кнопку "Начать". Исправлен bot.launch() — .then() никогда не срабатывал (long polling бесконечный), теперь getMe() проверяет связь, а launch() запускается fire-and-forget.

> **NEW** (id=17, general)
  SmartHelper бот переработан: система внутреннего баланса (пополнение USDT на внутренний счёт), тарифы: пробный 12 USDT (~1000₽) на 14 дней, стандарт/премиум/VIP: 59/119/179 USDT. Добавлены: /deposit, крипто-инструкции (Trust Wallet, Bybit, OKX), все кнопки активны (профиль с балансом, документы, возвраты, поддержка, о сервисе). Оплата списывается с баланса, пополнение через TronGrid.

> **NEW** (id=18, general)
  SmartHelper: Payment flow changed. Тарифы → Оплатить → сразу показывает кошелёк USDT TRC20 + сообщение "принимаем только крипту". Бот проверяет через TronGrid при нажатии "Я оплатил". Если тип tariff в заказе — активирует подписку сразу. Если deposit — добавляет на баланс. Цены в рублях везде. Legal документы переписаны в брендовом оранж/голд стиле.

> **NEW** (id=19, general)
  Leonardo AI доступ: аккаунт/токен be4ed32b-4978-46da-93fb-47c505ab20ca. Можно использовать для генерации дизайна ассетов SmartHelper (лого, баннеры, иконки).

> **NEW** (id=20, general)
  Leonardo AI: be4ed32b-4978-46da-93fb-47c505ab20ca — доступ для генерации дизайна ассетов SmartHelper (лого, баннеры, иконки).

> **NEW** (id=21, general)
  @sozdatelnica (ID 345344419, Татьяна) — оплаченный тариф standard, полный доступ, активно до 23.06.2026. Переведена с trial на standard.

> **NEW** (id=22, user_pref)
  AI SmartHelper запрещённые темы: политика, война, оружие, взрывчатка. Ответ: «Извините, я создан для помощи в ведении соцсетей и бизнеса».

> **NEW** (id=23, general)
  This Hermes agent session runs in a different environment than the bot server. The bot @SmartHelper579Bot runs on production server at IP 155.212.224.160 (Ubuntu 22.04). This terminal environment (7d3ed084da98) is a separate container with node v12, no PM2, no bot files. Can't directly check bot process from terminal - rely on earlier PM2 status checks in the same deployment turn.

> **NEW** (id=24, user_pref)
  Евгений хочет: убрать политику возврата, оставить согласие на обработку данных — показывать перед оплатой (перед кнопкой 100/пробного тарифа). Говорит что у меня есть доступ к боту SmartHelper через бот хелпер.

> **NEW** (id=25, project)
  Евгений хочет: убрать политику возврата, оставить согласие на обработку данных — показывать перед оплатой (перед кнопкой пробного тарифа). Есть доступ к боту SmartHelper через бот хелпер.

