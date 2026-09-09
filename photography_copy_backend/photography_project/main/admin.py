from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import (
    GalleryCategory,
    GalleryImage,
    ReelVideo,
    Service,
    Booking,
    Contact,
    Testimonial,
    HeroSection,
    AboutSection,
    Inquiry,
    GalleryProject,
    ChatbotConfiguration,
    WhatsAppConfiguration,
    Invoice,
)


# =============================================================================
# CUSTOM ADMIN SITE CONFIGURATION
# =============================================================================
admin.site.site_header = "Lens & Light Photography Admin"
admin.site.site_title = "Lens & Light Admin"
admin.site.index_title = "Welcome to your Photography Website Manager"


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================
def image_thumbnail(obj, field_name='image', width=80, height=60):
    """Generate a small thumbnail preview for ImageField in admin list."""
    img_field = getattr(obj, field_name, None)
    if img_field and hasattr(img_field, 'url'):
        return format_html(
            '<img src="{}" style="width:{}px; height:{}px; object-fit:cover; border-radius:4px;" />',
            img_field.url, width, height
        )
    return format_html('<span style="color:#888;">No Image</span>')


def video_preview(obj, field_name='video'):
    """Generate a small video preview for FileField in admin list."""
    vid_field = getattr(obj, field_name, None)
    if vid_field and hasattr(vid_field, 'url'):
        return format_html(
            '<video width="120" height="80" controls style="border-radius:4px;">'
            '<source src="{}" type="video/mp4">'
            'Your browser does not support the video tag.'
            '</video>',
            vid_field.url
        )
    return format_html('<span style="color:#888;">No Video</span>')


# =============================================================================
# 1. GALLERY CATEGORY ADMIN
# =============================================================================
@admin.register(GalleryCategory)
class GalleryCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'display_order', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description']
    list_editable = ['display_order', 'is_active']
    prepopulated_fields = {'slug': ('name',)}
    fieldsets = (
        ('Category Info', {
            'fields': ('name', 'slug', 'description')
        }),
        ('Display Settings', {
            'fields': ('display_order', 'is_active'),
        }),
    )


