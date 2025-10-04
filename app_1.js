// Telegram Bot JavaScript - Dr. Tykhonska Cosmetology (Fixed Version)
class TelegramBot {
    constructor() {
        this.currentScreen = 'main-menu';
        this.bookingData = {};
        this.currentMonth = new Date().getMonth();
        this.currentYear = new Date().getFullYear();
        this.procedures = [
            { name: "Чищення обличчя", price: 800, city: ["Дніпро", "Запоріжжя"] },
            { name: "Мезотерапія", price: 1200, city: ["Дніпро", "Запоріжжя"] },
            { name: "Біоревіталізація", price: 1500, city: ["Дніпро", "Запоріжжя"] },
            { name: "Пілінг хімічний", price: 900, city: ["Дніпро", "Запоріжжя"] },
            { name: "Контурна пластика", price: 2000, city: ["Дніпро", "Запоріжжя"] },
            { name: "Ботулінотерапія", price: 1800, city: ["Дніпро", "Запоріжжя"] },
            { name: "RF-ліфтинг", price: 1000, city: ["Дніпро", "Запоріжжя"] },
            { name: "Фотоомолодження", price: 1100, city: ["Дніпро", "Запоріжжя"] },
            { name: "Масаж обличчя", price: 600, city: ["Дніпро", "Запоріжжя"] },
            { name: "Карбокситерапія", price: 1300, city: ["Дніпро", "Запоріжжя"] },
            { name: "SMAS-ліфтинг", price: 2500, city: ["Дніпро", "Запоріжжя"] },
            { name: "Плазмотерапія", price: 1400, city: ["Дніпро", "Запоріжжя"] },
            { name: "Мікронідлінг", price: 1100, city: ["Дніпро", "Запоріжжя"] },
            { name: "Ліполітики", price: 1600, city: ["Дніпро", "Запоріжжя"] },
            { name: "Нитьовий ліфтинг", price: 3000, city: ["Дніпро", "Запоріжжя"] },
            { name: "Лазерна шліфовка", price: 2200, city: ["Дніпро", "Запоріжжя"] },
            { name: "Кріоліполіз", price: 1800, city: ["Дніпро", "Запоріжжя"] },
            { name: "Ультразвукова чистка", price: 700, city: ["Дніпро", "Запоріжжя"] },
            { name: "Вакуумна чистка", price: 650, city: ["Дніпро", "Запоріжжя"] },
            { name: "Альгінатні маски", price: 400, city: ["Дніпро", "Запоріжжя"] }
        ];
        this.currentPage = 1;
        this.bookedSlots = this.generateBookedSlots();
        
        this.init();
    }

    init() {
        this.generateCalendar();
        this.generateTimeSlots();
        this.loadProcedures();
        console.log('🤖 Telegram Bot ініціалізовано!');
    }

    // Screen Navigation
    showScreen(screenId) {
        document.querySelectorAll('.screen').forEach(screen => {
            screen.classList.remove('active');
        });
        
        document.getElementById(screenId).classList.add('active');
        this.currentScreen = screenId;
        
        // Reset booking data when going to main menu
        if (screenId === 'main-menu') {
            this.bookingData = {};
            this.resetBookingFlow();
            this.resetProcedureFlow();
        }
    }

    // Generate random booked slots for demo
    generateBookedSlots() {
        const bookedSlots = new Set();
        const currentDate = new Date();
        
        // Generate some random booked slots for the next 30 days
        for (let i = 0; i < 15; i++) {
            const randomDay = Math.floor(Math.random() * 30) + 1;
            const randomHour = Math.floor(Math.random() * 12) + 8; // 8-20
            const randomMinute = Math.random() < 0.5 ? '00' : '30';
            const dateStr = `2025-10-${randomDay.toString().padStart(2, '0')}`;
            const timeStr = `${randomHour}:${randomMinute}`;
            bookedSlots.add(`${dateStr}_${timeStr}`);
        }
        
        return bookedSlots;
    }

