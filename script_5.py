# Створюю скрипт ініціалізації БД

database_init_js = '''
const sqlite3 = require('sqlite3').verbose();
const fs = require('fs-extra');
const path = require('path');

// Створення папки для БД
const dbPath = './database';
if (!fs.existsSync(dbPath)) {
    fs.mkdirSync(dbPath, { recursive: true });
    console.log('✅ Створено папку database/');
}

// Ініціалізація БД
const db = new sqlite3.Database('./database/cosmetology.db');

console.log('🔄 Ініціалізація бази даних...');

// SQL запити для створення таблиць
const createTables = [
    // Таблиця користувачів
    `CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        telegram_id INTEGER UNIQUE NOT NULL,
        username TEXT,
        first_name TEXT,
        last_name TEXT,
        phone TEXT,
        email TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        active INTEGER DEFAULT 1,
        last_activity DATETIME DEFAULT CURRENT_TIMESTAMP
    )`,
    
    // Таблиця записів
    `CREATE TABLE IF NOT EXISTS appointments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        type TEXT NOT NULL, -- 'consultation', 'repeat_consultation', 'procedure'
        city TEXT NOT NULL,
        date TEXT NOT NULL,
        time TEXT NOT NULL,
        procedure_name TEXT,
        price INTEGER DEFAULT 0,
        payment_method TEXT, -- 'card', 'cash'
        payment_status TEXT DEFAULT 'pending', -- 'pending', 'paid', 'cancelled'
        notes TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )`,
    
    // Таблиця підписок
    `CREATE TABLE IF NOT EXISTS subscriptions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        subscription_type TEXT DEFAULT 'beauty_insider', -- 'beauty_insider'
        start_date DATE NOT NULL,
        end_date DATE NOT NULL,
        price INTEGER DEFAULT 300,
        payment_status TEXT DEFAULT 'pending',
        active INTEGER DEFAULT 1,
        reminder_sent INTEGER DEFAULT 0,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )`,
    
    // Таблиця робочого графіку
    `CREATE TABLE IF NOT EXISTS working_schedule (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT NOT NULL,
        city TEXT NOT NULL,
        time TEXT NOT NULL,
        available INTEGER DEFAULT 1, -- 1 - доступно, 0 - зайнято
        appointment_id INTEGER,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (appointment_id) REFERENCES appointments (id)
    )`,
    
    // Таблиця процедур
    `CREATE TABLE IF NOT EXISTS procedures (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        description TEXT,
        price INTEGER NOT NULL,
        duration INTEGER DEFAULT 60, -- тривалість в хвилинах
        cities TEXT NOT NULL, -- JSON масив міст
        active INTEGER DEFAULT 1,
        category TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )`,
    
    // Таблиця повідомлень для розсилки
    `CREATE TABLE IF NOT EXISTS admin_messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        message TEXT NOT NULL,
        message_type TEXT DEFAULT 'broadcast', -- 'broadcast', 'reminder', 'notification'
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        sent_to_users INTEGER DEFAULT 0,
        delivery_status TEXT DEFAULT 'pending' -- 'pending', 'sent', 'failed'
    )`,
    
    // Таблиця налаштувань бота
    `CREATE TABLE IF NOT EXISTS bot_settings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        setting_key TEXT UNIQUE NOT NULL,
        setting_value TEXT NOT NULL,
        description TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )`,
    
    // Таблиця платежів
    `CREATE TABLE IF NOT EXISTS payments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        appointment_id INTEGER,
        subscription_id INTEGER,
        amount INTEGER NOT NULL,
        currency TEXT DEFAULT 'UAH',
        payment_method TEXT, -- 'portmone', 'cash', 'bank_transfer'
        payment_id TEXT, -- ID платежу в платіжній системі
        status TEXT DEFAULT 'pending', -- 'pending', 'success', 'failed', 'cancelled'
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id),
        FOREIGN KEY (appointment_id) REFERENCES appointments (id),
        FOREIGN KEY (subscription_id) REFERENCES subscriptions (id)
    )`
];

// Створення таблиць
const createTablesPromise = () => {
    return new Promise((resolve, reject) => {
        let completed = 0;
        createTables.forEach((query, index) => {
            db.run(query, (err) => {
                if (err) {
                    console.error(`❌ Помилка створення таблиці ${index + 1}:`, err.message);
                    reject(err);
                } else {
                    completed++;
                    if (completed === createTables.length) {
                        console.log(`✅ Створено ${createTables.length} таблиць`);
                        resolve();
                    }
                }
            });
        });
    });
};

// Додавання початкових даних
const insertInitialData = () => {
    console.log('🔄 Додавання початкових даних...');
    
    // Процедури
    const procedures = [
        ['Чищення обличчя', 'Глибоке очищення пор, видалення комедонів', 800, 90, '["Дніпро", "Запоріжжя"]', 'Чищення'],
        ['Мезотерапія обличчя', 'Ін\'єкції вітамінних коктейлів для омолодження', 1200, 60, '["Дніпро", "Запоріжжя"]', 'Ін\'єкції'],
        ['Біоревіталізація', 'Глибоке зволоження шкіри гіалуроновою кислотою', 1500, 45, '["Дніпро", "Запоріжжя"]', 'Ін\'єкції'],
        ['Пілінг хімічний', 'Відновлення шкіри за допомогою кислот', 900, 75, '["Дніпро", "Запоріжжя"]', 'Пілінги'],
        ['Контурна пластика', 'Корекція об\'єму та контурів філерами', 2000, 60, '["Дніпро", "Запоріжжя"]', 'Ін\'єкції'],
        ['Ботулінотерапія', 'Розгладжування зморшок ботулотоксином', 1800, 30, '["Дніпро", "Запоріжжя"]', 'Ін\'єкції'],
        ['RF-ліфтинг', 'Безопераційна підтяжка радіочастотами', 1000, 90, '["Дніпро", "Запоріжжя"]', 'Апаратна косметологія'],
        ['Фотоомолодження', 'Відновлення шкіри світлом IPL', 1100, 60, '["Дніпро", "Запоріжжя"]', 'Апаратна косметологія'],
        ['Масаж обличчя', 'Розслаблюючий та омолоджуючий масаж', 600, 60, '["Дніпро", "Запоріжжя"]', 'Масаж'],
        ['Карбокситерапія', 'Терапія вуглекислим газом', 1300, 45, '["Дніпро", "Запоріжжя"]', 'Ін\'єкції'],
        ['SMAS-ліфтинг', 'Ультразвукова підтяжка HIFU', 2500, 120, '["Дніпро", "Запоріжжя"]', 'Апаратна косметологія'],
        ['Плазмотерапія', 'Омолодження власною плазмою крові', 1400, 90, '["Дніпро", "Запоріжжя"]', 'Ін\'єкції'],
        ['Мікронідлінг', 'Стимуляція регенерації мікроголками', 1100, 75, '["Дніпро", "Запоріжжя"]', 'Апаратна косметологія'],
        ['Ліполітики', 'Розщеплення жирових відкладень', 1600, 45, '["Дніпро", "Запоріжжя"]', 'Ін\'єкції'],
        ['Нитьовий ліфтинг', 'Підтяжка мезонитями', 3000, 90, '["Дніпро", "Запоріжжя"]', 'Ін\'єкції'],
        ['Лазерна шліфовка', 'Відновлення шкіри лазером', 2200, 60, '["Дніпро", "Запоріжжя"]', 'Лазерна косметологія'],
        ['Кріоліполіз', 'Заморожування жирових клітин', 1800, 120, '["Дніпро", "Запоріжжя"]', 'Апаратна косметологія'],
        ['Ультразвукова чистка', 'М\'яке очищення ультразвуком', 700, 60, '["Дніпро", "Запоріжжя"]', 'Чищення'],
        ['Вакуумна чистка', 'Глибоке очищення пор вакуумом', 650, 45, '["Дніпро", "Запоріжжя"]', 'Чищення'],
        ['Альгінатні маски', 'Зволожуючі та заспокійливі маски', 400, 30, '["Дніпро", "Запоріжжя"]', 'Догляд']
    ];
    
    const procedureQuery = `INSERT OR IGNORE INTO procedures 
                           (name, description, price, duration, cities, category) 
                           VALUES (?, ?, ?, ?, ?, ?)`;
    
    procedures.forEach(procedure => {
        db.run(procedureQuery, procedure, (err) => {
            if (err) console.error('Помилка додавання процедури:', err.message);
        });
    });
    
    // Налаштування бота
    const settings = [
        ['consultation_price', '500', 'Ціна консультації в грн'],
        ['repeat_consultation_price', '300', 'Ціна повторної консультації в грн'],
        ['subscription_price', '300', 'Ціна підписки Beauty Insider в грн'],
        ['subscription_duration', '30', 'Тривалість підписки в днях'],
        ['working_hours_start', '08:00', 'Початок робочого дня'],
        ['working_hours_end', '20:00', 'Кінець робочого дня'],
        ['appointment_duration', '30', 'Тривалість слоту запису в хвилинах'],
        ['reminder_days', '1', 'За скільки днів надсилати нагадування'],
        ['portmone_payee_id', 'YOUR_PAYEE_ID', 'ID в системі Portmone'],
        ['private_channel_url', 'https://t.me/+EYuNQljQHaNjYmI6', 'Посилання на приватний канал'],
        ['public_channel_url', 'https://t.me/dr_tykhonska', 'Посилання на публічний канал'],
        ['doctor_telegram', '@tykhonskaa', 'Telegram доктора'],
        ['doctor_instagram', 'dr.tykhonskaa', 'Instagram доктора'],
        ['doctor_tiktok', '@dr.tykhonska', 'TikTok доктора']
    ];
    
    const settingQuery = `INSERT OR IGNORE INTO bot_settings 
                         (setting_key, setting_value, description) 
                         VALUES (?, ?, ?)`;
    
    settings.forEach(setting => {
        db.run(settingQuery, setting, (err) => {
            if (err) console.error('Помилка додавання налаштування:', err.message);
        });
    });
    
    console.log(`✅ Додано ${procedures.length} процедур та ${settings.length} налаштувань`);
};

// Виконання ініціалізації
createTablesPromise()
    .then(() => {
        insertInitialData();
        console.log('✅ База даних успішно ініціалізована!');
        console.log('📁 Файл БД: ./database/cosmetology.db');
        db.close();
    })
    .catch((error) => {
        console.error('❌ Помилка ініціалізації БД:', error);
        db.close();
        process.exit(1);
    });
'''

