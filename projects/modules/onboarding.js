// ============================================================
// SmartHelper — Модуль онбординга + AI-профиль клиента
// ============================================================
// Этот модуль полностью автономный.
// Интегрируется в существующего бота через:
//   const onboarding = require('./modules/onboarding');
//   bot.use(onboarding.middleware());
// ============================================================

const { Markup } = require('telegraf');
const fs = require('fs');
const path = require('path');

const DATA_DIR = path.join(__dirname, '..', 'data');
const PROFILES_FILE = path.join(DATA_DIR, 'profiles.json');

// ============================================================
// 1. ЗАГРУЗКА/СОХРАНЕНИЕ ПРОФИЛЕЙ
// ============================================================

function loadProfiles() {
  try {
    return JSON.parse(fs.readFileSync(PROFILES_FILE, 'utf-8'));
  } catch {
    return {};
  }
}

function saveProfiles(profiles) {
  const dir = path.dirname(PROFILES_FILE);
  if (!fs.existsSync(dir)) fs.mkdirSync(dir, { recursive: true });
  fs.writeFileSync(PROFILES_FILE, JSON.stringify(profiles, null, 2));
}

function getProfile(userId) {
  const profiles = loadProfiles();
  return profiles[userId] || null;
}

function setProfile(userId, data) {
  const profiles = loadProfiles();
  profiles[userId] = { ...(profiles[userId] || {}), ...data, updatedAt: new Date().toISOString() };
  saveProfiles(profiles);
}

// ============================================================
// 2. ВОПРОСЫ ОПРОСНИКА
// ============================================================

const QUESTIONS = [
  // Вопрос 1 — Ниша
  {
    id: 'niche',
    type: 'buttons_or_text',
    text: `🧭 <b>Расскажи про свой бизнес</b>\n\nКто ты и чем занимаешься? Выбери или напиши своё:`,
    buttons: [
      ['💇 Салон красоты / Бьюти'],
      ['🏋️ Фитнес / Спорт / ЗОЖ'],
      ['🧠 Психология / Коучинг'],
      ['🛍 Интернет-магазин'],
      ['📚 Инфобизнес / Обучение'],
      ['⚖️ Юридические / Бухгалтерские'],
      ['☕ Ресторан / Кафе'],
      ['✏️ Другое (напишу сам)'],
    ],
    nextAfterButton: true, // После нажатия кнопки → след. вопрос
  },

  // Вопрос 2 — Платформы
  {
    id: 'platforms',
    type: 'multiple_choice',
    text: `🌐 <b>Где ты ведёшь соцсети?</b>\n\nВыбери площадки (можно несколько):`,
    buttons: [
      ['✅ Telegram', 'telegram'],
      ['✅ VK', 'vk'],
      ['✅ Дзен', 'dzen'],
      ['✅ Instagram', 'instagram'],
      ['❌ Пока нигде', 'none'],
    ],
    maxSelections: null, // null = без ограничений
    nextButton: '➡️ Далее',
  },

  // Вопрос 3 — Стиль
  {
    id: 'style',
    type: 'buttons',
    text: `🎨 <b>Какой стиль постов тебе ближе?</b>\n\nВыбери один вариант:`,
    buttons: [
      ['🔹 Экспертный — разборы, факты, исследования'],
      ['🔹 Душевный — истории, личный опыт, забота'],
      ['🔹 Продающий — акции, кейсы, товары'],
      ['🔹 Развлекательный — юмор, мемы, лайфстайл'],
      ['🔹 Смешанный — всего понемногу'],
    ],
  },

  // Вопрос 4 — Потребности
  {
    id: 'needs',
    type: 'multiple_choice',
    text: `🎯 <b>Что нужно твоему бизнесу прямо сейчас?</b>\n\nВыбери нужное (можно несколько):`,
    buttons: [
      ['✅ Посты и контент', 'posts'],
      ['✅ Контент-план на месяц', 'plan'],
      ['✅ Прогрев аудитории', 'warming'],
      ['✅ Аналитика', 'analytics'],
      ['✅ Автоматизация', 'automation'],
      ['✅ Всё сразу', 'all'],
    ],
    nextButton: '➡️ Далее',
  },

  // Вопрос 5 — Частота
  {
    id: 'frequency',
    type: 'buttons',
    text: `📅 <b>Как часто хочешь публиковать?</b>\n\nВыбери один вариант:`,
    buttons: [
      ['🌱 1-2 раза в неделю (лёгкий режим)'],
      ['🔥 3-5 раз в неделю (активный)'],
      ['⚡ Каждый день (максимум)'],
      ['🤷 Не знаю, нужна стратегия'],
    ],
  },

  // Вопрос 6 — Аудитория
  {
    id: 'audience',
    type: 'text',
    text: `👥 <b>Кто твоя аудитория?</b>\n\nОпиши коротко: возраст, пол, интересы, боли.\n\n<i>Например: «Женщины 30-45, мамы в декрете, хотят выглядеть хорошо, но нет времени на спортзал»</i>`,
  },

  // Вопрос 7 — Боли
  {
    id: 'pains',
    type: 'text',
    text: `💡 <b>Что сейчас не устраивает в ведении соцсетей?</b>\n\nНапиши пару слов:\n❌ Нет времени\n❌ Не знаю что писать\n❌ Нет результатов\n❌ Что-то другое`,
  },
];

