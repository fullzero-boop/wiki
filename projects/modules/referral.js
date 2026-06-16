// ============================================================
// SmartHelper — Реферальная система
// ============================================================
// Пользователь приводит друга → получает +7 дней Премиум
// ============================================================

const { Markup } = require('telegraf');
const fs = require('fs');
const path = require('path');

const DATA_DIR = path.join(__dirname, '..', 'data');
const REFERRALS_FILE = path.join(DATA_DIR, 'referrals.json');
const USERS_FILE = path.join(DATA_DIR, 'users.json');

// ============================================================
// 1. ДАННЫЕ
// ============================================================

function loadReferrals() {
  try { return JSON.parse(fs.readFileSync(REFERRALS_FILE, 'utf-8')); }
  catch { return {}; }
}

function saveReferrals(data) {
  const dir = path.dirname(REFERRALS_FILE);
  if (!fs.existsSync(dir)) fs.mkdirSync(dir, { recursive: true });
  fs.writeFileSync(REFERRALS_FILE, JSON.stringify(data, null, 2));
}

function loadUsers() {
  try { return JSON.parse(fs.readFileSync(USERS_FILE, 'utf-8')); }
  catch { return {}; }
}

function saveUsers(data) {
  const dir = path.dirname(USERS_FILE);
  if (!fs.existsSync(dir)) fs.mkdirSync(dir, { recursive: true });
  fs.writeFileSync(USERS_FILE, JSON.stringify(data, null, 2));
}

// ============================================================
// 2. ЛОГИКА РЕФЕРАЛОВ
// ============================================================

const REFERRAL_BONUS_DAYS = 7; // Дней Премиум за приведённого друга

/**
 * Генерирует реферальную ссылку для пользователя
 */
function generateReferralLink(botUsername, userId) {
  const code = Buffer.from(String(userId)).toString('base64').replace(/=/g, '');
  return `https://t.me/${botUsername}?start=ref_${code}`;
}

/**
 * Обрабатывает переход по реферальной ссылке
 * @param {number} referrerId - ID пригласившего
 * @param {number} newUserId - ID нового пользователя
 */
function processReferral(referrerId, newUserId) {
  const referrals = loadReferrals();
  const users = loadUsers();

  // Нельзя пригласить самого себя
  if (referrerId === newUserId) return { success: false, reason: 'self' };

  // Проверяем, не был ли этот пользователь уже приглашён
  if (referrals[newUserId]) return { success: false, reason: 'already_invited' };

  // Сохраняем рефералку
  referrals[newUserId] = {
    referrerId,
    invitedAt: new Date().toISOString(),
    bonusGiven: false,
  };
  saveReferrals(referrals);

  return { success: true, referrerId, newUserId };
}

/**
 * Начисляет бонус пригласившему, когда новый пользователь совершил целевое действие
 * (оплатил тариф или прошёл опросник)
 */
function giveReferralBonus(userId) {
  const referrals = loadReferrals();
  const users = loadUsers();

  // Проверяем, был ли этот пользователь кем-то приглашён
  const ref = referrals[userId];
  if (!ref || ref.bonusGiven) return { success: false, reason: 'no_bonus' };

  const referrerId = ref.referrerId;

  // Начисляем бонус пригласившему
  if (!users[referrerId]) return { success: false, reason: 'referrer_not_found' };

  // Даём +7 дней Премиум
  const now = Date.now();
  const bonusEnd = users[referrerId].premiumUntil 
    ? Math.max(users[referrerId].premiumUntil, now) + REFERRAL_BONUS_DAYS * 24 * 60 * 60 * 1000
    : now + REFERRAL_BONUS_DAYS * 24 * 60 * 60 * 1000;

  users[referrerId].premiumUntil = bonusEnd;
  users[referrerId].subscription = 'premium';
  users[referrerId].referralBonus = (users[referrerId].referralBonus || 0) + 1;

  // Отмечаем бонус как выданный
  ref.bonusGiven = true;
  ref.bonusGivenAt = new Date().toISOString();

  saveUsers(users);
  saveReferrals(referrals);

  return { 
    success: true, 
    referrerId, 
    bonusDays: REFERRAL_BONUS_DAYS,
    totalReferrals: users[referrerId].referralBonus,
  };
}

// ============================================================
// 3. ОБРАБОТЧИКИ ДЛЯ БОТА
// ============================================================

function createReferralHandlers(bot, config) {
  const botUsername = config.botUsername || 'SmartHelper579Bot';

  /**
   * Показать реферальную информацию
   */
  async function showReferralInfo(ctx) {
    const userId = ctx.from.id;
    const referrals = loadReferrals();
    const users = loadUsers();

    // Сколько человек привёл этот пользователь
    const myReferrals = Object.values(referrals).filter(r => r.referrerId === userId);
    const invitedCount = myReferrals.length;
    const bonusCount = myReferrals.filter(r => r.bonusGiven).length;

    const link = generateReferralLink(botUsername, userId);

    const msg = `
🤝 <b>Пригласи друга — получи Премиум бесплатно!</b>

Твоя реферальная ссылка:
<code>${link}</code>

📊 <b>Твоя статистика:</b>
• Приглашено: ${invitedCount} чел.
• Получено бонусов: ${bonusCount} × ${REFERRAL_BONUS_DAYS} дней
• Всего дней Премиум: ${bonusCount * REFERRAL_BONUS_DAYS}

🎁 <b>Как это работает:</b>
1️⃣ Отправь другу ссылку
2️⃣ Друг переходит и начинает пользоваться
3️⃣ Когда друг оплачивает тариф — ты получаешь +${REFERRAL_BONUS_DAYS} дней Премиум

👇 <b>Поделиться ссылкой:</b>
`.trim();

    await ctx.reply(msg, {
      parse_mode: 'HTML',
      ...Markup.inlineKeyboard([
        [Markup.button.url('📤 Отправить другу', `https://t.me/share/url?url=${encodeURIComponent(link)}&text=${encodeURIComponent('Попробуй SmartHelper — AI-помощник для соцсетей! 🚀')}`)],
        [Markup.button.callback('🔙 Назад', 'back_to_menu')],
      ]),
    });
  }

  return { showReferralInfo, generateReferralLink, processReferral, giveReferralBonus };
}

module.exports = {
  createReferralHandlers,
  generateReferralLink,
  processReferral,
  giveReferralBonus,
  REFERRAL_BONUS_DAYS,
};