    // Consultation Booking Flow
    selectConsultationType(type) {
        this.bookingData.consultationType = type;
        this.bookingData.price = type === 'first' ? 500 : 300;
        
        // Update UI
        document.querySelectorAll('#consultation-type .option-btn').forEach(btn => {
            btn.classList.remove('selected');
        });
        event.target.classList.add('selected');
        
        // Show next step after delay
        setTimeout(() => {
            document.getElementById('consultation-type').classList.add('hidden');
            document.getElementById('consultation-city').classList.remove('hidden');
        }, 500);
    }

    selectCity(city) {
        this.bookingData.city = city;
        
        // Update UI
        document.querySelectorAll('#consultation-city .option-btn').forEach(btn => {
            btn.classList.remove('selected');
        });
        event.target.classList.add('selected');
        
        // Show next step after delay
        setTimeout(() => {
            document.getElementById('consultation-city').classList.add('hidden');
            document.getElementById('consultation-date').classList.remove('hidden');
            this.generateCalendar();
        }, 500);
    }

    selectDate(day) {
        const selectedDate = `${this.currentYear}-${(this.currentMonth + 1).toString().padStart(2, '0')}-${day.toString().padStart(2, '0')}`;
        this.bookingData.date = selectedDate;
        
        // Update calendar UI
        document.querySelectorAll('#consultation-date .calendar-day').forEach(dayEl => {
            dayEl.classList.remove('selected');
        });
        event.target.classList.add('selected');
        
        // Generate time slots for selected date
        this.generateTimeSlots(selectedDate);
        
        // Show next step after delay
        setTimeout(() => {
            document.getElementById('consultation-date').classList.add('hidden');
            document.getElementById('consultation-time').classList.remove('hidden');
        }, 500);
    }

    selectTime(time) {
        this.bookingData.time = time;
        
        // Update UI
        document.querySelectorAll('#consultation-time .time-slot').forEach(slot => {
            slot.classList.remove('selected');
        });
        event.target.classList.add('selected');
        
        // Show next step after delay
        setTimeout(() => {
            document.getElementById('consultation-time').classList.add('hidden');
            document.getElementById('consultation-payment').classList.remove('hidden');
            
            // Hide cash option for online consultations
            if (this.bookingData.city === 'online') {
                document.getElementById('cash-payment').style.display = 'none';
            } else {
                document.getElementById('cash-payment').style.display = 'flex';
            }
        }, 500);
    }

    selectPayment(paymentType) {
        this.bookingData.payment = paymentType;
        
        // Update UI
        document.querySelectorAll('#consultation-payment .payment-btn').forEach(btn => {
            btn.classList.remove('selected');
        });
        event.target.classList.add('selected');
        
        // Show summary after delay
        setTimeout(() => {
            document.getElementById('consultation-payment').classList.add('hidden');
            this.showBookingSummary();
            document.getElementById('booking-summary').classList.remove('hidden');
        }, 500);
    }

    showBookingSummary() {
        const summaryDetails = document.getElementById('summary-details');
        const cityName = this.getCityName(this.bookingData.city);
        const consultationType = this.bookingData.consultationType === 'first' ? 'Перша консультація' : 'Повторна консультація';
        const paymentMethod = this.bookingData.payment === 'card' ? 'Картою (Portmone)' : 'Готівкою при прийомі';
        
        summaryDetails.innerHTML = `
            <div class="summary-item">
                <span class="summary-label">Тип:</span>
                <span class="summary-value">${consultationType}</span>
            </div>
            <div class="summary-item">
                <span class="summary-label">Місто:</span>
                <span class="summary-value">${cityName}</span>
            </div>
            <div class="summary-item">
                <span class="summary-label">Дата:</span>
                <span class="summary-value">${this.formatDate(this.bookingData.date)}</span>
            </div>
            <div class="summary-item">
                <span class="summary-label">Час:</span>
                <span class="summary-value">${this.bookingData.time}</span>
            </div>
            <div class="summary-item">
                <span class="summary-label">Оплата:</span>
                <span class="summary-value">${paymentMethod}</span>
            </div>
            <div class="summary-item">
                <span class="summary-label">Вартість:</span>
                <span class="summary-value">${this.bookingData.price} грн</span>
            </div>
        `;
    }

