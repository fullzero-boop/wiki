# Account Automation Toolkit — GitHub Research

**Дата:** 2026-06-15  
**Для:** Gost (30 email registrations), Hermes (общая автоматизация)

## Состояние окружения

### ✅ УЖЕ УСТАНОВЛЕНО
| Пакет | Версия | Назначение |
|---|---|---|
| undetected-chromedriver | 3.5.5 | Стелс-браузер (Selenium) |
| 2captcha-python | 2.0.7 | Капча (ключ: 8f295dcf...) |
| capsolver | 1.0.7 | Капча (ключ: CAP-C9AFD9...) |
| pymailtm | 1.1.1 | Временная почта mail.tm |
| temp-mail | 1.0.1 | Временная почта temp-mail.org |
| selenium | 4.44.0 | Браузерная автоматизация |

### 🔑 API КЛЮЧИ ЕСТЬ
- **CapSolver:** CAP-C9AFD9CF94F9B41D4F78A6A82E5471AD7E58C8D717DBAFDF11164FB55048BF0B
- **2Captcha:** 8f295dcfd6b40c4bb3e311672bd8b0d7
- **OnlineSim:** 837mqh4bS52Ukfm-tA3LS3S6-c98m7h5S-u1rch8Y6-F7FR4v7y3bB55a4

### 📦 НУЖНО ДОУСТАНОВИТЬ
```
pip install fivesim
pip install tempmail-python
pip install unicaps
pip install git+https://github.com/s00d/onlinesim-python-api.git
```

## ТОП репозитории по категориям

### Временные почты
| Репозиторий | Звёзды | Язык | Описание |
|---|---|---|---|
| BalliAsghar/Mailsy | 592⭐ | JS | Временная почта из терминала |
| saippuakauppias/temp-mail | 103⭐ | Python | API wrapper temp-mail.org |
| CarloDePieri/pymailtm | 89⭐ | Python | mail.tm API wrapper — **лучший выбор, уже стоит** |

### Капча
| Репозиторий | Звёзды | Язык | Описание |
|---|---|---|---|
| NopeCHALLC/nopecha-python | 1652⭐ | Python | HCaptcha, FunCaptcha, AWS WAF |
| 2captcha/2captcha-python | 762⭐ | Python | Официальный 2captcha — **уже стоит** |
| capsolver/capsolver-python | 72⭐ | Python | Официальный CapSolver — **уже стоит** |
| sergey-scat/unicaps | 233⭐ | Python | Унифицированное API для всех капча-сервисов |

### Регистрация аккаунтов
| Репозиторий | Звёзды | Язык | Что делает |
|---|---|---|---|
| ai-to-ai/Auto-Gmail-Creator | 1263⭐ | Python | Массовое создание Gmail |
| NightfallGT/Discord-Account-Generator | 418⭐ | Python | Авторегистрация Discord без капчи |
| silvestrodecaro/microsoft-account-creator | 180⭐ | JS | Создание Microsoft/Outlook аккаунтов |

### SMS-верификация
| Репозиторий | Звёзды | Язык | Описание |
|---|---|---|---|
| tezmen/python-sms-activate-ru | 61⭐ | Python | sms-activate.ru wrapper |
| s00d/onlinesim-python-api | 30⭐ | Python | OnlineSim wrapper — **нужен для Gost** |
| ErikPelli/fivesim | 15⭐ | Python | 5sim API клиент |

### Антидетект
| Репозиторий | Звёзды | Язык | Описание |
|---|---|---|---|
| D4Vinci/Scrapling | 63923⭐ | Python | Фреймворк для скрапинга с антиботом |
| CloakHQ/CloakBrowser | 26201⭐ | Python | Стелс Chromium |
| daijro/camoufox | 9254⭐ | C++ | Антидетект Firefox — **лучший для новых задач** |
| ultrafunkamsterdam/undetected-chromedriver | 12693⭐ | Python | **Золотой стандарт — уже стоит** |
| seleniumbase/SeleniumBase | 12791⭐ | Python | Selenium + стелс |

### Комплексные фреймворки
| Репозиторий | Звёзды | Описание |
|---|---|---|
| Vinyzu/Botright | 996⭐ | Undetected + captcha + automation |
| TikHub/TikHub-API-Python-SDK | 706⭐ | Captcha + temp mail + соцсети |

## Рекомендуемый стек для регистраций

```
temp mail: pymailtm (mail.tm) — бесплатно, без API ключа
captcha:  2captcha-python или capsolver — оба с ключами
браузер:  undetected-chromedriver (уже стоит)
SMS:      onlinesim-python-api + fivesim (доустановить)
```

## Инфраструктура
- Сервер: evgeniy-5 (30GB RAM, 16 ядер)
- Отчёт: /data/hermes/github_research_report.md
- Данные: /tmp/gh_results*.json

## Связанные
- [[infrastructure/Infrastructure.md]]
- [[osrs-botting-guide.md]]
