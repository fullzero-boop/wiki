// ============================================================
// SmartHelper — Grace Period + Proactive Suggestions
// ============================================================
// После оплаты: 15 мин мгновенного доступа + AI сам предлагает
// решения на основе профиля пользователя
// ============================================================

const { Markup } = require('telegraf');

const GRACE_PERIOD_MS = 15 * 60 * 1000; // 15 минут

/**
 * Предоставляет grace period после отправки платежа
 * Пользователь получает доступ сразу, пока проверяется TronGrid
 */
function activateGracePeriod(users, userId, tariffId) {
  const now = Date.now();
  
  if (!users[userId]) return false;

  users[userId].gracePeriod = {
    active: true,
    startedAt: now,
    expiresAt: now + GRACE_PERIOD_MS,
    tariffId: tariffId,
  };
  
  return true;
}

/**
 * Проверяет, активен ли grace period у пользователя
 */
function isGracePeriodActive(user) {
  if (!user || !user.gracePeriod || !user.gracePeriod.active) return false;
  if (Date.now() > user.gracePeriod.expiresAt) {
    user.gracePeriod.active = false;
    return false;
  }
  return true;
}

/**
 * AI-генерация проактивных предложений на основе профиля
 */

function generateProactiveSuggestions(profile) {
  if (!profile || !profile.profileData) return null;

  const { niche, style, platforms, needs, frequency } = profile.profileData;
  
  const suggestions = [];

  // Предложение 1 — Контент-план
  if (needs && (needs.includes('plan') || needs.includes('all'))) {
    suggestions.push({
      type: 'content_plan',
      title: '📅 Контент-план на неделю',
      text: `Уже готов контент-план для ${niche || 'твоего бизнеса'} на эту неделю. Хочешь посмотреть?`,
      button: '📅 Показать план',
    });
  }

  // Предложение 2 — Пост под нишу
  if (niche) {
    suggestions.push({
      type: 'generate_post',
      title: '📝 Пост под твою нишу',
      text: `Я могу написать пост для ${niche} в твоём стиле прямо сейчас. Попробуем?`,
      button: '✍️ Написать пост',
    });
  }

  // Предложение 3 — Анализ конкурентов
  if (niche && (needs && (needs.includes('analytics') || needs.includes('all')))) {
    suggestions.push({
      type: 'competitor_analysis',
      title: '📊 Анализ конкурентов',
      text: `Хочешь узнать, что публикуют конкуренты в нише "${niche}"? Я сделаю разбор за 2 минуты.`,
      button: '🔍 Анализировать',
    });
  }

  // Предложение 4 — Хештеги
  suggestions.push({
    type: 'hashtags',
    title: '🏷 Хештеги для твоих постов',
    text: `Подберу эффективные хештеги под ${niche || 'твою тему'} для ${(platforms || ['Telegram']).join(', ')}.`,
    button: '🏷 Подобрать хештеги',
  });

  return suggestions;
}

/**
 * Показывает проактивное предложение пользователю
 */
async function showProactiveSuggestion(ctx, suggestion) {
  if (!suggestion) return;

  const keyboard = Markup.inlineKeyboard([
    [Markup.button.callback(suggestion.button, `proactive_${suggestion.type}`)],
    [Markup.button.callback('⏸ Позже', 'proactive_later')],
    [Markup.button.callback('❌ Не предлагать', 'proactive_dismiss')],
  ]);

  await ctx.reply(`🤖 <b>SmartHelper</b>\n\n${suggestion.text}`, {
    parse_mode: 'HTML',
    ...keyboard,
  });
}

/**
 * Приветствие после оплаты (с grace period)
 */
function paymentSuccessMessage(userName, tariffName, duration) {
  return `
🎉 <b>Поздравляю, ${userName}!</b>

<b>${tariffName}</b> активирован на <b>${duration}</b> 🚀

🔥 <b>Что дальше?</b>
Сейчас я задам тебе 5 вопросов о твоём бизнесе.
На основе ответов настрою AI под тебя — и ты получишь готовые посты, контент-план и стратегию.

⬇️ <b>Поехали?</b> 👇
`.trim();
}

module.exports = {
  activateGracePeriod,
  isGracePeriodActive,
  generateProactiveSuggestions,
  showProactiveSuggestion,
  paymentSuccessMessage,
  GRACE_PERIOD_MS,
};
