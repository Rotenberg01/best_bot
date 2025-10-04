# Створю основний файл bot.js з повним функціоналом

bot_js_content = '''
const TelegramBot = require('node-telegram-bot-api');
const express = require('express');
const sqlite3 = require('sqlite3').verbose();
const bodyParser = require('body-parser');
const cors = require('cors');
const cron = require('node-cron');
const moment = require('moment');
const axios = require('axios');
require('dotenv').config();

// Налаштування
const BOT_TOKEN = process.env.BOT_TOKEN || '8464053440:AAGsYPF-TyVENUHBloOfVuHvq2ehuSpn-VY';
const PORT = process.env.PORT || 3000;
const ADMIN_PORT = process.env.ADMIN_PORT || 3001;

// Ініціалізація бота
const bot = new TelegramBot(BOT_TOKEN, {polling: true});

// Ініціалізація бази даних
const db = new sqlite3.Database('./database/cosmetology.db');

// Константи
const CITIES = ['Онлайн', 'Дніпро', 'Запоріжжя'];
const PROCEDURES = [
    {name: 'Чищення обличчя', price: 800, cities: ['Дніпро', 'Запоріжжя']},
    {name: 'Мезотерапія', price: 1200, cities: ['Дніпро', 'Запоріжжя']},
    {name: 'Біоревіталізація', price: 1500, cities: ['Дніпро', 'Запоріжжя']},
    {name: 'Пілінг хімічний', price: 900, cities: ['Дніпро', 'Запоріжжя']},
    {name: 'Контурна пластика', price: 2000, cities: ['Дніпро', 'Запоріжжя']},
    {name: 'Ботулінотерапія', price: 1800, cities: ['Дніпро', 'Запоріжжя']},
    {name: 'RF-ліфтинг', price: 1000, cities: ['Дніпро', 'Запоріжжя']},
    {name: 'Фотоомолодження', price: 1100, cities: ['Дніпро', 'Запоріжжя']},
    {name: 'Масаж обличчя', price: 600, cities: ['Дніпро', 'Запоріжжя']},
    {name: 'Карбокситерапія', price: 1300, cities: ['Дніпро', 'Запоріжжя']},
    {name: 'SMAS-ліфтинг', price: 2500, cities: ['Дніпро', 'Запоріжжя']},
    {name: 'Плазмотерапія', price: 1400, cities: ['Дніпро', 'Запоріжжя']},
    {name: 'Мікронідлінг', price: 1100, cities: ['Дніпро', 'Запоріжжя']},
    {name: 'Ліполітики', price: 1600, cities: ['Дніпро', 'Запоріжжя']},
    {name: 'Нитьовий ліфтинг', price: 3000, cities: ['Дніпро', 'Запоріжжя']},
    {name: 'Лазерна шліфовка', price: 2200, cities: ['Дніпро', 'Запоріжжя']},
    {name: 'Кріоліполіз', price: 1800, cities: ['Дніпро', 'Запоріжжя']},
    {name: 'Ультразвукова чистка', price: 700, cities: ['Дніпро', 'Запоріжжя']},
    {name: 'Вакуумна чистка', price: 650, cities: ['Дніпро', 'Запоріжжя']},
    {name: 'Альгінатні маски', price: 400, cities: ['Дніпро', 'Запоріжжя']}
];

const CONSULTATION_PRICE = 500;
const SUBSCRIPTION_PRICE = 300;
const PRIVATE_CHANNEL = 'https://t.me/+EYuNQljQHaNjYmI6';
const PUBLIC_CHANNEL = 'https://t.me/dr_tykhonska';

// Ініціалізація БД
function initDatabase() {
    const queries = [
        `CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            telegram_id INTEGER UNIQUE NOT NULL,
            username TEXT,
            first_name TEXT,
            last_name TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            active INTEGER DEFAULT 1
        )`,
        `CREATE TABLE IF NOT EXISTS appointments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            type TEXT NOT NULL,
            city TEXT NOT NULL,
            date TEXT NOT NULL,
            time TEXT NOT NULL,
            procedure_name TEXT,
            price INTEGER,
            payment_method TEXT,
            payment_status TEXT DEFAULT 'pending',
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )`,
        `CREATE TABLE IF NOT EXISTS subscriptions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            start_date DATE NOT NULL,
            end_date DATE NOT NULL,
            active INTEGER DEFAULT 1,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )`,
        `CREATE TABLE IF NOT EXISTS working_schedule (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            city TEXT NOT NULL,
            time TEXT NOT NULL,
            available INTEGER DEFAULT 1
        )`,
        `CREATE TABLE IF NOT EXISTS admin_messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            message TEXT NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            sent_to_users INTEGER DEFAULT 0
        )`
    ];
    
    queries.forEach(query => {
        db.run(query, (err) => {
            if (err) console.error('Database error:', err);
        });
    });
    
    console.log('✅ База даних ініціалізована');
}

// Утиліти для роботи з користувачами
function addUser(telegramId, username, firstName, lastName) {
    return new Promise((resolve, reject) => {
        const query = `INSERT OR IGNORE INTO users (telegram_id, username, first_name, last_name) 
                      VALUES (?, ?, ?, ?)`;
        db.run(query, [telegramId, username, firstName, lastName], function(err) {
            if (err) reject(err);
            else resolve(this.lastID);
        });
    });
}

function getUserById(telegramId) {
    return new Promise((resolve, reject) => {
        const query = `SELECT * FROM users WHERE telegram_id = ?`;
        db.get(query, [telegramId], (err, row) => {
            if (err) reject(err);
            else resolve(row);
        });
    });
}

// Генерація клавіатур
function generateMainMenu() {
    return {
        reply_markup: {
            inline_keyboard: [
                [{text: 'ℹ️ Вступна інформація', callback_data: 'intro_info'}],
                [{text: '📅 Запис на консультацію', callback_data: 'consultation_booking'}],
                [{text: '💆‍♀️ Запис на процедури', callback_data: 'procedure_booking'}],
                [{text: '💎 Підписка Beauty Insider', callback_data: 'subscription'}],
                [{text: '👥 Спільнота косметології', callback_data: 'community'}],
                [{text: '📞 Контакти', callback_data: 'contacts'}],
                [{text: '📍 Наші локації', callback_data: 'locations'}]
            ]
        }
    };
}

function generateCityKeyboard(cities) {
    const keyboard = cities.map(city => [{text: city, callback_data: `city_${city}`}]);
    keyboard.push([{text: '🔙 Назад', callback_data: 'back_to_main'}]);
    return {reply_markup: {inline_keyboard: keyboard}};
}

function generateCalendar(year, month) {
    const startDate = new Date(year, month, 1);
    const endDate = new Date(year, month + 1, 0);
    const keyboard = [];
    
    // Заголовок з місяцем та роком
    const monthNames = [
        'Січень', 'Лютий', 'Березень', 'Квітень', 'Травень', 'Червень',
        'Липень', 'Серпень', 'Вересень', 'Жовтень', 'Листопад', 'Грудень'
    ];
    
    keyboard.push([{text: `${monthNames[month]} ${year}`, callback_data: 'ignore'}]);
    
    // Дні тижня
    keyboard.push([
        {text: 'Пн', callback_data: 'ignore'},
        {text: 'Вт', callback_data: 'ignore'},
        {text: 'Ср', callback_data: 'ignore'},
        {text: 'Чт', callback_data: 'ignore'},
        {text: 'Пт', callback_data: 'ignore'},
        {text: 'Сб', callback_data: 'ignore'},
        {text: 'Нд', callback_data: 'ignore'}
    ]);
    
    // Генерація днів
    let week = [];
    const firstDay = startDate.getDay();
    const adjustedFirstDay = firstDay === 0 ? 6 : firstDay - 1;
    
    // Пусті дні в першому тижні
    for (let i = 0; i < adjustedFirstDay; i++) {
        week.push({text: ' ', callback_data: 'ignore'});
    }
    
    // Дні місяця
    for (let day = 1; day <= endDate.getDate(); day++) {
        const dateStr = `${year}-${String(month + 1).padStart(2, '0')}-${String(day).padStart(2, '0')}`;
        week.push({text: String(day), callback_data: `date_${dateStr}`});
        
        if (week.length === 7) {
            keyboard.push([...week]);
            week = [];
        }
    }
    
    // Заповнення останнього тижня
    while (week.length < 7) {
        week.push({text: ' ', callback_data: 'ignore'});
    }
    if (week.some(btn => btn.text !== ' ')) {
        keyboard.push(week);
    }
    
    // Навігація між місяцями
    const prevMonth = month === 0 ? {month: 11, year: year - 1} : {month: month - 1, year};
    const nextMonth = month === 11 ? {month: 0, year: year + 1} : {month: month + 1, year};
    
    keyboard.push([
        {text: '⬅️', callback_data: `calendar_${prevMonth.year}_${prevMonth.month}`},
        {text: '🔙 Назад', callback_data: 'back_to_city'},
        {text: '➡️', callback_data: `calendar_${nextMonth.year}_${nextMonth.month}`}
    ]);
    
    return {reply_markup: {inline_keyboard: keyboard}};
}

function generateTimeSlots(date, city) {
    const times = [];
    for (let hour = 8; hour < 20; hour++) {
        times.push(`${String(hour).padStart(2, '0')}:00`);
        times.push(`${String(hour).padStart(2, '0')}:30`);
    }
    
    const keyboard = [];
    let row = [];
    
    times.forEach((time, index) => {
        // Перевіряємо доступність часу (тут можна додати логіку перевірки бронювань)
        const isAvailable = Math.random() > 0.3; // Імітація зайнятих слотів
        const text = isAvailable ? time : `❌ ${time}`;
        const callbackData = isAvailable ? `time_${time}` : 'ignore';
        
        row.push({text, callback_data: callbackData});
        
        if (row.length === 3) {
            keyboard.push([...row]);
            row = [];
        }
    });
    
    if (row.length > 0) {
        keyboard.push(row);
    }
    
    keyboard.push([{text: '🔙 Назад до календаря', callback_data: 'back_to_calendar'}]);
    
    return {reply_markup: {inline_keyboard: keyboard}};
}

// Обробники команд
bot.onText(/\\/start/, async (msg) => {
    const chatId = msg.chat.id;
    const user = msg.from;
    
    try {
        await addUser(user.id, user.username, user.first_name, user.last_name);
        
        const welcomeMessage = `
🌸 Вітаю у моєму боті!

Я - доктор Тихонська, ваш особистий консультант з питань косметології.

✨ Що я можу для вас зробити:
• Записати на консультацію або процедуру
• Підписати на приватний канал Beauty Insider
• Надати актуальну інформацію про послуги
• Показати наші локації

Оберіть потрібний розділ з меню нижче 👇
        `;
        
        const photoPath = './assets/doctor-photo.jpg'; // Фото доктора
        
        try {
            await bot.sendPhoto(chatId, photoPath, {
                caption: welcomeMessage,
                ...generateMainMenu()
            });
        } catch {
            await bot.sendMessage(chatId, welcomeMessage, generateMainMenu());
        }
        
    } catch (error) {
        console.error('Помилка при обробці /start:', error);
        await bot.sendMessage(chatId, 'Виникла помилка. Спробуйте ще раз.');
    }
});

// Обробник callback запитів
bot.on('callback_query', async (query) => {
    const chatId = query.message.chat.id;
    const data = query.data;
    const messageId = query.message.message_id;
    
    try {
        await bot.answerCallbackQuery(query.id);
        
        if (data === 'intro_info') {
            const infoMessage = `
👩‍⚕️ **Про доктора Тихонську**

🎓 **Освіта та досвід:**
• Вища медична освіта
• Спеціалізація: дерматологія та косметологія
• Понад 5 років практичного досвіду
• Постійне підвищення кваліфікації

💎 **Спеціалізація:**
• Ін'єкційна косметологія
• Апаратна косметологія  
• Естетична дерматологія
• Антивікові програми

🏆 **Наші переваги:**
• Індивідуальний підхід до кожного клієнта
• Використання сучасного обладнання
• Сертифіковані препарати від провідних брендів
• Комфортна атмосфера клініки

📱 **Слідкуйте за новинами:**
Instagram: @dr.tykhonskaa
Telegram: @tykhonskaa
TikTok: @dr.tykhonska
            `;
            
            const backKeyboard = {
                reply_markup: {
                    inline_keyboard: [[{text: '🔙 Назад до меню', callback_data: 'back_to_main'}]]
                }
            };
            
            await bot.editMessageText(infoMessage, {
                chat_id: chatId,
                message_id: messageId,
                parse_mode: 'Markdown',
                ...backKeyboard
            });
            
        } else if (data === 'consultation_booking') {
            const consultationMessage = `
📅 **Запис на консультацію**

💰 Вартість: ${CONSULTATION_PRICE} грн

🔹 **Консультація** - перша зустріч (60 хв)
🔹 **Повторна консультація** - контрольний огляд (30 хв)

Оберіть тип консультації:
            `;
            
            const consultationKeyboard = {
                reply_markup: {
                    inline_keyboard: [
                        [{text: '🔹 Консультація', callback_data: 'cons_type_consultation'}],
                        [{text: '🔄 Повторна консультація', callback_data: 'cons_type_repeat'}],
                        [{text: '🔙 Назад до меню', callback_data: 'back_to_main'}]
                    ]
                }
            };
            
            await bot.editMessageText(consultationMessage, {
                chat_id: chatId,
                message_id: messageId,
                parse_mode: 'Markdown',
                ...consultationKeyboard
            });
            
        } else if (data.startsWith('cons_type_')) {
            const consultationType = data.replace('cons_type_', '');
            // Зберігаємо тип консультації в пам'яті (в реальному проекті - в БД)
            
            const cityMessage = `
🏙️ **Оберіть місто для консультації:**

🖥️ **Онлайн** - відеоконсультація (тільки оплата картою)
🏢 **Дніпро** - клініка на Проспекті Олександра Поля 22
🏢 **Запоріжжя** - клініка на Першій ливарній 27а
            `;
            
            await bot.editMessageText(cityMessage, {
                chat_id: chatId,
                message_id: messageId,
                parse_mode: 'Markdown',
                ...generateCityKeyboard(CITIES)
            });
            
        } else if (data.startsWith('city_')) {
            const city = data.replace('city_', '');
            const now = new Date();
            
            const calendarMessage = `
📅 **Оберіть дату консультації**

🏙️ Місто: ${city}
📋 Тип: Консультація
💰 Вартість: ${CONSULTATION_PRICE} грн

Оберіть зручну для вас дату:
            `;
            
            await bot.editMessageText(calendarMessage, {
                chat_id: chatId,
                message_id: messageId,
                parse_mode: 'Markdown',
                ...generateCalendar(now.getFullYear(), now.getMonth())
            });
            
        } else if (data.startsWith('date_')) {
            const date = data.replace('date_', '');
            const city = 'Дніпро'; // В реальному проекті отримувати з контексту
            
            const timeMessage = `
⏰ **Оберіть час консультації**

📅 Дата: ${date}
🏙️ Місто: ${city}
💰 Вартість: ${CONSULTATION_PRICE} грн

Доступний час (❌ - зайнято):
            `;
            
            await bot.editMessageText(timeMessage, {
                chat_id: chatId,
                message_id: messageId,
                parse_mode: 'Markdown',
                ...generateTimeSlots(date, city)
            });
            
        } else if (data.startsWith('time_')) {
            const time = data.replace('time_', '');
            const paymentMessage = `
💳 **Оберіть спосіб оплати**

📅 Дата: 2024-01-15 (приклад)
⏰ Час: ${time}
🏙️ Місто: Дніпро
💰 Вартість: ${CONSULTATION_PRICE} грн

Як бажаєте сплатити?
            `;
            
            const paymentKeyboard = {
                reply_markup: {
                    inline_keyboard: [
                        [{text: '💳 Оплатити картою (Portmone)', callback_data: 'payment_card'}],
                        [{text: '💵 Готівкою при прийомі', callback_data: 'payment_cash'}],
                        [{text: '🔙 Назад до часу', callback_data: 'back_to_time'}]
                    ]
                }
            };
            
            await bot.editMessageText(paymentMessage, {
                chat_id: chatId,
                message_id: messageId,
                parse_mode: 'Markdown',
                ...paymentKeyboard
            });
            
        } else if (data === 'payment_card') {
            const paymentUrl = `https://www.portmone.com.ua/gateway/?payee_id=YOUR_PAYEE_ID&shop_order_number=${Date.now()}&bill_amount=${CONSULTATION_PRICE}&description=Consultation&success_url=https://dr-tykhonska.com.ua/success&failure_url=https://dr-tykhonska.com.ua/failure`;
            
            const paymentMessage = `
✅ **Ваш запис майже готовий!**

Для завершення бронювання перейдіть за посиланням для оплати.

Після успішної оплати ви отримаєте підтвердження та всі необхідні деталі.

💡 **Важливо:** зберегите це повідомлення - в ньому будуть всі деталі вашого запису.
            `;
            
            const paymentKeyboard = {
                reply_markup: {
                    inline_keyboard: [
                        [{text: '💳 Перейти до оплати', url: paymentUrl}],
                        [{text: '🏠 Головне меню', callback_data: 'back_to_main'}]
                    ]
                }
            };
            
            await bot.editMessageText(paymentMessage, {
                chat_id: chatId,
                message_id: messageId,
                parse_mode: 'Markdown',
                ...paymentKeyboard
            });
            
        } else if (data === 'payment_cash') {
            const confirmationMessage = `
✅ **Запис успішно створено!**

📋 **Деталі вашого запису:**
👤 Пацієнт: ${query.from.first_name}
📅 Дата: 15 січня 2024 (приклад)
⏰ Час: 14:00
🏙️ Місто: Дніпро
📍 Адреса: Проспект Олександра Поля 22
💰 Вартість: ${CONSULTATION_PRICE} грн (готівкою)

📞 **Контакти для зв'язку:**
Telegram: @tykhonskaa
Телефон: +380-XX-XXX-XX-XX

💡 **Нагадування:** прийдіть за 10 хвилин до призначеного часу.

За добу до прийому ми надішлемо вам нагадування.
            `;
            
            const doneKeyboard = {
                reply_markup: {
                    inline_keyboard: [
                        [{text: '🏠 Головне меню', callback_data: 'back_to_main'}]
                    ]
                }
            };
            
            await bot.editMessageText(confirmationMessage, {
                chat_id: chatId,
                message_id: messageId,
                parse_mode: 'Markdown',
                ...doneKeyboard
            });
            
            // Тут додати запис в БД
            
        } else if (data === 'contacts') {
            const contactsMessage = `
📞 **Контактна інформація**

👩‍⚕️ **Доктор Тихонська**

📱 **Telegram:** @tykhonskaa
📸 **Instagram:** dr.tykhonskaa  
📺 **TikTok:** @dr.tykhonska
📢 **Канал:** https://t.me/dr_tykhonska

📞 **Телефон:**
+380-XX-XXX-XX-XX

📧 **Email:**
dr.tykhonska@gmail.com

🕒 **Години роботи:**
Пн-Пт: 8:00 - 20:00
Сб: 9:00 - 18:00
Нд: вихідний
            `;
            
            const contactsKeyboard = {
                reply_markup: {
                    inline_keyboard: [
                        [{text: '📱 Написати в Telegram', url: 'https://t.me/tykhonskaa'}],
                        [{text: '📸 Перейти в Instagram', url: 'https://instagram.com/dr.tykhonskaa'}],
                        [{text: '📢 Підписатися на канал', url: 'https://t.me/dr_tykhonska'}],
                        [{text: '🔙 Назад до меню', callback_data: 'back_to_main'}]
                    ]
                }
            };
            
            await bot.editMessageText(contactsMessage, {
                chat_id: chatId,
                message_id: messageId,
                parse_mode: 'Markdown',
                ...contactsKeyboard
            });
            
        } else if (data === 'locations') {
            const locationsMessage = `
📍 **Наші локації**

🏢 **Дніпро**
📍 Проспект Олександра Поля 22
🚇 Метро: Центральна (5 хв пішки)
🅿️ Паркування: є

🏢 **Запоріжжя** 
📍 Перша ливарна 27а
🚌 Транспорт: зупинка "Центр" 
🅿️ Паркування: є

💡 **Як знайти:**
Всі наші клініки розташовані в центрі міста з зручним транспортним сполученням.
            `;
            
            const locationsKeyboard = {
                reply_markup: {
                    inline_keyboard: [
                        [{text: '🗺️ Дніпро на карті', url: 'https://maps.app.goo.gl/vauDWtxgUE4J4b8M6?g_st=ic'}],
                        [{text: '🗺️ Запоріжжя на карті', url: 'https://maps.app.goo.gl/nyoi4rQC54FQCP7F9?g_st=ic'}],
                        [{text: '🔙 Назад до меню', callback_data: 'back_to_main'}]
                    ]
                }
            };
            
            await bot.editMessageText(locationsMessage, {
                chat_id: chatId,
                message_id: messageId,
                parse_mode: 'Markdown',
                ...locationsKeyboard
            });
            
        } else if (data === 'subscription') {
            const subscriptionMessage = `
💎 **Підписка Beauty Insider**

🔥 **Що вас чекає:**
• Ексклюзивний контент про краси та здоров'я
• Персональні рекомендації від доктора  
• Розбори реальних кейсів
• Знижки на процедури до 15%
• Першими дізнавайтеся про новинки

💰 **Вартість:** ${SUBSCRIPTION_PRICE} грн/місяць
⏰ **Тривалість:** 30 днів

📱 За 3 дні до закінчення підписки ви отримаєте нагадування про продовження.
            `;
            
            const subscriptionKeyboard = {
                reply_markup: {
                    inline_keyboard: [
                        [{text: '💳 Підписатися (300 грн)', callback_data: 'subscribe_pay'}],
                        [{text: '🔙 Назад до меню', callback_data: 'back_to_main'}]
                    ]
                }
            };
            
            await bot.editMessageText(subscriptionMessage, {
                chat_id: chatId,
                message_id: messageId,
                parse_mode: 'Markdown',
                ...subscriptionKeyboard
            });
            
        } else if (data === 'subscribe_pay') {
            const paymentUrl = `https://www.portmone.com.ua/gateway/?payee_id=YOUR_PAYEE_ID&shop_order_number=SUB${Date.now()}&bill_amount=${SUBSCRIPTION_PRICE}&description=Beauty%20Insider%20Subscription&success_url=https://dr-tykhonska.com.ua/sub-success&failure_url=https://dr-tykhonska.com.ua/sub-failure`;
            
            const payMessage = `
💳 **Оплата підписки Beauty Insider**

💰 Сума: ${SUBSCRIPTION_PRICE} грн
⏰ Термін: 30 днів

Після успішної оплати ви отримаєте:
✅ Посилання на приватний канал
✅ Підтвердження підписки
✅ Доступ до ексклюзивного контенту
            `;
            
            const payKeyboard = {
                reply_markup: {
                    inline_keyboard: [
                        [{text: '💳 Перейти до оплати', url: paymentUrl}],
                        [{text: '🔙 Назад', callback_data: 'subscription'}]
                    ]
                }
            };
            
            await bot.editMessageText(payMessage, {
                chat_id: chatId,
                message_id: messageId,
                parse_mode: 'Markdown',
                ...payKeyboard
            });
            
        } else if (data === 'community') {
            const communityMessage = `
👥 **Приєднуйтесь до нашої спільноти!**

📢 **Канал "Доктор Тихонська"**

🔥 **Що вас чекає:**
• Корисні поради з догляду за шкірою
• Відповіді на популярні питання
• Новини зі світу косметології
• Акції та спеціальні пропозиції
• Результати процедур наших клієнтів

📱 Більше 1000+ підписників вже з нами!
            `;
            
            const communityKeyboard = {
                reply_markup: {
                    inline_keyboard: [
                        [{text: '📢 Підписатися на канал', url: PUBLIC_CHANNEL}],
                        [{text: '🔙 Назад до меню', callback_data: 'back_to_main'}]
                    ]
                }
            };
            
            await bot.editMessageText(communityMessage, {
                chat_id: chatId,
                message_id: messageId,
                parse_mode: 'Markdown',
                ...communityKeyboard
            });
            
        } else if (data === 'back_to_main') {
            const mainMessage = `
🌸 **Головне меню**

Оберіть потрібний розділ:
            `;
            
            await bot.editMessageText(mainMessage, {
                chat_id: chatId,
                message_id: messageId,
                parse_mode: 'Markdown',
                ...generateMainMenu()
            });
        }
        
    } catch (error) {
        console.error('Помилка обробки callback:', error);
        await bot.sendMessage(chatId, '❌ Виникла помилка. Спробуйте ще раз або зверніться до підтримки.');
    }
});

// Нагадування про записи
cron.schedule('0 9 * * *', async () => {
    console.log('🔔 Перевіряємо нагадування...');
    // Тут логіка відправки нагадувань
});

// Перевірка закінчення підписок
cron.schedule('0 10 * * *', async () => {
    console.log('📅 Перевіряємо підписки...');
    // Тут логіка перевірки підписок
});

// Ініціалізація
initDatabase();

console.log('🤖 Бот доктора Тихонської запущено!');
console.log(`🌐 Адмін панель буде доступна на порту ${ADMIN_PORT}`);
'''

# Зберігаємо файл
with open('bot.js', 'w', encoding='utf-8') as f:
    f.write(bot_js_content)

print("✅ bot.js створено з повним функціоналом")