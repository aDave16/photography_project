from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm
from .models import (
    Booking, Contact, GalleryCategory, GalleryImage, ReelVideo, GalleryProject,
    ChatbotConfiguration, WhatsAppConfiguration, Invoice
)


# =============================================================================
# BOOKING FORM
# =============================================================================
class BookingForm(forms.ModelForm):
    """
    Form for client booking inquiries.
    Maps to the Booking model. All fields here are filled by the CLIENT.
    Admin-only fields (status, admin_notes) are excluded.
    """
    class Meta:
        model = Booking
        fields = [
            'name', 'email', 'phone', 'service',
            'event_date', 'time_slot', 'location', 'message', 'budget_range'
        ]
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Full Name',
                'required': True
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Email Address',
                'required': True
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Phone Number'
            }),
            'service': forms.Select(attrs={
                'class': 'form-control',
                'required': True
            }),
            'event_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'time_slot': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Preferred Time (e.g., 10:00 AM)'
            }),
            'location': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Event location or venue'
            }),
            'budget_range': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., $1,000 - $2,000'
            }),
            'message': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Briefly describe your vision, preferred style, or any special requests...',
                'rows': 4
            }),
        }


# =============================================================================
# CONTACT FORM
# =============================================================================
class ContactForm(forms.ModelForm):
    """
    Form for contact page messages.
    Maps to the Contact model. Admin-only fields excluded.
    """
    class Meta:
        model = Contact
        fields = ['name', 'email', 'phone', 'subject', 'message']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Full Name',
                'required': True
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Email Address',
                'required': True
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Phone Number (optional)'
            }),
            'subject': forms.Select(attrs={
                'class': 'form-control',
                'required': True
            }),
            'message': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Tell us about your project or inquiry...',
                'rows': 4,
                'required': True
            }),
        }


# =============================================================================
# GALLERY CATEGORY FORM
# =============================================================================
class GalleryCategoryForm(forms.ModelForm):
    class Meta:
        model = GalleryCategory
        fields = [
            'name', 'slug', 'description', 'display_order', 'is_active'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'input-field w-full px-4 py-3 rounded-xl text-sm', 'placeholder': 'Category Name'}),
            'slug': forms.TextInput(attrs={'class': 'input-field w-full px-4 py-3 rounded-xl text-sm', 'placeholder': 'Leave blank to auto-generate'}),
            'description': forms.Textarea(attrs={'class': 'input-field w-full px-4 py-3 rounded-xl text-sm', 'rows': 3, 'placeholder': 'Short description'}),
            'display_order': forms.NumberInput(attrs={'class': 'input-field w-full px-4 py-3 rounded-xl text-sm'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'rounded border-gray-300 text-gold focus:ring-gold'}),
        }

# =============================================================================
# GALLERY IMAGE FORM
# =============================================================================
class GalleryImageForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['category'].queryset = GalleryCategory.objects.filter(
            is_active=True
        ).order_by('display_order')

    class Meta:
        model = GalleryImage
        fields = [
            'title', 'category', 'image', 'caption', 
            'is_featured', 'is_published', 'display_order'
        ]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'input-field w-full px-4 py-3 rounded-xl text-sm'}),
            'category': forms.Select(attrs={'class': 'input-field w-full px-4 py-3 rounded-xl text-sm'}),
            'caption': forms.TextInput(attrs={'class': 'input-field w-full px-4 py-3 rounded-xl text-sm'}),
            'display_order': forms.NumberInput(attrs={'class': 'input-field w-full px-4 py-3 rounded-xl text-sm'}),
        }

# =============================================================================
# REEL VIDEO FORM
# =============================================================================
class ReelVideoForm(forms.ModelForm):
    class Meta:
        model = ReelVideo
        fields = [
            'title', 'category', 'video', 'thumbnail', 
            'description', 'duration', 'is_featured', 'is_published', 'order'
        ]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'input-field w-full px-4 py-3 rounded-xl text-sm'}),
            'category': forms.Select(attrs={'class': 'input-field w-full px-4 py-3 rounded-xl text-sm'}),
            'description': forms.Textarea(attrs={'class': 'input-field w-full px-4 py-3 rounded-xl text-sm', 'rows': 3}),
            'duration': forms.TextInput(attrs={'class': 'input-field w-full px-4 py-3 rounded-xl text-sm', 'placeholder': 'e.g. 0:45'}),
            'order': forms.NumberInput(attrs={'class': 'input-field w-full px-4 py-3 rounded-xl text-sm'}),
        }

