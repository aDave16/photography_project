/**
 * LUXE PHOTO | Premium Photography Advanced Features (Zero-Modification Integration)
 * High-performance, luxury-themed features injected at runtime.
 * Includes: Pricing Calculator, Smart Calendar, WhatsApp, Chat, and Invoice.
 */

(function () {
    // 1. DYNAMIC CSS INJECTION
    const style = document.createElement('style');
    style.textContent = `
        .feature-glass { background: rgba(10, 10, 10, 0.9); backdrop-filter: blur(25px); border: 1px solid rgba(212, 175, 55, 0.2); border-radius: 40px; box-shadow: 0 40px 100px rgba(0,0,0,0.5); max-height: 90vh; overflow-y: auto; }
        .feature-title { font-family: 'Playfair Display', serif; font-weight: 300; letter-spacing: 0.1em; color: #fff; }
        .cal-day { padding: 12px 0; text-align: center; border-radius: 12px; cursor: pointer; transition: 0.3s; font-size: 0.8rem; color: #fff; opacity: 0.7; }
        .cal-day:hover:not(.disabled) { background: rgba(212, 175, 55, 0.1); color: #D4AF37; opacity: 1; }
        .cal-day.active { background: #D4AF37; color: #000; font-weight: bold; opacity: 1; }
        .cal-day.disabled { opacity: 0.1; cursor: not-allowed; text-decoration: line-through; }
        .slot-pill { padding: 10px; border: 1px solid rgba(212, 175, 55, 0.2); border-radius: 12px; font-size: 10px; text-transform: uppercase; letter-spacing: 2px; color: #fff; cursor: pointer; transition: 0.3s; flex: 1; text-align: center; }
        .slot-pill.active { background: #D4AF37; color: #000; border-color: #D4AF37; }
        .pulse-wa { animation: waGlow 2s infinite; }
        @keyframes waGlow { 0% { box-shadow: 0 0 0 0 rgba(37, 211, 102, 0.7); } 70% { box-shadow: 0 0 0 15px rgba(37, 211, 102, 0); } 100% { box-shadow: 0 0 0 0 rgba(37, 211, 102, 0); } }
        
        /* Calendar Table Styles */
        .cal-header { 
            display: grid; 
            grid-template-columns: repeat(7, 1fr); 
            gap: 4px; 
            margin-bottom: 8px; 
            text-align: center;
        }
        .cal-header-day { 
            font-size: 0.65rem; 
            text-transform: uppercase; 
            letter-spacing: 1px; 
            color: rgba(212, 175, 55, 0.6); 
            padding: 4px 0;
            font-weight: 600;
        }
        .cal-grid-table { 
            display: grid; 
            grid-template-columns: repeat(7, 1fr); 
            gap: 4px; 
        }
        .cal-day { 
            aspect-ratio: 1; 
            display: flex; 
            align-items: center; 
            justify-content: center; 
            border-radius: 8px; 
            cursor: pointer; 
            transition: all 0.3s ease; 
            font-size: 0.85rem; 
            font-weight: 500;
            background: rgba(255,255,255,0.03);
            border: 1px solid transparent;
        }
        .cal-day:hover:not(.disabled):not(.active) { 
            background: rgba(212, 175, 55, 0.15); 
            border-color: rgba(212, 175, 55, 0.3);
            color: #D4AF37; 
        }
        .cal-day.active { 
            background: linear-gradient(135deg, #D4AF37 0%, #B8960C 100%); 
            color: #000; 
            font-weight: 700; 
            box-shadow: 0 4px 15px rgba(212, 175, 55, 0.4);
        }
        .cal-day.disabled { 
            opacity: 0.25; 
            cursor: not-allowed; 
            text-decoration: line-through;
            background: rgba(255,255,255,0.02);
        }
        .cal-day.today {
            border: 1px solid rgba(212, 175, 55, 0.5);
            color: #D4AF37;
        }
        .cal-day.other-month {
            opacity: 0.3;
            color: rgba(255,255,255,0.4);
        }
        
        /* Mobile Responsive Styles for Booking */
        @media (max-width: 768px) {
            #advanced-features-overlay { padding: 0.75rem !important; }
            .feature-glass { border-radius: 20px; padding: 1.25rem !important; max-height: 90vh; }
            .feature-glass .grid { grid-template-columns: 1fr !important; gap: 1.5rem !important; }
            .feature-title { font-size: 1.5rem !important; }
            .calendar-module { padding: 0 !important; }
            .cal-header { gap: 2px; }
            .cal-header-day { font-size: 0.6rem; padding: 2px 0; }
            .cal-grid-table { gap: 2px; }
            .cal-day { 
                font-size: 0.8rem; 
                border-radius: 6px;
                min-height: 36px;
            }
            .slot-pill { padding: 10px 6px; font-size: 10px; letter-spacing: 0.5px; }
            #cal-prev, #cal-next { padding: 8px; }
            #cal-month { font-size: 0.75rem !important; }
            #p-event, #p-hours, #f-client-name { font-size: 14px; padding: 12px !important; }
            #book-confirm-btn { padding: 16px !important; font-size: 12px; }
            #close-advanced { top: 0.75rem !important; right: 0.75rem !important; }
        }
    `;
    document.head.appendChild(style);

    // 1.5 INJECT PDF LIBRARY (html2pdf.js)
    const pdfScript = document.createElement('script');
    pdfScript.src = "https://cdnjs.cloudflare.com/ajax/libs/html2pdf.js/0.10.1/html2pdf.bundle.min.js";
    document.head.appendChild(pdfScript);

    // 1.5 CSRF HELPER for Django fetch requests
    const getCookie = (name) => {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    };

    // 1.6 In-memory booked dates (replaces localStorage f_booked)
    const bookedDates = [];

    // 2. WIDGET INJECTION (Pricing & Booking)
    // We add these to the body after a short delay to ensure DOM is ready.
    const init = () => {
        // Clear old WhatsApp config to ensure new number is used
        const storedConfig = localStorage.getItem('luxe_whatsapp_config');
        if (storedConfig) {
            const parsed = JSON.parse(storedConfig);
            if (parsed.number !== '919998001549') {
                localStorage.removeItem('luxe_whatsapp_config');
            }
        }

        const featureContainer = document.createElement('div');
        featureContainer.id = 'advanced-features-overlay';
        featureContainer.className = 'fixed inset-0 z-[2001] bg-dark/95 backdrop-blur-xl hidden items-center justify-center p-6';
        featureContainer.innerHTML = `
            <div class="feature-glass w-full max-w-4xl p-8 md:p-12 relative animate__animated animate__fadeInUp">
                <button id="close-advanced" class="absolute top-8 right-8 text-gold hover:scale-110 transition-transform"><i data-lucide="x-circle" class="w-8 h-8"></i></button>
                
                <div class="grid grid-cols-1 lg:grid-cols-2 gap-16">
                    <!-- Calculator Panel -->
                    <div class="space-y-10">
                        <h2 class="feature-title text-3xl">Artistic <span class="italic text-gold">Direction</span></h2>
                        <div class="space-y-6">
                            <div>
                                <label class="text-[10px] uppercase tracking-widest text-gold/60 block mb-2">Guest Name</label>
                                <input id="f-client-name" type="text" placeholder="E.g. Arnav Sharma" class="w-full bg-charcoal border border-gold/20 rounded-xl p-4 text-white outline-none focus:border-gold transition-colors">
                            </div>
                            <div>
                                <label class="text-[10px] uppercase tracking-widest text-gold/60 block mb-2">Service Selection</label>
                                <select id="p-event" class="w-full bg-charcoal border border-gold/20 rounded-xl p-4 text-white outline-none focus:border-gold transition-colors">
                                    <option value="wedding" data-price="150000">Wedding Cinematic (₹1.5L+)</option>
                                    <option value="prewedding" data-price="55000">Pre-Wedding Story (₹55k+)</option>
                                    <option value="commercial" data-price="40000">Commercial/Brand (₹40k+)</option>
                                    <option value="portrait" data-price="18000">Creative Portrait (₹18k+)</option>
                                </select>
                            </div>
                            <div>
                                <label class="text-[10px] uppercase tracking-widest text-gold/60 block mb-2">Duration (Hours)</label>
                                <input id="p-hours" type="number" value="4" min="1" class="w-full bg-charcoal border border-gold/20 rounded-xl p-4 text-white outline-none focus:border-gold transition-colors">
                            </div>
                        </div>
                    </div>

                    <!-- Booking Panel -->
                    <div class="space-y-10">
                        <h2 class="feature-title text-3xl">Secure <span class="italic text-gold">Date</span></h2>
                        <div class="calendar-module">
                            <div class="flex justify-between items-center mb-4 text-[10px] uppercase tracking-[0.2em] text-gold">
                                <button id="cal-prev" class="p-2 hover:bg-gold/20 rounded-full transition-all"><i data-lucide="chevron-left" class="w-5 h-5"></i></button>
                                <span id="cal-month" class="font-semibold tracking-wider">April 2026</span>
                                <button id="cal-next" class="p-2 hover:bg-gold/20 rounded-full transition-all"><i data-lucide="chevron-right" class="w-5 h-5"></i></button>
                            </div>
                            
                            <!-- Calendar Table Header -->
                            <div class="cal-header">
                                <div class="cal-header-day">Sun</div>
                                <div class="cal-header-day">Mon</div>
                                <div class="cal-header-day">Tue</div>
                                <div class="cal-header-day">Wed</div>
                                <div class="cal-header-day">Thu</div>
                                <div class="cal-header-day">Fri</div>
                                <div class="cal-header-day">Sat</div>
                            </div>
                            
                            <!-- Calendar Days Grid -->
                            <div class="cal-grid-table" id="cal-grid"></div>
                            
                            <div class="flex gap-2 mb-8 mt-6">
                                <div class="slot-pill active" data-slot="Morning">Morning</div>
                                <div class="slot-pill" data-slot="Afternoon">Afternoon</div>
                                <div class="slot-pill" data-slot="Evening">Evening</div>
                            </div>
                            <div id="p-total" class="hidden">₹1,50,000</div>
                            <button id="book-confirm-btn" class="w-full py-5 bg-gold text-dark font-black tracking-[0.3em] uppercase rounded-2xl hover:bg-white transition-all">
                                Confirm Booking
                            </button>
                            <div id="booking-success-msg" class="hidden text-center py-4">
                                <div class="text-green-400 text-sm font-medium mb-1">
                                    <i data-lucide="check-circle" class="w-5 h-5 inline-block mr-1"></i>
                                    Booking Confirmed
                                </div>
                                <p class="text-white/40 text-[10px] uppercase tracking-widest">Your session has been secured. Invoice ready below.</p>
                                <button id="view-invoice-btn" class="mt-4 px-6 py-2 bg-white/5 border border-white/10 text-gold text-[10px] uppercase tracking-widest rounded-xl hover:bg-gold hover:text-dark transition-all">
                                    View Invoice
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
        document.body.appendChild(featureContainer);

        // 3. LOGIC & HANDLERS
        lucide.createIcons();

        const overlay = document.getElementById('advanced-features-overlay');
        const closeBtn = document.getElementById('close-advanced');
        const pEvent = document.getElementById('p-event');
        const pHours = document.getElementById('p-hours');
        const pTotal = document.getElementById('p-total');
        const waBtn = document.getElementById('whatsapp-float');
        const chatInput = document.getElementById('chat-input');
        const sendBtn = document.getElementById('send-chat');

        const openModule = () => {
            overlay.classList.remove('hidden');
            overlay.classList.add('flex');
        };

        if (closeBtn && overlay) closeBtn.onclick = () => overlay.classList.add('hidden');

        // ================================================================
        // REAL AI CHATBOT — OpenAI-powered via Django backend
        // ================================================================
        const chatMessages = document.getElementById('chat-messages');
        let chatHistory = [];

        const appendMessage = (text, sender) => {
            if (!chatMessages) return;
            chatHistory.push({ role: sender, text: text });
            const div = document.createElement('div');
            div.className = sender === 'user'
                ? 'shrink-0 bg-gold/20 p-3 md:p-4 rounded-2xl rounded-br-none text-white/90 border border-gold/20 self-end ml-auto max-w-[85%] leading-relaxed shadow-sm'
                : 'shrink-0 bg-charcoal/80 p-3 md:p-4 rounded-2xl rounded-bl-none text-white/90 border border-white/5 self-start mr-auto max-w-[85%] leading-relaxed whitespace-pre-wrap shadow-sm text-left';

            if (sender === 'ai') {
                const escapeHTML = str => str.replace(/[&<>'"]/g, tag => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', "'": '&#39;', '"': '&quot;' }[tag] || tag));
                let escapedText = escapeHTML(text);
                let htmlFormat = escapedText
                    .replace(/\*\*(.*?)\*\*/g, '<strong class="text-gold">$1</strong>')
                    .replace(/\*(.*?)\*/g, '<em>$1</em>')
                    .replace(/\[(.*?)\]\((.*?)\)/g, '<a href="$2" class="text-gold underline" target="_blank">$1</a>');
                div.innerHTML = htmlFormat;
            } else {
                div.innerText = text;
            }

            chatMessages.appendChild(div);
            setTimeout(() => chatMessages.scrollTop = chatMessages.scrollHeight, 20);
        };

        const showTyping = () => {
            if (!chatMessages) return;
            const div = document.createElement('div');
            div.id = 'ai-typing';
            div.className = 'shrink-0 bg-charcoal/80 p-3 md:p-4 rounded-2xl rounded-bl-none text-white/50 border border-white/5 self-start mr-auto max-w-[85%] italic text-xs shadow-sm flex items-center gap-2';
            div.innerHTML = '<i data-lucide="loader-2" class="w-4 h-4 animate-spin text-gold"></i><span>LUXE AI is thinking...</span>';
            chatMessages.appendChild(div);
            if (window.lucide) lucide.createIcons({ root: div });
            setTimeout(() => chatMessages.scrollTop = chatMessages.scrollHeight, 20);
        };

        const removeTyping = () => {
            const typing = document.getElementById('ai-typing');
            if (typing) typing.remove();
        };

        const sendAiMessage = async () => {
            if (!chatInput) return;
            const message = chatInput.value.trim();
            if (!message) return;

            chatInput.disabled = true;
            if (sendBtn) {
                sendBtn.disabled = true;
                sendBtn.innerHTML = '<i data-lucide="loader-2" class="w-5 h-5 animate-spin"></i>';
                if (window.lucide) lucide.createIcons({ root: sendBtn });
            }

            // Show user message
            appendMessage(message, 'user');
            chatInput.value = '';

            // Show typing indicator
            showTyping();

            const resetState = () => {
                removeTyping();
                chatInput.disabled = false;
                if (sendBtn) {
                    sendBtn.disabled = false;
                    sendBtn.innerHTML = '<i data-lucide="send" class="w-5 h-5"></i>';
                    if (window.lucide) lucide.createIcons({ root: sendBtn });
                }
                setTimeout(() => chatInput.focus(), 10);
            };

            // Send to Django AI endpoint
            try {
                const payloadHistory = chatHistory.slice(0, -1).slice(-6);
                const csrfInput = document.querySelector('[name=csrfmiddlewaretoken]');
                const csrfToken = csrfInput ? csrfInput.value : '';
                const response = await fetch('/ai-chat/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': csrfToken
                    },
                    body: JSON.stringify({ message: message, history: payloadHistory })
                });

                resetState();

                if (!response.ok) {
                    appendMessage('Sorry, I am having trouble connecting right now. Please try again or contact us on WhatsApp.', 'ai');
                    return;
                }

                const data = await response.json();
                appendMessage(data.reply || 'I apologize, I did not understand that. Could you rephrase?', 'ai');

            } catch (err) {
                resetState();
                console.error('AI chat error:', err);
                appendMessage('Sorry, I am having trouble connecting right now. Please try again or contact us on WhatsApp.', 'ai');
            }

            // If user mentioned booking/pricing, also open the booking widget
            const lowerMsg = message.toLowerCase();
            if (lowerMsg.includes('book') || lowerMsg.includes('price') || lowerMsg.includes('cost') || lowerMsg.includes('date')) {
                setTimeout(openModule, 2500);
            }
        };

        sendBtn?.addEventListener('click', (e) => {

            e.preventDefault();

            sendAiMessage();

        });

        chatInput?.addEventListener('keypress', (e) => {

            if (e.key === 'Enter') {

                e.preventDefault();

                sendAiMessage();

            }

        });
        // Pricing Logic (Admin-Synchronized)
        const updatePricing = () => {
            const config = JSON.parse(localStorage.getItem('luxe_price_config') || '{"wedding":150000,"prewedding":55000,"commercial":40000,"portrait":18000,"hourly":7500,"travel":20000}');
            const waConfig = JSON.parse(localStorage.getItem('luxe_whatsapp_config') || '{"number":"919998001549","template":"Hi! I\'m inquiring about a {service} session. Est: {price}."}');

            const base = config[pEvent.value] || parseInt(pEvent.options[pEvent.selectedIndex].dataset.price);
            const hrs = parseInt(pHours.value) || 0;
            const extra = Math.max(0, hrs - 4) * (config.hourly || 7500);
            const total = base + extra;
            pTotal.innerText = `₹${total.toLocaleString()}`;

            if (waBtn) {
                const serviceName = pEvent.options[pEvent.selectedIndex].text.split('(')[0].trim();
                const msg = waConfig.template.replace('{service}', serviceName).replace('{price}', pTotal.innerText);
                waBtn.href = `https://wa.me/${waConfig.number}?text=${encodeURIComponent(msg)}`;
            }
        };
        if (pEvent) pEvent.onchange = updatePricing;
        if (pHours) pHours.oninput = updatePricing;
        updatePricing();

        // Calendar Logic (Admin-Synchronized)
        let cMonth = new Date().getMonth();
        let cYear = new Date().getFullYear();
        let selDate = null;
        let selSlot = "Morning";

        const calGrid = document.getElementById('cal-grid');
        const calMonth = document.getElementById('cal-month');

        const renderCal = () => {
            if (!calGrid) return;
            calGrid.innerHTML = '';

            const firstDayOfMonth = new Date(cYear, cMonth, 1).getDay();
            const daysInMonth = new Date(cYear, cMonth + 1, 0).getDate();
            const daysInPrevMonth = new Date(cYear, cMonth, 0).getDate();
            const booked = bookedDates;
            const today = new Date();
            const isCurrentMonth = today.getMonth() === cMonth && today.getFullYear() === cYear;

            // Update month header
            calMonth.innerText = `${new Intl.DateTimeFormat('en-US', { month: 'long' }).format(new Date(cYear, cMonth))} ${cYear}`;

            // Previous month days (for filling the first week)
            for (let i = firstDayOfMonth - 1; i >= 0; i--) {
                const dayNum = daysInPrevMonth - i;
                const div = document.createElement('div');
                div.innerText = dayNum;
                div.className = 'cal-day other-month';
                div.style.pointerEvents = 'none';
                calGrid.appendChild(div);
            }

            // Current month days
            for (let d = 1; d <= daysInMonth; d++) {
                const ds = `${cYear}-${String(cMonth + 1).padStart(2, '0')}-${String(d).padStart(2, '0')}`;
                const div = document.createElement('div');
                div.innerText = d;

                // Build class list
                let className = 'cal-day';

                // Check if today
                if (isCurrentMonth && today.getDate() === d) {
                    className += ' today';
                }

                // Check if booked
                if (booked.includes(ds)) {
                    className += ' disabled';
                    div.title = 'Already booked';
                } else {
                    // Check if selected
                    if (selDate === ds) {
                        className += ' active';
                    }

                    div.onclick = () => {
                        document.querySelectorAll('.cal-day').forEach(e => e.classList.remove('active'));
                        div.classList.add('active');
                        selDate = ds;
                    };
                }

                div.className = className;
                calGrid.appendChild(div);
            }

            // Next month days (to fill remaining grid cells - always show 6 rows)
            const totalCells = firstDayOfMonth + daysInMonth;
            const remainingCells = 42 - totalCells; // 6 rows × 7 columns = 42

            for (let d = 1; d <= remainingCells; d++) {
                const div = document.createElement('div');
                div.innerText = d;
                div.className = 'cal-day other-month';
                div.style.pointerEvents = 'none';
                calGrid.appendChild(div);
            }
        };

        const prev = document.getElementById('cal-prev');
        const next = document.getElementById('cal-next');
        if (prev) prev.onclick = () => { cMonth--; if (cMonth < 0) { cMonth = 11; cYear--; } renderCal(); };
        if (next) next.onclick = () => { cMonth++; if (cMonth > 11) { cMonth = 0; cYear++; } renderCal(); };
        renderCal();

        document.querySelectorAll('.slot-pill').forEach(pill => {
            pill.onclick = () => {
                document.querySelectorAll('.slot-pill').forEach(p => p.classList.remove('active'));
                pill.classList.add('active');
                selSlot = pill.dataset.slot;
            };
        });

        // Booking & Invoice (connected to Django backend)
        const confirmBtn = document.getElementById('book-confirm-btn');
        if (confirmBtn) confirmBtn.onclick = async () => {
            const nameEl = document.getElementById('f-client-name');
            const name = nameEl?.value || "Guest";
            if (!selDate) return alert("Please select a date from the calendar!");

            const serviceName = pEvent.options[pEvent.selectedIndex].text.split('(')[0].trim();
            const serviceType = pEvent.value;
            const invId = `INV-${Math.floor(1000 + Math.random() * 9000)}`;

            // 1. Send booking to Django backend
            try {
                const csrfInput = document.querySelector('[name=csrfmiddlewaretoken]');
                const csrfToken = csrfInput ? csrfInput.value : '';
                const response = await fetch('/ai-booking/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': csrfToken
                    },
                    body: JSON.stringify({
                        name: name,
                        email: '',
                        phone: '',
                        service_type: serviceType,
                        event_date: selDate,
                        time_slot: selSlot,
                        hours: pHours?.value || '',
                        message: `Service: ${serviceName}. Total: ${pTotal.innerText}`
                    })
                });

                const result = await response.json();
                if (!result.success) {
                    alert('Booking failed: ' + (result.error || 'Unknown error'));
                    return;
                }
            } catch (err) {
                console.error('Booking fetch error:', err);
                alert('Network error. Booking not saved. Please try again.');
                return;
            }

            // 2. Mark date as booked locally so calendar disables it immediately
            if (!bookedDates.includes(selDate)) {
                bookedDates.push(selDate);
            }

            // 3. Persist invoice locally (no Invoice model yet)
            const invoices = JSON.parse(localStorage.getItem('luxe_invoices') || '[]');
            invoices.push({ id: invId, client: name, date: selDate, total: pTotal.innerText, status: 'Unpaid' });
            localStorage.setItem('luxe_invoices', JSON.stringify(invoices));

            // 4. Show booking confirmed message inside the widget
            confirmBtn.classList.add('hidden');
            const successMsg = document.getElementById('booking-success-msg');
            if (successMsg) {
                successMsg.classList.remove('hidden');
                lucide.createIcons();
            }

            // 5. Populate Invoice Modal data (but don't open yet)
            const invClient = document.getElementById('inv-client-name');
            const invDate = document.getElementById('inv-date-slot');
            const invItems = document.getElementById('inv-items');
            const invTotal = document.getElementById('inv-total');

            if (invClient) invClient.innerText = name;
            if (invDate) invDate.innerText = `${selDate} | ${selSlot}`;
            if (invTotal) invTotal.innerText = pTotal.innerText;
            if (invItems) invItems.innerHTML = `<tr><td class="py-4 font-bold uppercase text-xs">${serviceName} session</td><td class="py-4 text-right">${pTotal.innerText}</td></tr>`;

            renderCal();
        };

        // View Invoice button handler
        document.getElementById('view-invoice-btn')?.addEventListener('click', () => {
            const invModal = document.getElementById('invoice-modal');
            const overlay = document.getElementById('advanced-features-overlay');
            if (overlay) overlay.classList.add('hidden');
            if (invModal) {
                invModal.classList.remove('hidden');
                invModal.classList.add('flex');
            }
        });

        // PDF Generation
        document.getElementById('download-invoice-btn')?.addEventListener('click', () => {
            const invoice = document.getElementById('invoice-content');
            if (invoice && typeof html2pdf !== 'undefined') {
                const opt = {
                    margin: 0.5,
                    filename: `LUXE_Inovice_${Date.now()}.pdf`,
                    image: { type: 'jpeg', quality: 0.98 },
                    html2canvas: { scale: 2 },
                    jsPDF: { unit: 'in', format: 'letter', orientation: 'portrait' }
                };
                html2pdf().from(invoice).set(opt).save();
            } else {
                window.print();
            }
        });

        document.getElementById('close-invoice')?.addEventListener('click', () => {
            const modal = document.getElementById('invoice-modal');
            if (modal) {
                modal.classList.add('hidden');
                modal.classList.remove('flex');
            }
        });

        const mainChatToggle = document.getElementById('chat-toggle');
        const mainChatWindow = document.getElementById('chat-window');
        const closeChatBtn = document.getElementById('close-chat');

        const toggleChatModal = () => {
            if (!mainChatWindow) return;
            if (mainChatWindow.classList.contains('hidden')) {
                mainChatWindow.classList.remove('hidden');
                setTimeout(() => {
                    mainChatWindow.classList.remove('opacity-0', 'scale-95');
                    mainChatWindow.classList.add('opacity-100', 'scale-100');
                    if (chatInput) chatInput.focus();
                }, 10);
            } else {
                mainChatWindow.classList.remove('opacity-100', 'scale-100');
                mainChatWindow.classList.add('opacity-0', 'scale-95');
                setTimeout(() => {
                    mainChatWindow.classList.add('hidden');
                }, 300);
            }
        };

        if (mainChatToggle) mainChatToggle.onclick = toggleChatModal;
        if (closeChatBtn) closeChatBtn.onclick = toggleChatModal;
    };

    if (document.readyState === 'loading') {
        window.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