    confirmBooking() {
        // Simulate booking confirmation
        const successMessage = `
            <div class="success-message">
                ✅ Запис підтверджено!<br>
                Очікуйте повідомлення з деталями консультації.
                ${this.bookingData.payment === 'card' ? '<br>Переходимо до оплати...' : ''}
            </div>
        `;
        
        document.getElementById('booking-summary').innerHTML = successMessage;
        
        // Simulate payment redirect for card payments
        if (this.bookingData.payment === 'card') {
            setTimeout(() => {
                alert('🔄 Перенаправлення на Portmone для оплати...');
            }, 2000);
        }
        
        // Return to main menu after delay
        setTimeout(() => {
            this.showScreen('main-menu');
            this.resetBookingFlow();
        }, 4000);
    }

    resetBookingFlow() {
        // Reset all booking steps
        document.querySelectorAll('#consultation-booking .booking-step').forEach(step => {
            if (step.id !== 'consultation-type') {
                step.classList.add('hidden');
            } else {
                step.classList.remove('hidden');
            }
        });
        
        document.getElementById('booking-summary').classList.add('hidden');
        
        // Clear selections
        document.querySelectorAll('#consultation-booking .option-btn, #consultation-booking .time-slot, #consultation-booking .payment-btn').forEach(btn => {
            btn.classList.remove('selected');
        });
    }

    // Procedure Booking Flow
    selectProcedureCity(city) {
        this.bookingData.procedureCity = city;
        
        // Update UI
        document.querySelectorAll('#procedure-city .option-btn').forEach(btn => {
            btn.classList.remove('selected');
        });
        event.target.classList.add('selected');
        
        // Show procedures after delay
        setTimeout(() => {
            document.getElementById('procedure-city').classList.add('hidden');
            document.getElementById('procedure-selection').classList.remove('hidden');
            this.loadProcedures();
        }, 500);
    }

    loadProcedures() {
        const proceduresList = document.getElementById('procedures-list');
        const startIndex = (this.currentPage - 1) * 10;
        const endIndex = startIndex + 10;
        const proceduresForPage = this.procedures.slice(startIndex, endIndex);
        
        proceduresList.innerHTML = '';
        
        proceduresForPage.forEach((procedure, index) => {
            const procedureItem = document.createElement('div');
            procedureItem.className = 'procedure-item';
            procedureItem.onclick = () => this.selectProcedure(procedure);
            
            procedureItem.innerHTML = `
                <span class="procedure-name">${procedure.name}</span>
                <span class="procedure-price">${procedure.price} грн</span>
            `;
            
            proceduresList.appendChild(procedureItem);
        });
        
        // Update pagination
        document.querySelectorAll('.page-btn').forEach((btn, index) => {
            btn.classList.toggle('active', index + 1 === this.currentPage);
        });
    }

    changePage(page) {
        this.currentPage = page;
        this.loadProcedures();
    }

    selectProcedure(procedure) {
        this.bookingData.procedure = procedure;
        
        // Update UI - find the clicked element
        document.querySelectorAll('.procedure-item').forEach(item => {
            item.classList.remove('selected');
        });
        event.target.closest('.procedure-item').classList.add('selected');
        
        // Show date selection after delay
        setTimeout(() => {
            document.getElementById('procedure-selection').classList.add('hidden');
            document.getElementById('procedure-date').classList.remove('hidden');
            this.generateProcedureCalendar();
        }, 500);
    }

    selectProcedureDate(day) {
        const selectedDate = `${this.currentYear}-${(this.currentMonth + 1).toString().padStart(2, '0')}-${day.toString().padStart(2, '0')}`;
        this.bookingData.procedureDate = selectedDate;
        
        // Update calendar UI
        document.querySelectorAll('#procedure-date .calendar-day').forEach(dayEl => {
            dayEl.classList.remove('selected');
        });
        event.target.classList.add('selected');
        
        // Generate time slots for selected date
        this.generateProcedureTimeSlots(selectedDate);
        
        // Show next step after delay
        setTimeout(() => {
            document.getElementById('procedure-date').classList.add('hidden');
            document.getElementById('procedure-time').classList.remove('hidden');
        }, 500);
    }

    selectProcedureTime(time) {
        this.bookingData.procedureTime = time;
        
        // Update UI
        document.querySelectorAll('#procedure-time-slots .time-slot').forEach(slot => {
            slot.classList.remove('selected');
        });
        event.target.classList.add('selected');
        
        // Show payment options after delay
        setTimeout(() => {
            document.getElementById('procedure-time').classList.add('hidden');
            document.getElementById('procedure-payment').classList.remove('hidden');
        }, 500);
    }