# =============================================================================
# GALLERY PROJECT FORM
# =============================================================================
class GalleryProjectForm(forms.ModelForm):
    class Meta:
        model = GalleryProject
        fields = [
            'title', 'category', 'client_name', 'slug', 'caption',
            'cover_image', 'is_featured', 'display_order'
        ]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'input-field w-full px-4 py-3 rounded-xl text-sm'}),
            'category': forms.Select(attrs={'class': 'input-field w-full px-4 py-3 rounded-xl text-sm'}),
            'client_name': forms.TextInput(attrs={'class': 'input-field w-full px-4 py-3 rounded-xl text-sm'}),
            'slug': forms.TextInput(attrs={'class': 'input-field w-full px-4 py-3 rounded-xl text-sm', 'placeholder': 'Leave blank to auto-generate'}),
            'caption': forms.Textarea(attrs={'class': 'input-field w-full px-4 py-3 rounded-xl text-sm', 'rows': 3}),
            'display_order': forms.NumberInput(attrs={'class': 'input-field w-full px-4 py-3 rounded-xl text-sm'}),
        }


# =============================================================================
# AUTHENTICATION FORMS
# =============================================================================
class AdminLoginForm(AuthenticationForm):
    """
    Custom admin login form with styling.
    """
    username = forms.CharField(
        max_length=254,
        widget=forms.TextInput(attrs={
            'autofocus': True,
            'class': 'input-field w-full px-4 py-3 rounded-xl text-sm',
            'placeholder': 'Username or Email',
            'autocomplete': 'username',
        })
    )
    password = forms.CharField(
        label="Password",
        strip=False,
        widget=forms.PasswordInput(attrs={
            'autocomplete': 'current-password',
            'class': 'input-field w-full px-4 py-3 rounded-xl text-sm',
            'placeholder': 'Password',
        })
    )

    class Meta:
        model = User
        fields = ('username', 'password')


# =============================================================================
# CHATBOT CONFIGURATION FORM
# =============================================================================
class ChatbotConfigurationForm(forms.ModelForm):
    """
    Form for managing chatbot settings.
    """
    class Meta:
        model = ChatbotConfiguration
        fields = ['welcome_message', 'system_prompt', 'faq_items', 'is_active']
        widgets = {
            'welcome_message': forms.Textarea(attrs={
                'class': 'input-field w-full px-4 py-3 rounded-xl text-sm',
                'rows': 3,
                'placeholder': 'Welcome message for chatbot users'
            }),
            'system_prompt': forms.Textarea(attrs={
                'class': 'input-field w-full px-4 py-3 rounded-xl text-sm',
                'rows': 3,
                'placeholder': 'System prompt for AI chatbot'
            }),
            'faq_items': forms.Textarea(attrs={
                'class': 'input-field w-full px-4 py-3 rounded-xl text-sm',
                'rows': 5,
                'placeholder': '[{"q": "Question?", "a": "Answer"}, ...]'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'rounded border-gray-300 text-gold focus:ring-gold'
            }),
        }


# =============================================================================
# WHATSAPP CONFIGURATION FORM
# =============================================================================
class WhatsAppConfigurationForm(forms.ModelForm):
    """
    Form for managing WhatsApp settings.
    """
    class Meta:
        model = WhatsAppConfiguration
        fields = ['whatsapp_number', 'message_template', 'is_active']
        widgets = {
            'whatsapp_number': forms.TextInput(attrs={
                'class': 'input-field w-full px-4 py-3 rounded-xl text-sm',
                'placeholder': '919106093868'
            }),
            'message_template': forms.Textarea(attrs={
                'class': 'input-field w-full px-4 py-3 rounded-xl text-sm',
                'rows': 3,
                'placeholder': 'Use {service} and {price} placeholders'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'rounded border-gray-300 text-gold focus:ring-gold'
            }),
        }


# =============================================================================
# INVOICE FORM
# =============================================================================
class InvoiceForm(forms.ModelForm):
    """
    Form for managing invoices.
    """
    class Meta:
        model = Invoice
        fields = ['booking', 'invoice_number', 'amount', 'status', 'notes']
        widgets = {
            'booking': forms.Select(attrs={
                'class': 'input-field w-full px-4 py-3 rounded-xl text-sm'
            }),
            'invoice_number': forms.TextInput(attrs={
                'class': 'input-field w-full px-4 py-3 rounded-xl text-sm',
                'placeholder': 'e.g., INV-2026-001'
            }),
            'amount': forms.NumberInput(attrs={
                'class': 'input-field w-full px-4 py-3 rounded-xl text-sm',
                'step': '0.01'
            }),
            'status': forms.Select(attrs={
                'class': 'input-field w-full px-4 py-3 rounded-xl text-sm'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'input-field w-full px-4 py-3 rounded-xl text-sm',
                'rows': 3
            }),
        }
