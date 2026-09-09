from rest_framework import viewsets, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import (
    GalleryCategory,
    GalleryProject,
    GalleryImage,
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
from .serializers import (
    GalleryCategorySerializer,
    GalleryProjectSerializer,
    GalleryImageSerializer,
    ReelCategorySerializer,
    ReelVideoSerializer,
    ServiceSerializer,
    BookingSerializer,
    ContactSerializer,
    InquirySerializer,
    TestimonialSerializer,
    ChatbotConfigurationSerializer,
    WhatsAppConfigurationSerializer,
    InvoiceSerializer,
)


class GalleryCategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for gallery categories.
    """
    queryset = GalleryCategory.objects.filter(is_active=True)
    serializer_class = GalleryCategorySerializer
    lookup_field = 'slug'


class GalleryProjectViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for gallery projects.
    """
    queryset = GalleryProject.objects.all()
    serializer_class = GalleryProjectSerializer
    lookup_field = 'slug'


class GalleryImageViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for gallery images.
    """
    queryset = GalleryImage.objects.filter(is_published=True)
    serializer_class = GalleryImageSerializer


class ReelCategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for reel categories.
    """
    queryset = ReelCategory.objects.filter(is_active=True)
    serializer_class = ReelCategorySerializer
    lookup_field = 'slug'


class ReelVideoViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for reel videos.
    """
    queryset = ReelVideo.objects.filter(is_published=True)
    serializer_class = ReelVideoSerializer
    lookup_field = 'slug'


class ServiceViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for services.
    """
    queryset = Service.objects.filter(is_active=True)
    serializer_class = ServiceSerializer
    lookup_field = 'slug'


class TestimonialViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for testimonials.
    """
    queryset = Testimonial.objects.filter(is_published=True)
    serializer_class = TestimonialSerializer


class InquiryViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for inquiries.
    """
    queryset = Inquiry.objects.all()
    serializer_class = InquirySerializer


@api_view(['POST'])
def create_booking(request):
    """
    API endpoint to create a booking.
    """
    serializer = BookingSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def create_contact(request):
    """
    API endpoint to create a contact message.
    """
    serializer = ContactSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ChatbotConfigurationViewSet(viewsets.ModelViewSet):
    """
    API endpoint for chatbot configuration.
    Only one instance should exist at a time.
    """
    queryset = ChatbotConfiguration.objects.all()
    serializer_class = ChatbotConfigurationSerializer
    
    def get_object(self):
        """Get or create the single chatbot configuration instance."""
        obj, created = ChatbotConfiguration.objects.get_or_create(pk=1)
        return obj


class WhatsAppConfigurationViewSet(viewsets.ModelViewSet):
    """
    API endpoint for WhatsApp configuration.
    Only one instance should exist at a time.
    """
    queryset = WhatsAppConfiguration.objects.all()
    serializer_class = WhatsAppConfigurationSerializer
    
    def get_object(self):
        """Get or create the single WhatsApp configuration instance."""
        obj, created = WhatsAppConfiguration.objects.get_or_create(pk=1)
        return obj


class InvoiceViewSet(viewsets.ModelViewSet):
    """
    API endpoint for invoices.
    """
    queryset = Invoice.objects.all()
    serializer_class = InvoiceSerializer


@api_view(['GET'])
def get_chatbot_config(request):
    """
    Get chatbot configuration (public API).
    """
    config, created = ChatbotConfiguration.objects.get_or_create(pk=1)
    serializer = ChatbotConfigurationSerializer(config)
    return Response(serializer.data)


@api_view(['GET'])
def get_whatsapp_config(request):
    """
    Get WhatsApp configuration (public API).
    """
    config, created = WhatsAppConfiguration.objects.get_or_create(pk=1)
    serializer = WhatsAppConfigurationSerializer(config)
    return Response(serializer.data)


@api_view(['PUT'])
def update_invoice_status(request, pk):
    """
    Update invoice payment status.
    """
    try:
        invoice = Invoice.objects.get(pk=pk)
    except Invoice.DoesNotExist:
        return Response({'error': 'Invoice not found'}, status=status.HTTP_404_NOT_FOUND)
    
    if 'status' in request.data:
        invoice.status = request.data['status']
        if request.data['status'] == 'paid':
            from django.utils import timezone
            invoice.paid_at = timezone.now()
        invoice.save()
    
    serializer = InvoiceSerializer(invoice)
    return Response(serializer.data)
