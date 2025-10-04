# Створюю детальну інструкцію з встановлення

readme_content = '''# 🤖 Telegram Bot для Доктора Тихонської

## 📋 Опис проекту

Повнофункціональний Telegram бот для косметологічної практики з веб адмін-панеллю, системою бронювання, підписками та інтеграцією платежів.

## ✨ Основні можливості

### 🎯 Для клієнтів:
- 📅 Запис на консультації та процедури
- 💎 Підписка на приватний канал Beauty Insider
- 💳 Оплата через Portmone або готівкою
- 📍 Карти з локаціями клінік
- 📞 Контактна інформація та соціальні мережі

### 👩‍💼 Для адміністратора:
- 📊 Дашборд з статистикою
- 📋 Управління записами та підписками
- 👥 База користувачів
- 📢 Розсилка повідомлень
- 📅 Управління робочим графіком
- 💰 Звіти по доходах

## 🛠 Технічний стек

- **Backend:** Node.js + Express
- **Database:** SQLite3
- **Bot API:** node-telegram-bot-api
- **Admin Panel:** Bootstrap 5, Chart.js
- **Payment:** Portmone API
- **Task Scheduler:** node-cron

## 📁 Структура проекту

```
dr-tykhonska-bot/
├── 📄 package.json          # Залежності проекту
├── 🤖 bot.js                # Головний файл бота
├── 🔧 database_init.js      # Ініціалізація БД
├── 📝 .env.example          # Приклад конфігурації
├── 📁 admin/
│   ├── 🌐 server.js         # Сервер адмін панелі
│   ├── 📄 index.html        # Інтерфейс адмін панелі
│   └── ⚡ admin.js          # JavaScript адмін панелі
├── 📁 database/
│   └── 🗃 cosmetology.db    # База даних (створюється автоматично)
└── 📁 assets/
    └── 📸 doctor-photo.jpg  # Фото доктора для привітання
```

---

# 🚀 ІНСТРУКЦІЯ З ВСТАНОВЛЕННЯ

## Крок 1: Підготовка VPS сервера

### 1.1 Підключення до VPS
```bash
ssh root@31.131.25.109
```

### 1.2 Оновлення системи
```bash
apt update && apt upgrade -y
```

### 1.3 Встановлення Node.js
```bash
# Встановлення Node.js 18.x
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
apt-get install -y nodejs

# Перевірка встановлення
node --version
npm --version
```

### 1.4 Встановлення додаткових пакетів
```bash
apt install -y git curl wget unzip nginx certbot python3-certbot-nginx
```

## Крок 2: Завантаження та налаштування проекту

### 2.1 Створення папки проекту
```bash
mkdir -p /var/www/dr-tykhonska-bot
cd /var/www/dr-tykhonska-bot
```

### 2.2 Завантаження файлів проекту
```bash
# Скопіюйте всі файли проекту на сервер
# Можна використовувати scp, rsync або git
```

### 2.3 Встановлення залежностей
```bash
npm install
```

### 2.4 Налаштування конфігурації
```bash
# Копіюємо приклад конфігурації
cp .env.example .env

# Редагуємо конфігурацію
nano .env
```

**Важливо:** Оновіть наступні параметри в `.env`:
- `PORTMONE_PAYEE_ID` - ваш ID в системі Portmone
- `PORTMONE_LOGIN` та `PORTMONE_PASSWORD` - дані для Portmone API
- `ADMIN_PASSWORD` - пароль для входу в адмін панель

## Крок 3: Ініціалізація бази даних

### 3.1 Створення БД
```bash
node database_init.js
```

Ви повинні побачити:
```
✅ Створено папку database/
✅ Створено 8 таблиць
✅ Додано 20 процедур та 14 налаштувань
✅ База даних успішно ініціалізована!
```

## Крок 4: Налаштування домену та SSL

### 4.1 Налаштування Nginx
```bash
nano /etc/nginx/sites-available/dr-tykhonska
```

Вставте конфігурацію:
```nginx
server {
    listen 80;
    server_name dr-tykhonska.com.ua www.dr-tykhonska.com.ua;

    # Бот API
    location /api {
        proxy_pass http://localhost:3001;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
    }

    # Адмін панель
    location / {
        proxy_pass http://localhost:3001;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }

    # Статичні файли
    location /static {
        alias /var/www/dr-tykhonska-bot/admin/static;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
```

### 4.2 Активація конфігурації
```bash
ln -s /etc/nginx/sites-available/dr-tykhonska /etc/nginx/sites-enabled/
nginx -t
systemctl reload nginx
```

### 4.3 Встановлення SSL сертифіката
```bash
certbot --nginx -d dr-tykhonska.com.ua -d www.dr-tykhonska.com.ua
```

## Крок 5: Створення systemd сервісів

### 5.1 Сервіс для основного бота
```bash
nano /etc/systemd/system/dr-tykhonska-bot.service
```

```ini
[Unit]
Description=Dr Tykhonska Telegram Bot
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/var/www/dr-tykhonska-bot
Environment=NODE_ENV=production
ExecStart=/usr/bin/node bot.js
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### 5.2 Сервіс для адмін панелі
```bash
nano /etc/systemd/system/dr-tykhonska-admin.service
```

```ini
[Unit]
Description=Dr Tykhonska Admin Panel
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/var/www/dr-tykhonska-bot
Environment=NODE_ENV=production
ExecStart=/usr/bin/node admin/server.js
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### 5.3 Активація сервісів
```bash
systemctl daemon-reload
systemctl enable dr-tykhonska-bot
systemctl enable dr-tykhonska-admin
systemctl start dr-tykhonska-bot
systemctl start dr-tykhonska-admin
```

### 5.4 Перевірка статусу
```bash
systemctl status dr-tykhonska-bot
systemctl status dr-tykhonska-admin
```

## Крок 6: Налаштування автоматичного резервного копіювання

### 6.1 Створення скрипта бекапу
```bash
nano /var/www/dr-tykhonska-bot/backup.sh
```

```bash
#!/bin/bash
# Резервне копіювання бази даних

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/var/backups/dr-tykhonska"
DB_PATH="/var/www/dr-tykhonska-bot/database/cosmetology.db"

# Створення папки для бекапів
mkdir -p $BACKUP_DIR

# Створення бекапу
sqlite3 $DB_PATH ".backup $BACKUP_DIR/cosmetology_$DATE.db"

# Видалення старих бекапів (старше 30 днів)
find $BACKUP_DIR -name "cosmetology_*.db" -mtime +30 -delete

echo "Backup created: cosmetology_$DATE.db"
```

### 6.2 Надання прав на виконання
```bash
chmod +x /var/www/dr-tykhonska-bot/backup.sh
```

### 6.3 Додавання до cron (щоденно о 02:00)
```bash
crontab -e
```

Додайте рядок:
```
0 2 * * * /var/www/dr-tykhonska-bot/backup.sh >> /var/log/backup.log 2>&1
```

## Крок 7: Налаштування брандмауера

### 7.1 Відкриття необхідних портів
```bash
ufw allow ssh
ufw allow 80
ufw allow 443
ufw enable
```

## Крок 8: Перевірка роботи

### 8.1 Перевірка бота
- Відкрийте Telegram і знайдіть ваш бот
- Надішліть команду `/start`
- Перевірте всі пункти меню

### 8.2 Перевірка адмін панелі
- Відкрийте https://dr-tykhonska.com.ua
- Увійдіть з паролем з файлу `.env`
- Перевірте всі розділи панелі

### 8.3 Перевірка логів
```bash
# Логи бота
journalctl -u dr-tykhonska-bot -f

# Логи адмін панелі
journalctl -u dr-tykhonska-admin -f

# Логи Nginx
tail -f /var/log/nginx/access.log
tail -f /var/log/nginx/error.log
```

---

# 🔧 КОРИСНІ КОМАНДИ

## Управління сервісами
```bash
# Перезапуск бота
systemctl restart dr-tykhonska-bot

# Зупинка/запуск адмін панелі
systemctl stop dr-tykhonska-admin
systemctl start dr-tykhonska-admin

# Перегляд логів
journalctl -u dr-tykhonska-bot --since "1 hour ago"
```

## Оновлення коду
```bash
# Зупинка сервісів
systemctl stop dr-tykhonska-bot dr-tykhonska-admin

# Оновлення коду
cd /var/www/dr-tykhonska-bot
# ... оновлення файлів ...

# Перезапуск
systemctl start dr-tykhonska-bot dr-tykhonska-admin
```

## Резервне копіювання
```bash
# Ручний бекап БД
./backup.sh

# Відновлення з бекапу
cp /var/backups/dr-tykhonska/cosmetology_YYYYMMDD_HHMMSS.db ./database/cosmetology.db
systemctl restart dr-tykhonska-bot
```

---

# 🐛 ВИРІШЕННЯ ПРОБЛЕМ

## Проблема: Бот не відповідає
1. Перевірте статус сервісу: `systemctl status dr-tykhonska-bot`
2. Подивіться логи: `journalctl -u dr-tykhonska-bot -n 50`
3. Перевірте токен бота в `.env`
4. Перезапустіть сервіс: `systemctl restart dr-tykhonska-bot`

## Проблема: Не працює адмін панель
1. Перевірте порт 3001: `netstat -tlnp | grep 3001`
2. Перевірте конфігурацію Nginx: `nginx -t`
3. Подивіться логи: `journalctl -u dr-tykhonska-admin -n 50`

## Проблема: Не працють платежі
1. Перевірте налаштування Portmone в `.env`
2. Подивіться логи для помилок API
3. Перевірте SSL сертифікат

## Проблема: Помилки БД
1. Перевірте права доступу до файлу БД
2. Зробіть резервну копію і відновіть БД
3. Переініціалізуйте БД: `node database_init.js`

---

# 📞 КОНТАКТИ ДЛЯ ПІДТРИМКИ

- **Telegram:** @tykhonskaa
- **Instagram:** dr.tykhonskaa
- **Домен:** https://dr-tykhonska.com.ua
- **VPS IP:** 31.131.25.109

---

# ⚠️ ВАЖЛИВІ ПРИМІТКИ

1. **Безпека:** Змініть пароль адміністратора в `.env`
2. **Бекапи:** Регулярно створюйте резервні копії БД
3. **Оновлення:** Стежте за оновленнями залежностей
4. **Моніторинг:** Налаштуйте моніторинг сервісів
5. **SSL:** Оновлюйте SSL сертифікати вчасно

Удачі з запуском бота! 🚀
'''

# Зберігаємо README
with open('README.md', 'w', encoding='utf-8') as f:
    f.write(readme_content)

print("✅ README.md створено з повними інструкціями")