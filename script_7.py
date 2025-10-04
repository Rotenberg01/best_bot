# Створюю остаточний package.json з усіма залежностями

package_json_content = '''{
    "name": "dr-tykhonska-bot",
    "version": "1.0.0",
    "description": "Telegram bot for Dr. Tykhonska cosmetology practice with admin panel",
    "main": "bot.js",
    "scripts": {
        "start": "node bot.js",
        "dev": "nodemon bot.js",
        "admin": "node admin/server.js",
        "setup": "node database_init.js",
        "backup": "./backup.sh",
        "test": "echo \\"No tests specified\\" && exit 0",
        "install-all": "npm install && npm run setup"
    },
    "dependencies": {
        "node-telegram-bot-api": "^0.64.0",
        "express": "^4.18.2",
        "sqlite3": "^5.1.6",
        "body-parser": "^1.20.2",
        "cors": "^2.8.5",
        "node-cron": "^3.0.3",
        "moment": "^2.29.4",
        "axios": "^1.6.0",
        "dotenv": "^16.3.1",
        "multer": "^1.4.5-lts.1",
        "path": "^0.12.7",
        "fs-extra": "^11.1.1",
        "helmet": "^7.1.0",
        "bcrypt": "^5.1.1",
        "jsonwebtoken": "^9.0.2",
        "uuid": "^9.0.1",
        "validator": "^13.11.0"
    },
    "devDependencies": {
        "nodemon": "^3.0.1",
        "eslint": "^8.56.0"
    },
    "engines": {
        "node": ">=16.0.0",
        "npm": ">=8.0.0"
    },
    "keywords": [
        "telegram",
        "bot",
        "cosmetology",
        "ukraine",
        "booking",
        "admin-panel",
        "portmone",
        "sqlite"
    ],
    "author": {
        "name": "Dr. Tykhonska",
        "email": "dr.tykhonska@gmail.com",
        "url": "https://dr-tykhonska.com.ua"
    },
    "license": "MIT",
    "repository": {
        "type": "git",
        "url": "https://github.com/dr-tykhonska/telegram-bot"
    },
    "bugs": {
        "url": "https://github.com/dr-tykhonska/telegram-bot/issues"
    },
    "homepage": "https://dr-tykhonska.com.ua"
}'''

# Створюю додатковий скрипт для швидкого деплою

deploy_script = '''#!/bin/bash
# Скрипт для швидкого деплою бота на VPS

set -e

echo "🚀 Початок деплою Dr. Tykhonska Bot..."

# Зупинка сервісів
echo "⏸️  Зупинка сервісів..."
sudo systemctl stop dr-tykhonska-bot dr-tykhonska-admin || true

# Створення бекапу
echo "💾 Створення бекапу..."
if [ -f "./database/cosmetology.db" ]; then
    cp ./database/cosmetology.db ./database/cosmetology_backup_$(date +%Y%m%d_%H%M%S).db
fi

# Встановлення залежностей
echo "📦 Встановлення залежностей..."
npm install

# Ініціалізація БД (якщо потрібно)
if [ ! -f "./database/cosmetology.db" ]; then
    echo "🗃️  Ініціалізація бази даних..."
    node database_init.js
fi

# Перевірка конфігурації
if [ ! -f ".env" ]; then
    echo "⚠️  Попередження: файл .env не знайдено. Копіюємо з .env.example"
    cp .env.example .env
    echo "❗ УВАГА: Відредагуйте файл .env з правильними налаштуваннями!"
fi

# Налаштування прав доступу
echo "🔒 Налаштування прав доступу..."
sudo chown -R www-data:www-data .
sudo chmod +x backup.sh

# Запуск сервісів
echo "▶️  Запуск сервісів..."
sudo systemctl start dr-tykhonska-bot
sudo systemctl start dr-tykhonska-admin

# Перевірка статусу
echo "📊 Перевірка статусу сервісів..."
sleep 3
sudo systemctl status dr-tykhonska-bot --no-pager
sudo systemctl status dr-tykhonska-admin --no-pager

echo "✅ Деплой завершено успішно!"
echo "🌐 Адмін панель: https://dr-tykhonska.com.ua"
echo "🤖 Бот готовий до роботи в Telegram"

# Показати порти
echo "📡 Активні порти:"
netstat -tlnp | grep -E ':(3000|3001)' || echo "Порти поки не активні"

echo ""
echo "📝 Корисні команди:"
echo "   sudo systemctl status dr-tykhonska-bot    # Статус бота"
echo "   sudo systemctl logs dr-tykhonska-bot      # Логи бота"
echo "   sudo systemctl restart dr-tykhonska-bot   # Перезапуск бота"
echo "   ./backup.sh                               # Ручний бекап"
echo ""
'''

# Скрипт для моніторингу системи

monitoring_script = '''#!/bin/bash
# Скрипт для моніторингу стану бота

echo "🔍 Моніторинг Dr. Tykhonska Bot"
echo "================================"

# Перевірка статусу сервісів
echo "📊 Статус сервісів:"
systemctl is-active dr-tykhonska-bot && echo "✅ Bot: активний" || echo "❌ Bot: неактивний"
systemctl is-active dr-tykhonska-admin && echo "✅ Admin: активний" || echo "❌ Admin: неактивний"
systemctl is-active nginx && echo "✅ Nginx: активний" || echo "❌ Nginx: неактивний"

echo ""

# Перевірка портів
echo "🌐 Мережеві порти:"
ss -tlnp | grep -E ':(80|443|3000|3001)' || echo "Порти недоступні"

echo ""

# Використання диска
echo "💾 Використання диску:"
df -h | grep -E '(/$|/var)'

echo ""

# Використання пам'яті
echo "🧠 Використання пам'яті:"
free -h

echo ""

# Процеси бота
echo "⚙️  Процеси бота:"
ps aux | grep -E '(bot\.js|server\.js)' | grep -v grep || echo "Процеси бота не знайдені"

echo ""

# Останні логи бота
echo "📋 Останні логи бота (5 рядків):"
journalctl -u dr-tykhonska-bot -n 5 --no-pager

echo ""

# Статистика БД
if [ -f "./database/cosmetology.db" ]; then
    echo "🗃️  Статистика БД:"
    sqlite3 ./database/cosmetology.db "SELECT 'Користувачі: ' || COUNT(*) FROM users;"
    sqlite3 ./database/cosmetology.db "SELECT 'Записи: ' || COUNT(*) FROM appointments;"
    sqlite3 ./database/cosmetology.db "SELECT 'Підписки: ' || COUNT(*) FROM subscriptions WHERE active = 1;"
else
    echo "❌ База даних не знайдена"
fi

echo ""
echo "✅ Моніторинг завершено"
'''

# Зберігаємо всі файли
with open('package.json', 'w', encoding='utf-8') as f:
    f.write(package_json_content)

with open('deploy.sh', 'w', encoding='utf-8') as f:
    f.write(deploy_script)
    
with open('monitor.sh', 'w', encoding='utf-8') as f:
    f.write(monitoring_script)

print("✅ package.json створено")
print("✅ deploy.sh створено (скрипт автоматичного деплою)")
print("✅ monitor.sh створено (скрипт моніторингу)")