    selectProcedurePayment(paymentType) {
        this.bookingData.procedurePayment = paymentType;
        
        // Update UI
        document.querySelectorAll('#procedure-payment .payment-btn').forEach(btn => {
            btn.classList.remove('selected');
        });
        event.target.classList.add('selected');
        
        // Show confirmation after delay
        setTimeout(() => {
            alert(`✅ Запис на процедуру "${this.bookingData.procedure.name}" підтверджено!\n📅 Дата: ${this.formatDate(this.bookingData.procedureDate)}\n⏰ Час: ${this.bookingData.procedureTime}\n💰 Вартість: ${this.bookingData.procedure.price} грн`);
            
            // Return to main menu
            this.showScreen('main-menu');
            this.resetProcedureFlow();
        }, 500);
    }

    resetProcedureFlow() {
        // Reset all procedure booking steps
        document.querySelectorAll('#procedure-booking .booking-step').forEach(step => {
            if (step.id !== 'procedure-city') {
                step.classList.add('hidden');
            } else {
                step.classList.remove('hidden');
            }
        });
        
        // Clear selections
        document.querySelectorAll('#procedure-booking .option-btn, #procedure-booking .time-slot, #procedure-booking .payment-btn, .procedure-item').forEach(btn => {
            btn.classList.remove('selected');
        });
        
        this.currentPage = 1;
        this.bookingData = {};
    }

    // Calendar Functions
    generateCalendar() {
        const calendarGrid = document.getElementById('calendar-grid');
        if (!calendarGrid) return;
        
        const monthNames = [
            'Січень', 'Лютий', 'Березень', 'Квітень', 'Травень', 'Червень',
            'Липень', 'Серпень', 'Вересень', 'Жовтень', 'Листопад', 'Грудень'
        ];
        
        const monthElement = document.querySelector('#consultation-date .calendar-month');
        if (monthElement) {
            monthElement.textContent = `${monthNames[this.currentMonth]} ${this.currentYear}`;
        }
        
        const firstDay = new Date(this.currentYear, this.currentMonth, 1).getDay();
        const daysInMonth = new Date(this.currentYear, this.currentMonth + 1, 0).getDate();
        const today = new Date();
        
        calendarGrid.innerHTML = '';
        
        // Add day headers
        const dayHeaders = ['Нд', 'Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб'];
        dayHeaders.forEach(header => {
            const headerEl = document.createElement('div');
            headerEl.textContent = header;
            headerEl.style.fontWeight = 'bold';
            headerEl.style.color = 'var(--color-bot-text)';
            calendarGrid.appendChild(headerEl);
        });
        
        // Add empty cells for days before month starts
        for (let i = 0; i < firstDay; i++) {
            const emptyDay = document.createElement('div');
            calendarGrid.appendChild(emptyDay);
        }
        
        // Add days of month
        for (let day = 1; day <= daysInMonth; day++) {
            const dayElement = document.createElement('div');
            dayElement.className = 'calendar-day';
            dayElement.textContent = day;
            
            const currentDate = new Date(this.currentYear, this.currentMonth, day);
            
            if (currentDate >= today) {
                dayElement.classList.add('available');
                dayElement.onclick = () => this.selectDate(day);
            } else {
                dayElement.classList.add('unavailable');
            }
            
            calendarGrid.appendChild(dayElement);
        }
    }