# Створюю .env файл
env_content = '''# Telegram Bot Configuration
BOT_TOKEN=8464053440:AAGsYPF-TyVENUHBloOfVuHvq2ehuSpn-VY

# Server Configuration  
PORT=3000
ADMIN_PORT=3001
NODE_ENV=production

# Admin Panel
ADMIN_PASSWORD=admin2024

# Database
DATABASE_PATH=./database/cosmetology.db

# VPS Configuration
VPS_IP=31.131.25.109
DOMAIN=dr-tykhonska.com.ua

# Payment System (Portmone)
PORTMONE_PAYEE_ID=YOUR_PAYEE_ID
PORTMONE_LOGIN=YOUR_LOGIN
PORTMONE_PASSWORD=YOUR_PASSWORD

# Channels and Social Media
PRIVATE_CHANNEL_URL=https://t.me/+EYuNQljQHaNjYmI6
PUBLIC_CHANNEL_URL=https://t.me/dr_tykhonska
DOCTOR_TELEGRAM=@tykhonskaa
DOCTOR_INSTAGRAM=dr.tykhonskaa
DOCTOR_TIKTOK=@dr.tykhonska

# Business Settings
CONSULTATION_PRICE=500
SUBSCRIPTION_PRICE=300
WORKING_HOURS_START=08:00
WORKING_HOURS_END=20:00

# Locations
DNIPRO_ADDRESS=Проспект Олександра Поля 22
ZAPORIZHZHIA_ADDRESS=Перша ливарна 27а
DNIPRO_MAPS=https://maps.app.goo.gl/vauDWtxgUE4J4b8M6?g_st=ic
ZAPORIZHZHIA_MAPS=https://maps.app.goo.gl/nyoi4rQC54FQCP7F9?g_st=ic

# SSL Certificate (for production)
SSL_CERT_PATH=/etc/ssl/certs/dr-tykhonska.crt
SSL_KEY_PATH=/etc/ssl/private/dr-tykhonska.key
'''

# Зберігаємо файли
with open('database_init.js', 'w', encoding='utf-8') as f:
    f.write(database_init_js)

with open('.env.example', 'w', encoding='utf-8') as f:
    f.write(env_content)

print("✅ database/init.js створено")
print("✅ .env.example створено")