# =============================================================================
# 2. GALLERY IMAGE ADMIN
# =============================================================================
@admin.register(GalleryImage)
class GalleryImageAdmin(admin.ModelAdmin):
    list_display = [
        'thumbnail_preview', 'title', 'category', 'is_featured',
        'is_published', 'display_order', 'created_at'
    ]
    list_filter = [
        'category', 'is_featured', 'is_published', 'created_at'
    ]
    search_fields = ['title', 'caption', 'description']
    list_editable = ['is_featured', 'is_published', 'display_order']
    readonly_fields = ['created_at', 'updated_at', 'image_preview_large']
    prepopulated_fields = {'slug': ('title',)}
    date_hierarchy = 'created_at'
    list_per_page = 20

    fieldsets = (
        ('Image Upload', {
            'fields': (
                'title', 'slug', 'image', 'thumbnail',
                'image_preview_large', 'category'
            )
        }),
        ('Details', {
            'fields': ('caption', 'description'),
            'classes': ('collapse',)
        }),
        ('Display Settings', {
            'fields': ('is_featured', 'is_published', 'display_order'),
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def thumbnail_preview(self, obj):
        return image_thumbnail(obj, 'image', 80, 60)
    thumbnail_preview.short_description = 'Preview'

    def image_preview_large(self, obj):
        return image_thumbnail(obj, 'image', 300, 200)
    image_preview_large.short_description = 'Large Preview'


# =============================================================================
# 3. REEL VIDEO ADMIN
# =============================================================================
@admin.register(ReelVideo)
class ReelVideoAdmin(admin.ModelAdmin):
    list_display = [
        'video_thumbnail', 'title', 'category', 'duration',
        'is_featured', 'is_published', 'views_count', 'created_at'
    ]
    list_filter = [
        'category', 'is_featured', 'is_published', 'created_at'
    ]
    search_fields = ['title', 'description']
    list_editable = ['is_featured', 'is_published', 'duration']
    readonly_fields = ['created_at', 'updated_at', 'video_preview_admin']
    prepopulated_fields = {'slug': ('title',)}
    date_hierarchy = 'created_at'
    list_per_page = 15

    fieldsets = (
        ('Video Upload', {
            'fields': (
                'title', 'slug', 'video',
                'video_preview_admin', 'thumbnail', 'category'
            )
        }),
        ('Details', {
            'fields': ('description', 'duration', 'views_count'),
            'classes': ('collapse',)
        }),
        ('Display Settings', {
            'fields': ('is_featured', 'is_published', 'display_order'),
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def video_thumbnail(self, obj):
        if obj.thumbnail and hasattr(obj.thumbnail, 'url'):
            return image_thumbnail(obj, 'thumbnail', 100, 70)
        return video_preview(obj, 'video')
    video_thumbnail.short_description = 'Preview'

    def video_preview_admin(self, obj):
        if obj.video and hasattr(obj.video, 'url'):
            return format_html(
                '<video width="400" height="250" controls style="border-radius:8px; max-width:100%;">'
                '<source src="{}" type="video/mp4">'
                'Your browser does not support the video tag.'
                '</video>',
                obj.video.url
            )
        return format_html('<span style="color:#888;">No video uploaded</span>')
    video_preview_admin.short_description = 'Video Preview'


# =============================================================================
# 4. GALLERY PROJECT ADMIN
# =============================================================================
@admin.register(GalleryProject)
class GalleryProjectAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'client_name', 'is_featured', 'display_order']
    list_filter = ['category', 'is_featured']
    search_fields = ['title', 'client_name', 'caption']
    prepopulated_fields = {'slug': ('title',)}
    list_editable = ['is_featured', 'display_order']


# =============================================================================
# 5. SERVICE ADMIN
# =============================================================================
@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = [
        'cover_image_preview', 'title', 'service_type', 'price',
        'is_featured', 'is_active', 'display_order', 'created_at'
    ]
    list_editable = ['price', 'is_featured', 'is_active', 'display_order']
    list_filter = ['service_type', 'is_featured', 'is_active', 'created_at']
    search_fields = ['title', 'description', 'tagline']
    readonly_fields = ['created_at', 'updated_at']
    prepopulated_fields = {'slug': ('title',)}

    def cover_image_preview(self, obj):
        if obj.cover_image and hasattr(obj.cover_image, 'url'):
            return image_thumbnail(obj, 'cover_image', 60, 45)
        return format_html('<span style="color:#888;">No Image</span>')


# =============================================================================
# 6. BOOKING ADMIN
# =============================================================================
@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'service', 'event_date', 'status', 'created_at']
    list_filter = ['status', 'service', 'event_date', 'created_at']
    search_fields = ['name', 'email', 'phone', 'message']
    list_editable = ['status']
    readonly_fields = ['created_at', 'updated_at']


# =============================================================================
# 7. CONTACT ADMIN
# =============================================================================
@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'subject', 'is_read', 'is_replied', 'created_at']
    list_filter = ['subject', 'is_read', 'is_replied', 'created_at']
    search_fields = ['name', 'email', 'message']
    list_editable = ['is_read', 'is_replied']


# =============================================================================
# 8. TESTIMONIAL ADMIN
# =============================================================================
@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    list_display = ['client_name', 'project', 'rating', 'is_featured', 'is_published', 'created_at']
    list_filter = ['is_featured', 'is_published', 'rating', 'created_at']
    search_fields = ['client_name', 'testimonial']
    list_editable = ['is_featured', 'is_published', 'rating']


# =============================================================================
# 9. HERO SECTION ADMIN
# =============================================================================
@admin.register(HeroSection)
class HeroSectionAdmin(admin.ModelAdmin):
    list_display = ['title', 'is_active', 'show_reel_slider', 'updated_at']
    list_filter = ['is_active', 'show_reel_slider']
    list_editable = ['is_active']


# =============================================================================
# 10. ABOUT SECTION ADMIN
# =============================================================================
@admin.register(AboutSection)
class AboutSectionAdmin(admin.ModelAdmin):
    list_display = ['photographer_name', 'photographer_title', 'experience_years', 'is_active']
    list_editable = ['is_active']


# =============================================================================
# 11. INQUIRY ADMIN
# =============================================================================
@admin.register(Inquiry)
class InquiryAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'event_type', 'replied', 'created_at']
    list_filter = ['event_type', 'replied', 'created_at']
    search_fields = ['name', 'email', 'message']
    list_editable = ['replied']


# =============================================================================
# 12. CHATBOT CONFIGURATION ADMIN
# =============================================================================
@admin.register(ChatbotConfiguration)
class ChatbotConfigurationAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'is_active', 'updated_at']
    list_filter = ['is_active']
    list_editable = ['is_active']
    fieldsets = (
        ('Bot Settings', {
            'fields': ('welcome_message', 'system_prompt', 'is_active')
        }),
        ('FAQ Items', {
            'fields': ('faq_items',),
            'classes': ('collapse',),
            'description': 'Enter FAQ items as JSON: [{"q": "Question?", "a": "Answer"}, ...]'
        }),
    )
    
    def has_add_permission(self, request):
        """Allow only one chatbot configuration."""
        return not ChatbotConfiguration.objects.exists()


# =============================================================================
# 13. WHATSAPP CONFIGURATION ADMIN
# =============================================================================
@admin.register(WhatsAppConfiguration)
class WhatsAppConfigurationAdmin(admin.ModelAdmin):
    list_display = ['whatsapp_number', 'is_active', 'updated_at']
    list_filter = ['is_active']
    list_editable = ['is_active']
    fieldsets = (
        ('WhatsApp Settings', {
            'fields': ('whatsapp_number', 'message_template', 'is_active')
        }),
    )
    
    def has_add_permission(self, request):
        """Allow only one WhatsApp configuration."""
        return not WhatsAppConfiguration.objects.exists()


# =============================================================================
# 14. INVOICE ADMIN
# =============================================================================
@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ['invoice_number', 'booking', 'amount', 'status', 'generated_at', 'paid_at']
    list_filter = ['status', 'generated_at', 'paid_at']
    search_fields = ['invoice_number', 'booking__name', 'booking__email']
    readonly_fields = ['generated_at', 'updated_at']
    list_editable = ['status']
    date_hierarchy = 'generated_at'
    list_per_page = 25
    
    fieldsets = (
        ('Invoice Details', {
            'fields': ('booking', 'invoice_number', 'amount', 'status')
        }),
        ('Payment Info', {
            'fields': ('paid_at', 'pdf_file'),
            'classes': ('collapse',)
        }),
        ('Notes', {
            'fields': ('notes',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('generated_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_readonly_fields(self, request, obj=None):
        """Make certain fields readonly for existing invoices."""
        if obj:
            return self.readonly_fields + ['booking', 'invoice_number']
        return self.readonly_fields


