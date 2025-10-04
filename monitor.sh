#!/bin/bash
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