    generateProcedureCalendar() {
        const calendarGrid = document.getElementById('procedure-calendar-grid');
        if (!calendarGrid) return;
        
        const monthNames = [
            'Січень', 'Лютий', 'Березень', 'Квітень', 'Травень', 'Червень',
            'Липень', 'Серпень', 'Вересень', 'Жовтень', 'Листопад', 'Грудень'
        ];
        
        const monthElement = document.querySelector('#procedure-date .calendar-month');
        if (monthElement) {
            monthElement.textContent = `${monthNames[this.currentMonth]} ${this.currentYear}`;
        }
        
        const firstDay = new Date(this.currentYear, this.currentMonth, 1).getDay();
        const daysInMonth = new Date(this.currentYear, this.currentMonth + 1, 0).getDate();
        const today = new Date();
        
        calendarGrid.innerHTML = '';
        
        // Add day headers
        const dayHeaders = ['Нд', 'Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб'];
        dayHeaders.forEach(header => {
            const headerEl = document.createElement('div');
            headerEl.textContent = header;
            headerEl.style.fontWeight = 'bold';
            headerEl.style.color = 'var(--color-bot-text)';
            calendarGrid.appendChild(headerEl);
        });
        
        // Add empty cells for days before month starts
        for (let i = 0; i < firstDay; i++) {
            const emptyDay = document.createElement('div');
            calendarGrid.appendChild(emptyDay);
        }
        
        // Add days of month
        for (let day = 1; day <= daysInMonth; day++) {
            const dayElement = document.createElement('div');
            dayElement.className = 'calendar-day';
            dayElement.textContent = day;
            
            const currentDate = new Date(this.currentYear, this.currentMonth, day);
            
            if (currentDate >= today) {
                dayElement.classList.add('available');
                dayElement.onclick = () => this.selectProcedureDate(day);
            } else {
                dayElement.classList.add('unavailable');
            }
            
            calendarGrid.appendChild(dayElement);
        }
    }

    previousMonth() {
        this.currentMonth--;
        if (this.currentMonth < 0) {
            this.currentMonth = 11;
            this.currentYear--;
        }
        this.generateCalendar();
        this.generateProcedureCalendar();
    }

    nextMonth() {
        this.currentMonth++;
        if (this.currentMonth > 11) {
            this.currentMonth = 0;
            this.currentYear++;
        }
        this.generateCalendar();
        this.generateProcedureCalendar();
    }

    // Time Slots Functions
    generateTimeSlots(selectedDate = null) {
        const timeSlotsContainer = document.getElementById('time-slots');
        if (!timeSlotsContainer) return;
        
        timeSlotsContainer.innerHTML = '';
        
        const workingHours = [8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19];
        const minutes = ['00', '30'];
        
        workingHours.forEach(hour => {
            minutes.forEach(minute => {
                const timeSlot = document.createElement('div');
                timeSlot.className = 'time-slot';
                const timeString = `${hour}:${minute}`;
                timeSlot.textContent = timeString;
                
                // Check if slot is booked
                const slotKey = selectedDate ? `${selectedDate}_${timeString}` : `default_${timeString}`;
                if (this.bookedSlots.has(slotKey)) {
                    timeSlot.classList.add('booked');
                    timeSlot.textContent += ' 🚫';
                } else {
                    timeSlot.onclick = () => this.selectTime(timeString);
                }
                
                timeSlotsContainer.appendChild(timeSlot);
            });
        });
    }

    generateProcedureTimeSlots(selectedDate = null) {
        const timeSlotsContainer = document.getElementById('procedure-time-slots');
        if (!timeSlotsContainer) return;
        
        timeSlotsContainer.innerHTML = '';
        
        const workingHours = [8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19];
        const minutes = ['00', '30'];
        
        workingHours.forEach(hour => {
            minutes.forEach(minute => {
                const timeSlot = document.createElement('div');
                timeSlot.className = 'time-slot';
                const timeString = `${hour}:${minute}`;
                timeSlot.textContent = timeString;
                
                // Check if slot is booked
                const slotKey = selectedDate ? `${selectedDate}_${timeString}` : `default_${timeString}`;
                if (this.bookedSlots.has(slotKey)) {
                    timeSlot.classList.add('booked');
                    timeSlot.textContent += ' 🚫';
                } else {
                    timeSlot.onclick = () => this.selectProcedureTime(timeString);
                }
                
                timeSlotsContainer.appendChild(timeSlot);
            });
        });
    }

    // Subscription Functions
    subscribeToPremium() {
        alert('💳 Перенаправлення на Portmone для оплати підписки...\n💰 Сума: 300 грн\n📅 Тривалість: 30 днів');
        
        // Simulate successful payment
        setTimeout(() => {
            const successMessage = `✅ Оплата успішна!\n\n🔗 Посилання на приватний канал:\nhttps://t.me/+EYuNQljQHaNjYmI6\n\n📱 Натисніть, щоб приєднатися\n\n⏰ Підписка активна 30 днів\n🔔 Нагадування про продовження надійде за 3 дні до закінчення`;
            
            alert(successMessage);
            
            // Open private channel link
            window.open('https://t.me/+EYuNQljQHaNjYmI6', '_blank');
            
            this.showScreen('main-menu');
        }, 2000);
    }

