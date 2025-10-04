import os
import json

# Создам структуру полного проекта Telegram бота для косметолога

# package.json
package_json = {
    "name": "dr-tykhonska-bot",
    "version": "1.0.0",
    "description": "Telegram bot for Dr. Tykhonska cosmetology practice",
    "main": "bot.js",
    "scripts": {
        "start": "node bot.js",
        "dev": "nodemon bot.js",
        "setup": "node setup/database.js",
        "admin": "node admin/server.js"
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
        "helmet": "^7.1.0"
    },
    "devDependencies": {
        "nodemon": "^3.0.1"
    },
    "engines": {
        "node": ">=16.0.0"
    },
    "keywords": [
        "telegram",
        "bot",
        "cosmetology",
        "ukraine",
        "booking"
    ],
    "author": "Dr. Tykhonska",
    "license": "MIT"
}

print("✅ package.json створено")