// ============================================================
// 3. СИСТЕМА ПЕРСОНАЛИЗИРОВАННОГО ПРЕДЛОЖЕНИЯ
// ============================================================

/**
 * Генерирует текст персонализированного предложения на основе профиля
 * @param {object} profile - AI-профиль клиента
 * @param {string} userName - имя пользователя
 * @returns {string} - готовое HTML-сообщение
 */
function generatePersonalizedProposal(profile, userName) {
  const { niche, platforms, style, needs, frequency, audience, pains } = profile;

  // Маппинг потребностей в услуги
  const serviceMap = {
    posts: '📝 Регулярные посты — готовый контент под твой стиль',
    plan: '📅 Контент-план на месяц — темы, даты, время публикаций',
    warming: '🔥 Прогрев аудитории — серия продающих постов',
    analytics: '📊 Аналитика раз в неделю — что залетело, что нет',
    automation: '⚡ Автоматизация — посты публикуются сами',
    all: '🏆 Полное ведение — AI делает всё за тебя',
  };

  // Какие услуги подходят
  const selectedServices = (needs || ['posts', 'plan'])
    .filter(n => n !== 'all')
    .map(n => serviceMap[n] || serviceMap.posts);

  // Рекомендация тарифа на основе ответов
  let recommendedTariff = 'Пробный (12 USDT)';
  let tariffDesc = 'Попробуй 14 дней без риска';
  
  if (needs && needs.includes('all')) {
    recommendedTariff = 'Премиум (119 USDT)';
    tariffDesc = 'Полное ведение + аналитика + приоритет';
  } else if (needs && needs.includes('automation')) {
    recommendedTariff = 'Стандарт (59 USDT)';
    tariffDesc = 'Посты + контент-план + автопубликация';
  }

  // Частота публикаций
  const freqMap = {
    '1-2 раза в неделю': '🌱 1-2 раза в неделю',
    '3-5 раз в неделю': '🔥 3-5 раз в неделю',
    'Каждый день': '⚡ Каждый день',
    'Не знаю': '📅 По расписанию (подберём оптимальное)',
  };
  const freqText = freqMap[frequency] || '📅 По согласованию';

  return `
🎯 <b>SmartHelper — персональный план для твоего бизнеса</b>

Привет, ${userName}!

Я проанализировал твои ответы. Вот что я могу для тебя сделать 👇

━━━━━━━━━━━━━━━━━━━━━━
<b>📌 ТВОЙ ПРОФИЛЬ</b>
━━━━━━━━━━━━━━━━━━━━━━

🏢 <b>Ниша:</b> ${niche || 'Не указана'}
🌐 <b>Платформы:</b> ${(platforms || ['Telegram']).join(', ')}
🎨 <b>Стиль:</b> ${style || 'Смешанный'}
👥 <b>Аудитория:</b> ${audience || 'Не указана'}
📅 <b>Частота:</b> ${freqText}

━━━━━━━━━━━━━━━━━━━━━━
<b>🔥 ЧТО Я ПРЕДЛАГАЮ</b>
━━━━━━━━━━━━━━━━━━━━━━

${selectedServices.map(s => `• ${s}`).join('\n')}

${pains ? `💡 <b>Я знаю, что тебя беспокоит:</b> ${pains}\n\nЯ создан решать именно такие задачи.` : ''}

━━━━━━━━━━━━━━━━━━━━━━
<b>💎 РЕКОМЕНДУЕМЫЙ ТАРИФ</b>
━━━━━━━━━━━━━━━━━━━━━━

<b>${recommendedTariff}</b>
${tariffDesc}

⬇️ <b>Хочешь попробовать?</b> 👇
`.trim();
}

