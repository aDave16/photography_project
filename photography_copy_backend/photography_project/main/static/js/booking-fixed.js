// Complete Booking System JavaScript
window.bookingApp = function() {
    return {
                // Navigation properties
                scrolled: false,
                mobileMenu: false,
                videoMuted: false,
                
                // Booking properties
                loading: false,
                showConfirmModal: false,
                currentDate: new Date(),
                currentMonth: new Date().getMonth(),
                currentYear: new Date().getFullYear(),
                currentMonthName: '',
                calendarData: {},
                selectedService: {},
                selectedDate: '',
                selectedTimeSlot: '',
                availableSlots: [],
                bookingForm: {
                    name: '',
                    email: '',
                    phone: '',
                    location: '',
                    message: ''
                },
                toast: {
                    show: false,
                    message: '',
                    type: 'success'
                },
                
                // Computed property
                get canSubmit() {
                    return this.selectedService.id && 
                           this.selectedDate && 
                           this.selectedTimeSlot &&
                           this.bookingForm.name &&
                           this.bookingForm.email;
                },
                
                // Initialization
                init() {
                    console.log('Booking app initializing...');
                    this.updateMonthName();
                    this.loadCalendarData();
                    
                    // Re-initialize Lucide icons after Alpine renders
                    this.$nextTick(() => {
                        if (typeof lucide !== 'undefined') {
                            lucide.createIcons();
                        }
                    });
                },
                
                // Service selection
                selectService(id, title, price) {
                    console.log('Selecting service:', id, title, price);
                    this.selectedService = { id, title, price };
                    
                    // Reset date and time when service changes
                    this.selectedDate = '';
                    this.selectedTimeSlot = '';
                    this.availableSlots = [];
                    
                    // Refresh calendar data for new service
                    this.loadCalendarData();
                    
                    // Update UI
                    this.$nextTick(() => {
                        this.updateServiceCards();
                        this.updateBookingSummary();
                    });
                },
                
                updateServiceCards() {
                    const cards = document.querySelectorAll('.service-card');
                    cards.forEach(card => {
                        const serviceId = card.dataset.serviceId;
                        if (serviceId == this.selectedService.id) {
                            card.classList.add('selected');
                        } else {
                            card.classList.remove('selected');
                        }
                    });
                },
                
                updateBookingSummary() {
                    // Summary updates automatically via x-text bindings
                },
                
                // Calendar functions
                updateMonthName() {
                    const months = ['January', 'February', 'March', 'April', 'May', 'June',
                                  'July', 'August', 'September', 'October', 'November', 'December'];
                    this.currentMonthName = `${months[this.currentMonth]} ${this.currentYear}`;
                },
                
                previousMonth() {
                    this.currentMonth--;
                    if (this.currentMonth < 0) {
                        this.currentMonth = 11;
                        this.currentYear--;
                    }
                    this.updateMonthName();
                    this.renderCalendar();
                    this.loadCalendarData();
                },
                
                nextMonth() {
                    this.currentMonth++;
                    if (this.currentMonth > 11) {
                        this.currentMonth = 0;
                        this.currentYear++;
                    }
                    this.updateMonthName();
                    this.renderCalendar();
                    this.loadCalendarData();
                },
                
                renderCalendar() {
                    console.log('Rendering calendar for:', this.currentMonth, this.currentYear);
                    const firstDay = new Date(this.currentYear, this.currentMonth, 1).getDay();
                    const daysInMonth = new Date(this.currentYear, this.currentMonth + 1, 0).getDate();
                    const today = new Date();
                    
                    let html = '';
                    
                    // Empty cells for days before month starts
                    for (let i = 0; i < firstDay; i++) {
                        html += '<div></div>';
                    }
                    
                    // Days of month
                    for (let day = 1; day <= daysInMonth; day++) {
                        const dateStr = `${this.currentYear}-${String(this.currentMonth + 1).padStart(2, '0')}-${String(day).padStart(2, '0')}`;
                        const date = new Date(this.currentYear, this.currentMonth, day);
                        const isPast = date < today.setHours(0, 0, 0, 0);
                        const isToday = date.toDateString() === today.toDateString();
                        const isSelected = this.selectedDate === dateStr;
                        const calendarInfo = this.calendarData[dateStr];
                        const isBooked = calendarInfo && !calendarInfo.available;
                        
                        let classes = 'calendar-day p-3 rounded-lg border cursor-pointer text-center ';
                        
                        if (isPast) {
                            classes += 'disabled ';
                        } else if (isSelected) {
                            classes += 'selected ';
                        } else if (isBooked) {
                            classes += 'booked ';
                        } else {
                            classes += 'hover:border-gold/50 ';
                        }
                        
                        if (isToday) {
                            classes += 'font-bold text-gold ';
                        }
                        
                        html += `
                            <div class="${classes}" 
                                 data-date="${dateStr}"
                                 @click="selectDate('${dateStr}', ${isPast}, ${isBooked})">
                                <div>${day}</div>
                                ${isBooked ? '<div class="text-xs text-red-400">Full</div>' : ''}
                            </div>
                        `;
                    }
                    
                    const calendarGrid = document.getElementById('calendar-grid');
                    if (calendarGrid) {
                        calendarGrid.innerHTML = html;
                    }
                },
                
                async loadCalendarData() {
                    try {
                        console.log('Loading calendar data for:', this.currentYear, this.currentMonth + 1);
                        const response = await fetch(`/api/calendar/?year=${this.currentYear}&month=${this.currentMonth + 1}`);
                        const data = await response.json();
                        this.calendarData = data.calendar_data || {};
                        this.renderCalendar();
                    } catch (error) {
                        console.error('Error loading calendar data:', error);
                        this.showToast('Error loading calendar data', 'error');
                    }
                },
                
                selectDate(dateStr, isPast, isBooked) {
                    console.log('Selecting date:', dateStr, 'isPast:', isPast, 'isBooked:', isBooked);
                    if (isPast || isBooked) return;
                    
                    this.selectedDate = dateStr;
                    this.selectedTimeSlot = '';
                    this.loadAvailableSlots();
                    this.renderCalendar();
                },
                
                async loadAvailableSlots() {
                    if (!this.selectedDate || !this.selectedService.id) return;
                    
                    try {
                        this.loading = true;
                        console.log('Loading available slots for:', this.selectedDate, this.selectedService.id);
                        const response = await fetch(`/api/available-slots/?date=${this.selectedDate}&service_id=${this.selectedService.id}`);
                        const data = await response.json();
                        
                        if (data.error) {
                            this.showToast(data.error, 'error');
                            return;
                        }
                        
                        this.availableSlots = data.available_slots || [];
                        this.renderTimeSlots();
                    } catch (error) {
                        console.error('Error loading available slots:', error);
                        this.showToast('Error loading available time slots', 'error');
                    } finally {
                        this.loading = false;
                    }
                },
                
                renderTimeSlots() {
                    const allSlots = [
                        '09:00 AM', '10:00 AM', '11:00 AM', '12:00 PM',
                        '01:00 PM', '02:00 PM', '03:00 PM', '04:00 PM', '05:00 PM'
                    ];
                    
                    let html = '';
                    allSlots.forEach(slot => {
                        // If availableSlots is empty (no bookings), all slots are available
                        const isAvailable = this.availableSlots.length === 0 || this.availableSlots.includes(slot);
                        const isSelected = this.selectedTimeSlot === slot;
                        
                        let classes = 'time-slot p-3 rounded-lg border text-center cursor-pointer ';
                        
                        if (!isAvailable) {
                            classes += 'disabled ';
                        } else if (isSelected) {
                            classes += 'selected ';
                        } else {
                            classes += 'hover:border-gold/50 ';
                        }
                        
                        html += `
                            <div class="${classes}" 
                                 @click="selectTimeSlot('${slot}', ${isAvailable})">
                                ${slot}
                            </div>
                        `;
                    });
                    
                    const timeSlotsContainer = document.getElementById('time-slots');
                    if (timeSlotsContainer) {
                        timeSlotsContainer.innerHTML = html;
                    }
                },
                
                selectTimeSlot(slot, isAvailable) {
                    console.log('Selecting time slot:', slot, 'available:', isAvailable);
                    if (!isAvailable) return;
                    this.selectedTimeSlot = slot;
                    this.renderTimeSlots();
                },
                
                // Booking submission
                async submitBooking() {
                    if (!this.canSubmit) {
                        this.showToast('Please fill all required fields', 'error');
                        return;
                    }
                    
                    this.showConfirmModal = true;
                },
                
                async confirmBooking() {
                    this.showConfirmModal = false;
                    this.loading = true;
                    
                    try {
                        const response = await fetch('/api/create-booking/', {
                            method: 'POST',
                            headers: {
                                'Content-Type': 'application/json',
                                'X-CSRFToken': this.getCsrfToken()
                            },
                            body: JSON.stringify({
                                name: this.bookingForm.name,
                                email: this.bookingForm.email,
                                phone: this.bookingForm.phone,
                                service_id: this.selectedService.id,
                                event_date: this.selectedDate,
                                time_slot: this.selectedTimeSlot,
                                location: this.bookingForm.location,
                                message: this.bookingForm.message
                            })
                        });
                        
                        const data = await response.json();
                        
                        if (data.success) {
                            this.showToast('Booking confirmed successfully!', 'success');
                            setTimeout(() => {
                                window.location.href = '/booking/success/';
                            }, 2000);
                        } else {
                            this.showToast(data.error || 'Booking failed', 'error');
                        }
                    } catch (error) {
                        console.error('Error creating booking:', error);
                        this.showToast('Error creating booking', 'error');
                    } finally {
                        this.loading = false;
                    }
                },
                
                // Helper functions
                getCsrfToken() {
                    const cookie = document.cookie.split('; ').find(row => row.trim().startsWith('csrftoken='));
                    return cookie ? cookie.split('=')[1] : '';
                },
                
                showToast(message, type = 'success') {
                    console.log('Showing toast:', message, type);
                    this.toast = {
                        show: true,
                        message,
                        type
                    };
                    
                    setTimeout(() => {
                        this.toast.show = false;
                    }, 5000);
                },
                
                // Navigation methods
                toggleMenu() {
                    this.mobileMenu = !this.mobileMenu;
                },
                
                closeMenu() {
                    this.mobileMenu = false;
                },
                
                scrollToBooking() {
                    const bookingSection = document.getElementById('booking-section');
                    if (bookingSection) {
                        bookingSection.scrollIntoView({ behavior: 'smooth' });
                    }
                }
            };
        });
    }
});
