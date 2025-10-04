#!/bin/bash
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