    // Community Functions
    joinCommunity() {
        window.open('https://t.me/dr_tykhonska', '_blank');
        setTimeout(() => {
            alert('📱 Дякуємо за приєднання до нашої спільноти!\n🌸 Слідкуйте за новинами та корисними порадами.');
        }, 1000);
    }

    // Contact Functions
    openContact(platform) {
        const contacts = {
            telegram: 'https://t.me/tykhonskaa',
            instagram: 'https://instagram.com/dr.tykhonskaa',
            channel: 'https://t.me/dr_tykhonska',
            tiktok: 'https://tiktok.com/@dr.tykhonska'
        };
        
        if (contacts[platform]) {
            window.open(contacts[platform], '_blank');
        }
    }

    // Location Functions
    openMap(city) {
        const locations = {
            dnipro: 'https://maps.app.goo.gl/vauDWtxgUE4J4b8M6?g_st=ic',
            zaporizhzhya: 'https://maps.app.goo.gl/nyoi4rQC54FQCP7F9?g_st=ic'
        };
        
        if (locations[city]) {
            window.open(locations[city], '_blank');
        }
    }

    // Admin Panel Functions
    showAdminPanel() {
        // Create admin panel overlay
        const adminOverlay = document.createElement('div');
        adminOverlay.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.8);
            z-index: 10000;
            display: flex;
            justify-content: center;
            align-items: center;
        `;
        
        const adminPanel = document.createElement('div');
        adminPanel.style.cssText = `
            background: white;
            padding: 30px;
            border-radius: 15px;
            max-width: 500px;
            width: 90%;
            text-align: center;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
        `;
        
        adminPanel.innerHTML = `
            <h2 style="margin-bottom: 20px; color: var(--color-bot-text);">⚙️ Адмін Панель</h2>
            <div style="margin-bottom: 20px;">
                <h3 style="color: var(--color-bot-accent);">📊 Статистика</h3>
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px; margin: 15px 0;">
                    <div style="background: var(--color-bot-light-blue); padding: 15px; border-radius: 10px;">
                        <div style="font-size: 24px; font-weight: bold; color: var(--color-bot-accent);">23</div>
                        <div style="font-size: 14px;">Записи сьогодні</div>
                    </div>
                    <div style="background: var(--color-bot-light-blue); padding: 15px; border-radius: 10px;">
                        <div style="font-size: 24px; font-weight: bold; color: var(--color-bot-accent);">156</div>
                        <div style="font-size: 14px;">Записи місяць</div>
                    </div>
                    <div style="background: var(--color-bot-light-blue); padding: 15px; border-radius: 10px;">
                        <div style="font-size: 24px; font-weight: bold; color: var(--color-bot-accent);">12</div>
                        <div style="font-size: 14px;">Активні підписки</div>
                    </div>
                    <div style="background: var(--color-bot-light-blue); padding: 15px; border-radius: 10px;">
                        <div style="font-size: 24px; font-weight: bold; color: var(--color-bot-accent);">₴45,600</div>
                        <div style="font-size: 14px;">Дохід місяць</div>
                    </div>
                </div>
            </div>
            <div style="margin-bottom: 20px;">
                <h3 style="color: var(--color-bot-accent);">🛠️ Управління</h3>
                <div style="display: flex; flex-direction: column; gap: 10px;">
                    <button onclick="bot.manageBookings()" style="padding: 10px 20px; background: var(--color-bot-accent); color: white; border: none; border-radius: 8px; cursor: pointer;">📅 Управління записами</button>
                    <button onclick="bot.sendBroadcast()" style="padding: 10px 20px; background: var(--color-bot-accent); color: white; border: none; border-radius: 8px; cursor: pointer;">📢 Розсилка</button>
                    <button onclick="bot.manageSubscriptions()" style="padding: 10px 20px; background: var(--color-bot-accent); color: white; border: none; border-radius: 8px; cursor: pointer;">⭐ Підписки</button>
                </div>
            </div>
            <button onclick="this.parentElement.parentElement.remove()" style="padding: 10px 20px; background: var(--color-bot-text); color: white; border: none; border-radius: 8px; cursor: pointer;">❌ Закрити</button>
        `;
        
        adminOverlay.appendChild(adminPanel);
        document.body.appendChild(adminOverlay);
    }

    manageBookings() {
        alert('📅 Функція управління записами:\n\n• Перегляд всіх записів\n• Редагування часу роботи\n• Підтвердження оплат\n• Скасування записів\n\n🔧 В розробці...');
    }

    sendBroadcast() {
        const message = prompt('📢 Введіть повідомлення для розсилки:');
        if (message) {
            alert(`✅ Розсилка відправлена!\n📨 Повідомлення: "${message}"\n👥 Отримувачів: 1,247 користувачів`);
        }
    }

    manageSubscriptions() {
        alert('⭐ Управління підписками:\n\n📊 Активних: 12\n📉 Закінчуються: 3\n💰 Дохід місяць: ₴3,600\n\n🔧 Детальна панель в розробці...');
    }

    // Utility Functions
    getCityName(cityCode) {
        const cities = {
            online: 'Онлайн',
            dnipro: 'Дніпро',
            zaporizhzhya: 'Запоріжжя'
        };
        return cities[cityCode] || cityCode;
    }

    formatDate(dateString) {
        const date = new Date(dateString);
        const months = [
            'січня', 'лютого', 'березня', 'квітня', 'травня', 'червня',
            'липня', 'серпня', 'вересня', 'жовтня', 'листопада', 'грудня'
        ];
        
        return `${date.getDate()} ${months[date.getMonth()]} ${date.getFullYear()}`;
    }
}

// Global functions for HTML onclick events
function showScreen(screenId) {
    bot.showScreen(screenId);
}

function selectConsultationType(type) {
    bot.selectConsultationType(type);
}

function selectCity(city) {
    bot.selectCity(city);
}

function selectPayment(paymentType) {
    bot.selectPayment(paymentType);
}

function confirmBooking() {
    bot.confirmBooking();
}

function selectProcedureCity(city) {
    bot.selectProcedureCity(city);
}

function changePage(page) {
    bot.changePage(page);
}

function selectProcedurePayment(paymentType) {
    bot.selectProcedurePayment(paymentType);
}

function subscribeToPremium() {
    bot.subscribeToPremium();
}

function joinCommunity() {
    bot.joinCommunity();
}

function openContact(platform) {
    bot.openContact(platform);
}

function openMap(city) {
    bot.openMap(city);
}

function previousMonth() {
    bot.previousMonth();
}

function nextMonth() {
    bot.nextMonth();
}

function showAdminPanel() {
    bot.showAdminPanel();
}

// Initialize bot when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.bot = new TelegramBot();
    
    // Add some demo notifications
    setTimeout(() => {
        console.log('🔔 Демо-сповіщення: Новий запис на консультацію!');
    }, 3000);
    
    setTimeout(() => {
        console.log('💳 Демо-сповіщення: Оплата підписки отримана!');
    }, 6000);
});

// Add some CSS animations for better UX
const style = document.createElement('style');
style.textContent = `
    .screen {
        transition: opacity 0.3s ease-in-out;
    }
    
    .booking-step {
        transform: translateY(0);
        transition: all 0.3s ease-in-out;
    }
    
    .booking-step.hidden {
        opacity: 0;
        transform: translateY(-20px);
        pointer-events: none;
    }
    
    .menu-btn:active,
    .option-btn:active,
    .time-slot:active,
    .payment-btn:active,
    .procedure-item:active {
        transform: translateY(1px);
    }
    
    @keyframes pulse {
        0% { box-shadow: 0 0 0 0 rgba(33, 150, 243, 0.7); }
        70% { box-shadow: 0 0 0 10px rgba(33, 150, 243, 0); }
        100% { box-shadow: 0 0 0 0 rgba(33, 150, 243, 0); }
    }
    
    .selected {
        animation: pulse 1s;
    }
`;

document.head.appendChild(style);