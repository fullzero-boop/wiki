// ============================================================
// SmartHelper — Главная логика: меню + интеграция модулей
// ============================================================
// Как подключить к существующему боту:
//   1. Скопировать папку modules/ в проект
//   2. Добавить require в bot.js
//   3. Интегрировать через registerModules(bot, config)
// ============================================================

const { Markup } = require('telegraf');

// ============================================================
// 1. НОВАЯ СТРУКТУРА МЕНЮ
// ============================================================

/**
 * Клавиатура гостя (без подписки)
 */
function guestKeyboard() {
  return Markup.keyboard([
    ['🚀 Тарифы', '🆓 Попробовать 14 дней'],
    ['👤 Профиль', '📖 Документы'],
    ['🤖 О сервисе', '📞 Поддержка'],
  ]).resize();
}

/**
 * Клавиатура подписчика (с подпиской)
 */
function subscriberKeyboard() {
  return Markup.keyboard([
    ['💬 Чат с AI', '👤 Профиль'],
    ['📊 Активность', '⚙️ Настройки'],
    ['📖 Документы', '📞 Поддержка'],
    ['➕ Пригласить друга'],
  ]).resize();
}

/**
 * Админ-клавиатура (дополнительные кнопки для админа)
 */
function adminKeyboard() {
  return Markup.keyboard([
    ['👥 Пользователи', '📊 Статистика'],
    ['📦 Заказы', '📝 Рассылка'],
    ['💬 Чат с AI', '👤 Профиль'],
  ]).resize();
}

// ============================================================
// 2. НОВАЯ ЛОГИКА /start
// ============================================================

async function handleStart(ctx, config, onboarding) {
  const userId = ctx.from.id;
  const userName = ctx.from.first_name || 'Друг';
  const isAdmin = userId === config.adminId;

  // Проверяем реферальный переход
  const refCode = ctx.message.text.match(/ref_(.+)/);
  if (refCode) {
    try {
      const referrerId = parseInt(Buffer.from(refCode[1], 'base64').toString('utf-8'), 10);
      if (referrerId && referrerId !== userId) {
        const { processReferral } = require('./referral');
        processReferral(referrerId, userId);
      }
    } catch (e) {
      // Невалидный реферальный код — игнорируем
    }
  }

  // Приветствие
  const welcomeText = `
🚀 <b>SmartHelper</b> — твой AI-помощник для соцсетей

Привет, ${userName}! 🤝

Я помогу тебе:
• 📝 Писать посты для VK, Telegram, Дзен
• 📅 Планировать контент на месяц
• 🔥 Прогревать аудиторию
• 📊 Анализировать что залетело
• 🎨 Создавать обложки к постам

<b>Просто выбери, что нужно 👇</b>
`.trim();

  const userProfile = onboarding.getProfile(userId);

  // Если профиля нет — предлагаем опросник
  if (!userProfile || !userProfile.profileCompleted) {
    const keyboard = Markup.inlineKeyboard([
      [Markup.button.callback('🎯 Заполнить профиль', 'start_questionnaire')],
      [Markup.button.callback('🚀 Смотреть тарифы', 'view_tariffs')],
    ]);

    await ctx.reply(welcomeText + '\n\n<i>Рекомендую начать с профиля — я настроюсь под твой бизнес</i>', {
      parse_mode: 'HTML',
      ...keyboard,
    });
    return;
  }

  // Профиль заполнен — показываем полное меню
  const keyboard = isAdmin ? adminKeyboard() : 
    (userProfile.subscription ? subscriberKeyboard() : guestKeyboard());

  await ctx.reply(welcomeText + `\n\n✅ <i>Твой профиль заполнен. Я готов помогать!</i>`, {
    parse_mode: 'HTML',
    ...keyboard,
  });
}

// ============================================================
// 3. АВТОМАТИЧЕСКИЕ ПРЕДЛОЖЕНИЯ ПОСЛЕ ОПЛАТЫ
// ============================================================

async function handlePaymentSuccess(ctx, userId, users, config, onboardingModule) {
  const userName = ctx.from.first_name || 'Друг';
  const user = users[userId];
  const tariffName = user.subscription || 'Тариф';
  
  // Сообщение об успехе
  await ctx.reply(`
🎉 <b>Поздравляю, ${userName}!</b>

<b>${tariffName}</b> активирован! 🚀

Сейчас я задам тебе 5 вопросов, чтобы настроить AI под твой бизнес.
`.trim(), {
    parse_mode: 'HTML',
    ...Markup.inlineKeyboard([
      [Markup.button.callback('🎯 Заполнить профиль', 'start_questionnaire')],
      [Markup.button.callback('💬 Просто чат с AI', 'ai_chat')],
    ]),
  });

  // Проактивное предложение через 30 секунд
  setTimeout(async () => {
    try {
      const { generateProactiveSuggestions, showProactiveSuggestion } = require('./grace-period');
      const profile = onboardingModule.getProfile(userId);
      const suggestions = generateProactiveSuggestions(profile);
      
      if (suggestions && suggestions.length > 0) {
        // Показываем первое предложение через 30 сек
        await showProactiveSuggestion(ctx, suggestions[0]);
        
        // Остальные — с интервалом
        for (let i = 1; i < Math.min(suggestions.length, 3); i++) {
          setTimeout(() => showProactiveSuggestion(ctx, suggestions[i]), 30000 * (i + 1));
        }
      }
    } catch (e) {
      console.error('Proactive suggestion error:', e.message);
    }
  }, 30000);
}

// ============================================================
// 4. РЕГИСТРАЦИЯ ВСЕХ МОДУЛЕЙ
// ============================================================

function registerModules(bot, config) {
  // Подключаем модули
  const onboarding = require('./onboarding');
  const referral = require('./referral');
  
  // Создаём обработчики
  const onboardingHandlers = onboarding.createOnboardingHandlers(bot);
  const referralHandlers = referral.createReferralHandlers(bot, config);

  // Обработчик /start
  bot.start(async (ctx) => {
    await handleStart(ctx, config, onboarding);
  });

  // Обработчик кнопки "➕ Пригласить друга"
  bot.hears('➕ Пригласить друга', async (ctx) => {
    await referralHandlers.showReferralInfo(ctx);
  });

  // Кнопка "🎯 Заполнить профиль"
  bot.action('start_questionnaire', async (ctx) => {
    await ctx.deleteMessage().catch(() => {});
    await onboardingHandlers.startQuestionnaire(ctx);
  });

  return {
    onboardingHandlers,
    referralHandlers,
    handlePaymentSuccess,
  };
}

module.exports = {
  guestKeyboard,
  subscriberKeyboard,
  adminKeyboard,
  handleStart,
  handlePaymentSuccess,
  registerModules,
};
