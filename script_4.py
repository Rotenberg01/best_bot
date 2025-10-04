# Створюю JavaScript для адмін панелі

admin_js = '''
// Адмін панель JavaScript

class AdminPanel {
    constructor() {
        this.token = localStorage.getItem('adminToken');
        this.apiBase = '/api';
        this.currentSection = 'dashboard';
        
        if (this.token) {
            this.showMainInterface();
        } else {
            this.showLoginScreen();
        }
        
        this.initEventListeners();
        this.updateCurrentDate();
    }
    
    initEventListeners() {
        // Авторизація
        document.getElementById('loginForm')?.addEventListener('submit', (e) => {
            e.preventDefault();
            this.login();
        });
        
        // Навігація по секціях
        document.querySelectorAll('[data-section]').forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                const section = e.target.closest('[data-section]').dataset.section;
                this.showSection(section);
            });
        });
        
        // Розсилка
        document.getElementById('broadcastForm')?.addEventListener('submit', (e) => {
            e.preventDefault();
            this.sendBroadcast();
        });
    }
    
    async login() {
        const password = document.getElementById('password').value;
        const errorDiv = document.getElementById('loginError');
        
        try {
            const response = await fetch(`${this.apiBase}/auth`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ password })
            });
            
            const data = await response.json();
            
            if (data.success) {
                this.token = data.token;
                localStorage.setItem('adminToken', this.token);
                this.showMainInterface();
                this.loadDashboard();
            } else {
                errorDiv.textContent = data.error || 'Помилка авторизації';
                errorDiv.classList.remove('hidden');
            }
        } catch (error) {
            errorDiv.textContent = 'Помилка підключення до сервера';
            errorDiv.classList.remove('hidden');
        }
    }
    
    logout() {
        localStorage.removeItem('adminToken');
        this.token = null;
        this.showLoginScreen();
    }
    
    showLoginScreen() {
        document.getElementById('loginScreen').classList.remove('hidden');
        document.getElementById('mainInterface').classList.add('hidden');
    }
    
    showMainInterface() {
        document.getElementById('loginScreen').classList.add('hidden');
        document.getElementById('mainInterface').classList.remove('hidden');
        this.loadDashboard();
    }
    
    showSection(sectionName) {
        // Оновлення активного пункту меню
        document.querySelectorAll('.nav-link').forEach(link => {
            link.classList.remove('active');
        });
        document.querySelector(`[data-section="${sectionName}"]`).classList.add('active');
        
        // Приховування всіх секцій
        document.querySelectorAll('[id$="Section"]').forEach(section => {
            section.classList.add('hidden');
        });
        
        // Показ обраної секції
        document.getElementById(`${sectionName}Section`).classList.remove('hidden');
        
        // Оновлення заголовку
        const titles = {
            dashboard: 'Дашборд',
            appointments: 'Записи',
            users: 'Користувачі',
            subscriptions: 'Підписки',
            broadcast: 'Розсилка',
            schedule: 'Графік роботи'
        };
        
        const icons = {
            dashboard: 'fas fa-chart-line',
            appointments: 'fas fa-calendar-check',
            users: 'fas fa-users',
            subscriptions: 'fas fa-crown',
            broadcast: 'fas fa-bullhorn',
            schedule: 'fas fa-clock'
        };
        
        document.getElementById('sectionTitle').textContent = titles[sectionName];
        document.querySelector('#sectionTitle').previousElementSibling.className = `${icons[sectionName]} me-2 text-primary`;
        
        this.currentSection = sectionName;
        
        // Завантаження даних для секції
        this.loadSectionData(sectionName);
    }
    
    async loadSectionData(section) {
        switch (section) {
            case 'dashboard':
                await this.loadDashboard();
                break;
            case 'appointments':
                await this.loadAppointments();
                break;
            case 'users':
                await this.loadUsers();
                break;
            case 'subscriptions':
                await this.loadSubscriptions();
                break;
        }
    }
    
    async loadDashboard() {
        try {
            const response = await fetch(`${this.apiBase}/dashboard`, {
                headers: { 'Authorization': `Bearer ${this.token}` }
            });
            
            if (!response.ok) throw new Error('Помилка завантаження даних');
            
            const data = await response.json();
            this.renderDashboardStats(data);
            this.loadTodayAppointments();
            
        } catch (error) {
            console.error('Помилка завантаження дашборду:', error);
        }
    }
    
    renderDashboardStats(data) {
        const statsCards = document.getElementById('statsCards');
        
        const cards = [
            {
                title: 'Всього користувачів',
                value: data.totalUsers,
                icon: 'fas fa-users',
                color: 'primary'
            },
            {
                title: 'Всього записів',
                value: data.totalAppointments,
                icon: 'fas fa-calendar-check',
                color: 'success'
            },
            {
                title: 'Дохід за місяць',
                value: `${data.monthlyRevenue || 0} грн`,
                icon: 'fas fa-money-bill-wave',
                color: 'warning'
            },
            {
                title: 'Активні підписки',
                value: data.activeSubscriptions,
                icon: 'fas fa-crown',
                color: 'info'
            },
            {
                title: 'Записів сьогодні',
                value: data.todayAppointments,
                icon: 'fas fa-calendar-day',
                color: 'danger'
            }
        ];
        
        statsCards.innerHTML = cards.map(card => `
            <div class="col-md-4 col-lg-2">
                <div class="stat-card text-center">
                    <div class="stat-icon text-${card.color}">
                        <i class="${card.icon}"></i>
                    </div>
                    <h4 class="fw-bold">${card.value}</h4>
                    <p class="text-muted mb-0">${card.title}</p>
                </div>
            </div>
        `).join('');
    }
    
    async loadTodayAppointments() {
        try {
            const response = await fetch(`${this.apiBase}/appointments`, {
                headers: { 'Authorization': `Bearer ${this.token}` }
            });
            
            if (!response.ok) throw new Error('Помилка завантаження записів');
            
            const appointments = await response.json();
            const today = new Date().toISOString().split('T')[0];
            const todayAppointments = appointments.filter(app => app.date === today);
            
            const container = document.getElementById('todayAppointments');
            
            if (todayAppointments.length === 0) {
                container.innerHTML = `
                    <div class="text-center text-muted py-3">
                        <i class="fas fa-calendar-day fa-2x mb-2"></i>
                        <p>Немає записів на сьогодні</p>
                    </div>
                `;
                return;
            }
            
            container.innerHTML = `
                <div class="list-group">
                    ${todayAppointments.map(app => `
                        <div class="list-group-item d-flex justify-content-between align-items-center">
                            <div>
                                <h6 class="mb-1">${app.first_name} ${app.last_name || ''}</h6>
                                <small class="text-muted">${app.time} • ${app.city} • ${app.procedure_name || app.type}</small>
                            </div>
                            <span class="badge bg-${app.payment_status === 'paid' ? 'success' : 'warning'}">
                                ${app.payment_status === 'paid' ? 'Оплачено' : 'Очікує оплати'}
                            </span>
                        </div>
                    `).join('')}
                </div>
            `;
            
        } catch (error) {
            console.error('Помилка завантаження записів на сьогодні:', error);
        }
    }
    
    async loadAppointments() {
        try {
            const response = await fetch(`${this.apiBase}/appointments`, {
                headers: { 'Authorization': `Bearer ${this.token}` }
            });
            
            if (!response.ok) throw new Error('Помилка завантаження записів');
            
            const appointments = await response.json();
            this.renderAppointmentsTable(appointments);
            
        } catch (error) {
            console.error('Помилка завантаження записів:', error);
        }
    }
    
    renderAppointmentsTable(appointments) {
        const tbody = document.getElementById('appointmentsTable');
        
        if (appointments.length === 0) {
            tbody.innerHTML = `
                <tr>
                    <td colspan="9" class="text-center text-muted py-3">
                        <i class="fas fa-calendar-day fa-2x mb-2"></i>
                        <p>Записів не знайдено</p>
                    </td>
                </tr>
            `;
            return;
        }
        
        tbody.innerHTML = appointments.map(app => `
            <tr>
                <td>
                    <div>
                        <strong>${app.first_name} ${app.last_name || ''}</strong>
                        ${app.username ? `<br><small class="text-muted">@${app.username}</small>` : ''}
                    </div>
                </td>
                <td>
                    <span class="badge bg-primary">${app.type}</span>
                </td>
                <td>${app.city}</td>
                <td>${app.date}</td>
                <td>${app.time}</td>
                <td>${app.procedure_name || '-'}</td>
                <td>${app.price} грн</td>
                <td>
                    <span class="badge bg-${app.payment_status === 'paid' ? 'success' : app.payment_status === 'pending' ? 'warning' : 'secondary'}">
                        ${this.getPaymentStatusText(app.payment_status)}
                    </span>
                </td>
                <td>
                    <div class="btn-group btn-group-sm">
                        <button class="btn btn-outline-success" onclick="adminPanel.updatePaymentStatus(${app.id}, 'paid')" 
                                ${app.payment_status === 'paid' ? 'disabled' : ''}>
                            <i class="fas fa-check"></i>
                        </button>
                        <button class="btn btn-outline-danger" onclick="adminPanel.deleteAppointment(${app.id})">
                            <i class="fas fa-trash"></i>
                        </button>
                    </div>
                </td>
            </tr>
        `).join('');
    }
    
    getPaymentStatusText(status) {
        const statusMap = {
            'pending': 'Очікує оплати',
            'paid': 'Оплачено',
            'cash': 'Готівкою',
            'cancelled': 'Скасовано'
        };
        return statusMap[status] || status;
    }
    
    async updatePaymentStatus(appointmentId, status) {
        try {
            const response = await fetch(`${this.apiBase}/appointments/${appointmentId}`, {
                method: 'PUT',
                headers: {
                    'Authorization': `Bearer ${this.token}`,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ payment_status: status })
            });
            
            if (!response.ok) throw new Error('Помилка оновлення статусу');
            
            this.showNotification('Статус оплати оновлено', 'success');
            this.loadAppointments();
            
        } catch (error) {
            console.error('Помилка оновлення статусу оплати:', error);
            this.showNotification('Помилка оновлення статусу', 'error');
        }
    }
    
    async deleteAppointment(appointmentId) {
        if (!confirm('Ви впевнені, що хочете видалити цей запис?')) {
            return;
        }
        
        try {
            const response = await fetch(`${this.apiBase}/appointments/${appointmentId}`, {
                method: 'DELETE',
                headers: { 'Authorization': `Bearer ${this.token}` }
            });
            
            if (!response.ok) throw new Error('Помилка видалення запису');
            
            this.showNotification('Запис видалено', 'success');
            this.loadAppointments();
            
        } catch (error) {
            console.error('Помилка видалення запису:', error);
            this.showNotification('Помилка видалення запису', 'error');
        }
    }
    
    async loadUsers() {
        try {
            const response = await fetch(`${this.apiBase}/users`, {
                headers: { 'Authorization': `Bearer ${this.token}` }
            });
            
            if (!response.ok) throw new Error('Помилка завантаження користувачів');
            
            const users = await response.json();
            this.renderUsersTable(users);
            
        } catch (error) {
            console.error('Помилка завантаження користувачів:', error);
        }
    }
    
    renderUsersTable(users) {
        const tbody = document.getElementById('usersTable');
        
        if (users.length === 0) {
            tbody.innerHTML = `
                <tr>
                    <td colspan="5" class="text-center text-muted py-3">
                        <i class="fas fa-users fa-2x mb-2"></i>
                        <p>Користувачів не знайдено</p>
                    </td>
                </tr>
            `;
            return;
        }
        
        tbody.innerHTML = users.map(user => `
            <tr>
                <td>${user.telegram_id}</td>
                <td>${user.first_name} ${user.last_name || ''}</td>
                <td>
                    ${user.username ? `@${user.username}` : '-'}
                </td>
                <td>${new Date(user.created_at).toLocaleDateString('uk-UA')}</td>
                <td>
                    <span class="badge bg-${user.active ? 'success' : 'secondary'}">
                        ${user.active ? 'Активний' : 'Неактивний'}
                    </span>
                </td>
            </tr>
        `).join('');
    }
    
    async loadSubscriptions() {
        try {
            const response = await fetch(`${this.apiBase}/subscriptions`, {
                headers: { 'Authorization': `Bearer ${this.token}` }
            });
            
            if (!response.ok) throw new Error('Помилка завантаження підписок');
            
            const subscriptions = await response.json();
            this.renderSubscriptionsTable(subscriptions);
            
        } catch (error) {
            console.error('Помилка завантаження підписок:', error);
        }
    }
    
    renderSubscriptionsTable(subscriptions) {
        const tbody = document.getElementById('subscriptionsTable');
        
        if (subscriptions.length === 0) {
            tbody.innerHTML = `
                <tr>
                    <td colspan="5" class="text-center text-muted py-3">
                        <i class="fas fa-crown fa-2x mb-2"></i>
                        <p>Активних підписок не знайдено</p>
                    </td>
                </tr>
            `;
            return;
        }
        
        tbody.innerHTML = subscriptions.map(sub => {
            const daysLeft = Math.ceil((new Date(sub.end_date) - new Date()) / (1000 * 60 * 60 * 24));
            
            return `
                <tr>
                    <td>
                        <strong>${sub.first_name} ${sub.last_name || ''}</strong>
                        ${sub.username ? `<br><small class="text-muted">@${sub.username}</small>` : ''}
                    </td>
                    <td>${new Date(sub.start_date).toLocaleDateString('uk-UA')}</td>
                    <td>${new Date(sub.end_date).toLocaleDateString('uk-UA')}</td>
                    <td>
                        <span class="badge bg-${sub.active && daysLeft > 0 ? 'success' : 'warning'}">
                            ${sub.active && daysLeft > 0 ? 'Активна' : 'Закінчується'}
                        </span>
                    </td>
                    <td>
                        <span class="badge bg-${daysLeft > 7 ? 'success' : daysLeft > 0 ? 'warning' : 'danger'}">
                            ${daysLeft > 0 ? `${daysLeft} днів` : 'Закінчена'}
                        </span>
                    </td>
                </tr>
            `;
        }).join('');
    }
    
    async sendBroadcast() {
        const message = document.getElementById('broadcastMessage').value.trim();
        
        if (!message) {
            this.showNotification('Введіть текст повідомлення', 'error');
            return;
        }
        
        if (!confirm(`Відправити повідомлення всім користувачам?\\n\\n"${message}"`)) {
            return;
        }
        
        try {
            const response = await fetch(`${this.apiBase}/broadcast`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${this.token}`,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ message })
            });
            
            if (!response.ok) throw new Error('Помилка відправки розсилки');
            
            const data = await response.json();
            this.showNotification(`Повідомлення відправлено ${data.recipientsCount} користувачам`, 'success');
            document.getElementById('broadcastMessage').value = '';
            
        } catch (error) {
            console.error('Помилка відправки розсилки:', error);
            this.showNotification('Помилка відправки розсилки', 'error');
        }
    }
    
    showNotification(message, type = 'info') {
        // Створення та показ сповіщення
        const notification = document.createElement('div');
        notification.className = `alert alert-${type === 'error' ? 'danger' : type} alert-dismissible fade show position-fixed`;
        notification.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
        notification.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.remove();
        }, 5000);
    }
    
    updateCurrentDate() {
        const now = new Date();
        const options = {
            year: 'numeric',
            month: 'long',
            day: 'numeric',
            weekday: 'long'
        };
        document.getElementById('currentDate').textContent = 
            now.toLocaleDateString('uk-UA', options);
    }
    
    refreshAppointments() {
        this.loadAppointments();
    }
}

// Глобальні функції для викликів з HTML
function logout() {
    if (confirm('Ви впевнені, що хочете вийти?')) {
        adminPanel.logout();
    }
}

function refreshAppointments() {
    adminPanel.refreshAppointments();
}

function loadSchedule() {
    const date = document.getElementById('scheduleDate').value;
    const city = document.getElementById('scheduleCity').value;
    
    if (!date) {
        adminPanel.showNotification('Виберіть дату', 'error');
        return;
    }
    
    // Тут буде логіка завантаження графіку
    document.getElementById('scheduleGrid').innerHTML = `
        <div class="alert alert-info">
            <i class="fas fa-info-circle me-2"></i>
            Функція управління графіком буде реалізована в наступній версії.
            <br>Дата: ${date}, Місто: ${city}
        </div>
    `;
}

// Ініціалізація після завантаження DOM
document.addEventListener('DOMContentLoaded', () => {
    window.adminPanel = new AdminPanel();
});
'''

# Зберігаємо файл
with open('admin.js', 'w', encoding='utf-8') as f:
    f.write(admin_js)

print("✅ admin.js створено з повним функціоналом")