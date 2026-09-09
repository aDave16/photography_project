from rest_framework import serializers
from .models import (
    GalleryProject,
    GalleryImage,
    GalleryCategory,
    ReelCategory,
    ReelVideo,
    Service,
    Booking,
    Contact,
    Inquiry,
    Testimonial,
    ChatbotConfiguration,
    WhatsAppConfiguration,
    Invoice,
)


class GalleryCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = GalleryCategory
        fields = ['id', 'name', 'slug', 'description', 'display_order', 'icon', 'order', 'is_active']


class GalleryImageSerializer(serializers.ModelSerializer):
    image_url = serializers.ImageField(source='image', read_only=True)
    thumbnail_url = serializers.ImageField(source='thumbnail', read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)

    class Meta:
        model = GalleryImage
        fields = [
            'id',
            'title',
            'slug',
            'category',
            'category_name',
            'image',
            'image_url',
            'thumbnail',
            'thumbnail_url',
            'caption',
            'description',
            'location',
            'date_taken',
            'display_order',
            'is_featured',
            'is_published',
            'created_at',
            'updated_at',
        ]


class GalleryProjectSerializer(serializers.ModelSerializer):
    images = GalleryImageSerializer(many=True, read_only=True)
    category = GalleryCategorySerializer(read_only=True)
    cover_image_url = serializers.ImageField(source='cover_image', read_only=True)

    class Meta:
        model = GalleryProject
        fields = [
            'id',
            'title',
            'slug',
            'client_name',
            'caption',
            'cover_image',
            'cover_image_url',
            'is_featured',
            'display_order',
            'category',
            'images',
            'created_at',
        ]


class ReelCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ReelCategory
        fields = ['id', 'name', 'slug', 'description', 'order', 'is_active', 'display_order']


class ReelVideoSerializer(serializers.ModelSerializer):
    thumbnail_url = serializers.ImageField(source='thumbnail', read_only=True)
    video_url = serializers.FileField(source='video', read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)

    class Meta:
        model = ReelVideo
        fields = [
            'id',
            'title',
            'slug',
            'category',
            'category_name',
            'video',
            'video_url',
            'thumbnail',
            'thumbnail_url',
            'description',
            'duration',
            'views_count',
            'is_featured',
            'is_published',
            'order',
            'created_at',
            'updated_at',
        ]


class ServiceSerializer(serializers.ModelSerializer):
    cover_image_url = serializers.ImageField(source='cover_image', read_only=True)
    image_url = serializers.ImageField(source='image', read_only=True)

    class Meta:
        model = Service
        fields = [
            'id',
            'title',
            'slug',
            'service_type',
            'tagline',
            'price',
            'price_note',
            'description',
            'short_description',
            'full_description',
            'features',
            'duration',
            'icon',
            'image',
            'image_url',
            'cover_image',
            'cover_image_url',
            'gallery_images',
            'display_order',
            'is_featured',
            'is_active',
            'created_at',
            'updated_at',
        ]


class BookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = [
            'id',
            'name',
            'email',
            'phone',
            'service',
            'event_date',
            'time_slot',
            'location',
            'message',
            'budget_range',
            'status',
            'payment_status',
            'admin_notes',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['created_at', 'updated_at']


class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = ['id', 'name', 'email', 'phone', 'subject', 'message', 'is_read', 'is_replied', 'admin_notes', 'created_at']
        read_only_fields = ['created_at']


class InquirySerializer(serializers.ModelSerializer):
    class Meta:
        model = Inquiry
        fields = [
            'id',
            'name',
            'email',
            'phone',
            'event_type',
            'message',
            'admin_reply',
            'replied',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['created_at', 'updated_at']


class TestimonialSerializer(serializers.ModelSerializer):
    image_url = serializers.ImageField(source='image', read_only=True)

    class Meta:
        model = Testimonial
        fields = [
            'id',
            'client_name',
            'client_role',
            'project',
            'testimonial',
            'rating',
            'image',
            'image_url',
            'is_featured',
            'is_published',
            'display_order',
            'created_at',
        ]


class ChatbotConfigurationSerializer(serializers.ModelSerializer):
    """Serializer for chatbot configuration."""
    
    class Meta:
        model = ChatbotConfiguration
        fields = ['id', 'welcome_message', 'system_prompt', 'faq_items', 'is_active', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']


class WhatsAppConfigurationSerializer(serializers.ModelSerializer):
    """Serializer for WhatsApp configuration."""
    
    class Meta:
        model = WhatsAppConfiguration
        fields = ['id', 'whatsapp_number', 'message_template', 'is_active', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']


class InvoiceSerializer(serializers.ModelSerializer):
    """Serializer for invoice model."""
    booking_name = serializers.CharField(source='booking.name', read_only=True)
    booking_email = serializers.CharField(source='booking.email', read_only=True)
    
    class Meta:
        model = Invoice
        fields = [
            'id',
            'booking',
            'booking_name',
            'booking_email',
            'invoice_number',
            'amount',
            'status',
            'pdf_file',
            'notes',
            'generated_at',
            'paid_at',
            'updated_at',
        ]
        read_only_fields = ['generated_at', 'updated_at']
