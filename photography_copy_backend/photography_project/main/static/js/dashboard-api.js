/**
 * Dashboard API Communication Layer
 * Replaces localStorage with API calls for database-backed configurations
 */

const DashboardAPI = {
    // API endpoint base
    apiBase: '/api',
    
    /**
     * Fetch chatbot configuration from database
     */
    async getChatbotConfig() {
        try {
            const response = await fetch(`${this.apiBase}/chatbot-config/get/`, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]')?.value || '',
                }
            });
            if (!response.ok) throw new Error('Failed to fetch chatbot config');
            const data = await response.json();
            
            // Map API field names to template expectations
            return {
                greeting: data.welcome_message || 'Hello! I am your AI concierge. How can I help you today?',
                faq: data.faq_items || [],
                _id: data.id, // Store for updates
                _fullData: data // Store full data for complete updates
            };
        } catch (error) {
            console.error('Error fetching chatbot config:', error);
            // Fallback to default
            return {
                greeting: 'Hello! I am your AI concierge. How can I help you today?',
                faq: [],
                _id: null
            };
        }
    },
    
    /**
     * Save chatbot configuration to database
     */
    async saveChatbotConfig(chatbotData) {
        try {
            const payload = {
                welcome_message: chatbotData.greeting,
                faq_items: chatbotData.faq,
                is_active: true
            };
            
            const url = `${this.apiBase}/chatbot-config/${chatbotData._id || '1'}/`;
            const method = chatbotData._id ? 'PUT' : 'POST';
            
            const response = await fetch(url, {
                method: method,
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]')?.value || '',
                },
                body: JSON.stringify(payload)
            });
            
            if (!response.ok) throw new Error('Failed to save chatbot config');
            const data = await response.json();
            console.log('Chatbot config saved:', data);
            return data;
        } catch (error) {
            console.error('Error saving chatbot config:', error);
            alert('Failed to save chatbot configuration: ' + error.message);
            throw error;
        }
    },
    
    /**
     * Fetch WhatsApp configuration from database
     */
    async getWhatsAppConfig() {
        try {
            const response = await fetch(`${this.apiBase}/whatsapp-config/get/`, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]')?.value || '',
                }
            });
            if (!response.ok) throw new Error('Failed to fetch WhatsApp config');
            const data = await response.json();
            
            // Map API field names to template expectations
            return {
                number: data.whatsapp_number || '',
                template: data.message_template || '',
                _id: data.id, // Store for updates
                _fullData: data // Store full data for complete updates
            };
        } catch (error) {
            console.error('Error fetching WhatsApp config:', error);
            // Fallback to default
            return {
                number: '',
                template: '',
                _id: null
            };
        }
    },
    
    /**
     * Save WhatsApp configuration to database
     */
    async saveWhatsAppConfig(whatsappData) {
        try {
            const payload = {
                whatsapp_number: whatsappData.number,
                message_template: whatsappData.template,
                is_active: true
            };
            
            const url = `${this.apiBase}/whatsapp-config/${whatsappData._id || '1'}/`;
            const method = whatsappData._id ? 'PUT' : 'POST';
            
            const response = await fetch(url, {
                method: method,
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]')?.value || '',
                },
                body: JSON.stringify(payload)
            });
            
            if (!response.ok) throw new Error('Failed to save WhatsApp config');
            const data = await response.json();
            console.log('WhatsApp config saved:', data);
            return data;
        } catch (error) {
            console.error('Error saving WhatsApp config:', error);
            alert('Failed to save WhatsApp configuration: ' + error.message);
            throw error;
        }
    },
    
    /**
     * Fetch all invoices from database
     */
    async getInvoices() {
        try {
            const response = await fetch(`${this.apiBase}/invoices/`, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]')?.value || '',
                }
            });
            if (!response.ok) throw new Error('Failed to fetch invoices');
            const data = await response.json();
            
            // Handle paginated response
            const invoices = Array.isArray(data) ? data : (data.results || []);
            return invoices.map(inv => ({
                id: inv.id,
                booking_id: inv.booking,
                booking_name: inv.booking_name,
                invoice_number: inv.invoice_number,
                amount: inv.amount,
                status: inv.status,
                generated_at: inv.generated_at,
                paid_at: inv.paid_at,
                _fullData: inv
            }));
        } catch (error) {
            console.error('Error fetching invoices:', error);
            return [];
        }
    },
    
    /**
     * Create a new invoice
     */
    async createInvoice(invoiceData) {
        try {
            const response = await fetch(`${this.apiBase}/invoices/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]')?.value || '',
                },
                body: JSON.stringify(invoiceData)
            });
            
            if (!response.ok) throw new Error('Failed to create invoice');
            return await response.json();
        } catch (error) {
            console.error('Error creating invoice:', error);
            alert('Failed to create invoice: ' + error.message);
            throw error;
        }
    },
    
    /**
     * Update invoice status
     */
    async updateInvoiceStatus(invoiceId, status) {
        try {
            const response = await fetch(`${this.apiBase}/invoices/${invoiceId}/update-status/`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]')?.value || '',
                },
                body: JSON.stringify({ status: status })
            });
            
            if (!response.ok) throw new Error('Failed to update invoice status');
            return await response.json();
        } catch (error) {
            console.error('Error updating invoice status:', error);
            alert('Failed to update invoice: ' + error.message);
            throw error;
        }
    },
    
    /**
     * Delete an invoice
     */
    async deleteInvoice(invoiceId) {
        try {
            const response = await fetch(`${this.apiBase}/invoices/${invoiceId}/`, {
                method: 'DELETE',
                headers: {
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]')?.value || '',
                }
            });
            
            if (!response.ok) throw new Error('Failed to delete invoice');
            return true;
        } catch (error) {
            console.error('Error deleting invoice:', error);
            alert('Failed to delete invoice: ' + error.message);
            throw error;
        }
    }
};

// Export for use in templates
window.DashboardAPI = DashboardAPI;