// ============================================================
// 4. ОБРАБОТЧИК ОПРОСНИКА
// ============================================================

function createOnboardingHandlers(bot) {
  const sessions = {}; // userId → { questionIndex, answers: {} }

  /**
   * Начать опросник
   */
  function startQuestionnaire(ctx) {
    const userId = ctx.from.id;
    sessions[userId] = { questionIndex: 0, answers: {} };
    return sendQuestion(ctx, userId);
  }

  /**
   * Отправить текущий вопрос
   */
  async function sendQuestion(ctx, userId) {
    const session = sessions[userId];
    if (!session) {
      return ctx.reply('❌ Что-то пошло не так. Начни заново — /start');
    }

    const question = QUESTIONS[session.questionIndex];
    if (!question) {
      // Опросник завершён — формируем предложение
      return finishQuestionnaire(ctx, userId);
    }

    const keyboard = Markup.inlineKeyboard(
      (question.buttons || []).map(row => {
        if (question.type === 'multiple_choice') {
          // Для множественного выбора добавляем callback data
          return row.map(btn => Markup.button.callback(btn[0], `qn_${question.id}_${btn[1]}`));
        }
        // Для обычных кнопок
        return row.map(btn => Markup.button.callback(btn[0], `qn_${question.id}_${btn[0]}`));
      })
    );

    // Добавляем кнопку "Далее" для multiple_choice
    if (question.type === 'multiple_choice' && question.nextButton) {
      keyboard.inline_keyboard.push([
        Markup.button.callback(question.nextButton, `qn_next_${question.id}`)
      ]);
    }

    // Кнопка "Назад"
    if (session.questionIndex > 0) {
      keyboard.inline_keyboard.push([
        Markup.button.callback('🔙 Назад', 'qn_back')
      ]);
    }

    const msg = await ctx.reply(question.text, {
      parse_mode: 'HTML',
      ...(question.type !== 'text' ? keyboard : Markup.removeKeyboard()),
    });

    session.messageId = msg.message_id;
    return msg;
  }

  /**
   * Обработать ответ на вопрос
   */
  async function handleAnswer(ctx, answer) {
    const userId = ctx.from.id;
    const session = sessions[userId];
    if (!session) return;

    const question = QUESTIONS[session.questionIndex];
    if (!question) return;

    // Сохраняем ответ
    if (question.type === 'multiple_choice') {
      if (!session.answers[question.id]) {
        session.answers[question.id] = [];
      }
      if (!session.answers[question.id].includes(answer)) {
        session.answers[question.id].push(answer);
      }
    } else {
      session.answers[question.id] = answer;
    }

    // Для текстовых вопросов — ждём текст
    if (question.type === 'text') return;

    // Для кнопок — сразу на следующий вопрос
    session.questionIndex++;
    await ctx.deleteMessage().catch(() => {});
    return sendQuestion(ctx, userId);
  }

  /**
   * Завершить опросник
   */
  async function finishQuestionnaire(ctx, userId) {
    const session = sessions[userId];
    const profile = session.answers;

    // Сохраняем профиль
    setProfile(userId, {
      profileCompleted: true,
      profileData: profile,
    });

    // Генерируем персонализированное предложение
    const userName = ctx.from.first_name || 'Друг';
    const proposal = generatePersonalizedProposal(profile, userName);

    // Очищаем сессию
    delete sessions[userId];

    await ctx.reply(`✅ <b>Спасибо, ${userName}!</b>\n\nТвой профиль сохранён. Анализирую...`, {
      parse_mode: 'HTML',
    });

    // Небольшая пауза — эффект "AI анализирует"
    await new Promise(r => setTimeout(r, 1500));

    await ctx.reply(proposal, {
      parse_mode: 'HTML',
      ...Markup.inlineKeyboard([
        [Markup.button.callback('🆓 Попробовать 14 дней', 'tariff_trial')],
        [Markup.button.callback('🚀 Хочу Стандарт', 'tariff_standard')],
        [Markup.button.callback('💬 Задать вопрос', 'support')],
      ]),
    });
  }

  // ============================================================
  // CALLBACK HANDLERS
  // ============================================================

  // Обработка нажатий на кнопки опросника
  bot.on('callback_query', async (ctx, next) => {
    if (!ctx.callbackQuery || !ctx.callbackQuery.data) return next();
    const data = ctx.callbackQuery.data;
    const userId = ctx.from.id;

    // Кнопка "Назад"
    if (data === 'qn_back') {
      const session = sessions[userId];
      if (session && session.questionIndex > 0) {
        session.questionIndex--;
        await ctx.deleteMessage().catch(() => {});
        return sendQuestion(ctx, userId);
      }
    }

    // Кнопка "Далее" для multiple_choice
    if (data.startsWith('qn_next_')) {
      const questionId = data.replace('qn_next_', '');
      const session = sessions[userId];
      if (session) {
        session.questionIndex++;
        await ctx.deleteMessage().catch(() => {});
        return sendQuestion(ctx, userId);
      }
    }

    // Ответ на вопрос
    if (data.startsWith('qn_')) {
      const parts = data.split('_');
      const questionId = parts[1];
      const answer = parts.slice(2).join('_');
      return handleAnswer(ctx, answer);
    }

    return next();
  });

  // Обработка текстовых ответов на вопросы
  bot.on('text', async (ctx, next) => {
    const userId = ctx.from.id;
    const session = sessions[userId];
    if (!session) return next();

    const question = QUESTIONS[session.questionIndex];
    if (!question || question.type !== 'text') return next();

    const answer = ctx.message.text.trim();
    if (answer.startsWith('/')) return next();

    session.answers[question.id] = answer;
    session.questionIndex++;
    return sendQuestion(ctx, userId);
  });

  return {
    startQuestionnaire,
    getProfile,
    generatePersonalizedProposal,
  };
}

// ============================================================
// 5. MIDDLEWARE — автоматическое предложение опросника
// ============================================================

/**
 * Middleware: если пользователь без профиля → предлагает опросник
 * Использование: bot.use(onboarding.onboardingMiddleware());
 */
function onboardingMiddleware() {
  return async (ctx, next) => {
    if (!ctx.from || ctx.chat.type !== 'private') return next();
    if (!ctx.message?.text) return next();

    const userId = ctx.from.id;
    const text = ctx.message.text;

    // Не перехватываем команды
    if (text.startsWith('/')) return next();

    const profile = getProfile(userId);

    // Если профиля нет — это новый пользователь
    // Не перехватываем, пропускаем дальше
    // (опросник запускается только после /start или кнопки)

    return next();
  };
}

module.exports = {
  createOnboardingHandlers,
  onboardingMiddleware,
  getProfile,
  setProfile,
  generatePersonalizedProposal,
  QUESTIONS,
};
