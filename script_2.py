# Створюю адмін панель (admin/server.js)

admin_server_js = '''
const express = require('express');
const path = require('path');
const sqlite3 = require('sqlite3').verbose();
const cors = require('cors');
const bodyParser = require('body-parser');
const fs = require('fs-extra');
require('dotenv').config();

const app = express();
const PORT = process.env.ADMIN_PORT || 3001;

// Middleware
app.use(cors());
app.use(bodyParser.json());
app.use(bodyParser.urlencoded({ extended: true }));
app.use('/static', express.static(path.join(__dirname, 'static')));

// База даних
const db = new sqlite3.Database('./database/cosmetology.db');

// Простий middleware для авторизації
const adminAuth = (req, res, next) => {
    const adminPassword = process.env.ADMIN_PASSWORD || 'admin2024';
    const authHeader = req.headers.authorization;
    
    if (!authHeader) {
        return res.status(401).json({ error: 'Необхідна авторизація' });
    }
    
    const token = authHeader.split(' ')[1];
    if (token !== Buffer.from(`admin:${adminPassword}`).toString('base64')) {
        return res.status(401).json({ error: 'Невірний пароль' });
    }
    
    next();
};

// Головна сторінка адмін панелі
app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, 'index.html'));
});

// Авторизація
app.post('/api/auth', (req, res) => {
    const { password } = req.body;
    const adminPassword = process.env.ADMIN_PASSWORD || 'admin2024';
    
    if (password === adminPassword) {
        const token = Buffer.from(`admin:${adminPassword}`).toString('base64');
        res.json({ success: true, token });
    } else {
        res.status(401).json({ success: false, error: 'Невірний пароль' });
    }
});

// Отримання статистики дашборду
app.get('/api/dashboard', adminAuth, (req, res) => {
    const queries = {
        totalUsers: 'SELECT COUNT(*) as count FROM users WHERE active = 1',
        totalAppointments: 'SELECT COUNT(*) as count FROM appointments',
        monthlyRevenue: `SELECT SUM(price) as revenue FROM appointments 
                        WHERE payment_status = 'paid' 
                        AND date LIKE '${new Date().getFullYear()}-${String(new Date().getMonth() + 1).padStart(2, '0')}%'`,
        activeSubscriptions: 'SELECT COUNT(*) as count FROM subscriptions WHERE active = 1',
        todayAppointments: `SELECT COUNT(*) as count FROM appointments 
                           WHERE date = '${new Date().toISOString().split('T')[0]}'`
    };
    
    Promise.all([
        new Promise(resolve => db.get(queries.totalUsers, (err, row) => resolve(row?.count || 0))),
        new Promise(resolve => db.get(queries.totalAppointments, (err, row) => resolve(row?.count || 0))),
        new Promise(resolve => db.get(queries.monthlyRevenue, (err, row) => resolve(row?.revenue || 0))),
        new Promise(resolve => db.get(queries.activeSubscriptions, (err, row) => resolve(row?.count || 0))),
        new Promise(resolve => db.get(queries.todayAppointments, (err, row) => resolve(row?.count || 0)))
    ]).then(results => {
        res.json({
            totalUsers: results[0],
            totalAppointments: results[1],
            monthlyRevenue: results[2],
            activeSubscriptions: results[3],
            todayAppointments: results[4]
        });
    });
});

// Отримання всіх записів
app.get('/api/appointments', adminAuth, (req, res) => {
    const query = `
        SELECT a.*, u.username, u.first_name, u.last_name 
        FROM appointments a
        JOIN users u ON a.user_id = u.id
        ORDER BY a.date DESC, a.time DESC
    `;
    
    db.all(query, (err, rows) => {
        if (err) {
            res.status(500).json({ error: err.message });
        } else {
            res.json(rows);
        }
    });
});

// Оновлення статусу запису
app.put('/api/appointments/:id', adminAuth, (req, res) => {
    const { id } = req.params;
    const { payment_status } = req.body;
    
    const query = 'UPDATE appointments SET payment_status = ? WHERE id = ?';
    db.run(query, [payment_status, id], function(err) {
        if (err) {
            res.status(500).json({ error: err.message });
        } else {
            res.json({ success: true, changes: this.changes });
        }
    });
});

// Видалення запису
app.delete('/api/appointments/:id', adminAuth, (req, res) => {
    const { id } = req.params;
    
    const query = 'DELETE FROM appointments WHERE id = ?';
    db.run(query, [id], function(err) {
        if (err) {
            res.status(500).json({ error: err.message });
        } else {
            res.json({ success: true, changes: this.changes });
        }
    });
});

// Отримання користувачів
app.get('/api/users', adminAuth, (req, res) => {
    const query = 'SELECT * FROM users WHERE active = 1 ORDER BY created_at DESC';
    
    db.all(query, (err, rows) => {
        if (err) {
            res.status(500).json({ error: err.message });
        } else {
            res.json(rows);
        }
    });
});

// Відправка розсилки
app.post('/api/broadcast', adminAuth, (req, res) => {
    const { message } = req.body;
    
    // Спочатку зберігаємо повідомлення в БД
    const insertQuery = 'INSERT INTO admin_messages (message) VALUES (?)';
    db.run(insertQuery, [message], function(err) {
        if (err) {
            res.status(500).json({ error: err.message });
        } else {
            // Отримуємо всіх активних користувачів
            const usersQuery = 'SELECT telegram_id FROM users WHERE active = 1';
            db.all(usersQuery, async (err, users) => {
                if (err) {
                    res.status(500).json({ error: err.message });
                } else {
                    // В реальному проекті тут буде логіка відправки через Telegram Bot API
                    console.log(`📢 Розсилка для ${users.length} користувачів: ${message}`);
                    res.json({ 
                        success: true, 
                        messageId: this.lastID,
                        recipientsCount: users.length 
                    });
                }
            });
        }
    });
});

// Управління робочим графіком
app.get('/api/schedule', adminAuth, (req, res) => {
    const { date, city } = req.query;
    const query = 'SELECT * FROM working_schedule WHERE date = ? AND city = ? ORDER BY time';
    
    db.all(query, [date, city], (err, rows) => {
        if (err) {
            res.status(500).json({ error: err.message });
        } else {
            res.json(rows);
        }
    });
});

app.post('/api/schedule', adminAuth, (req, res) => {
    const { date, city, time, available } = req.body;
    
    const query = `INSERT OR REPLACE INTO working_schedule (date, city, time, available) 
                  VALUES (?, ?, ?, ?)`;
    
    db.run(query, [date, city, time, available], function(err) {
        if (err) {
            res.status(500).json({ error: err.message });
        } else {
            res.json({ success: true, id: this.lastID });
        }
    });
});

// Отримання підписок
app.get('/api/subscriptions', adminAuth, (req, res) => {
    const query = `
        SELECT s.*, u.username, u.first_name, u.last_name 
        FROM subscriptions s
        JOIN users u ON s.user_id = u.id
        ORDER BY s.created_at DESC
    `;
    
    db.all(query, (err, rows) => {
        if (err) {
            res.status(500).json({ error: err.message });
        } else {
            res.json(rows);
        }
    });
});

// Статистика по місяцях
app.get('/api/stats/monthly', adminAuth, (req, res) => {
    const query = `
        SELECT 
            strftime('%Y-%m', date) as month,
            COUNT(*) as appointments,
            SUM(CASE WHEN payment_status = 'paid' THEN price ELSE 0 END) as revenue
        FROM appointments
        WHERE date >= date('now', '-12 months')
        GROUP BY strftime('%Y-%m', date)
        ORDER BY month
    `;
    
    db.all(query, (err, rows) => {
        if (err) {
            res.status(500).json({ error: err.message });
        } else {
            res.json(rows);
        }
    });
});

// Запуск сервера
app.listen(PORT, () => {
    console.log(`🔧 Адмін панель запущена на порту ${PORT}`);
    console.log(`🌐 http://localhost:${PORT}`);
    console.log(`🔑 Пароль за замовчуванням: admin2024`);
});
'''

# Зберігаємо файл
with open('admin_server.js', 'w', encoding='utf-8') as f:
    f.write(admin_server_js)

print("✅ admin/server.js створено")