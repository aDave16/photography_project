from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import api_views

router = DefaultRouter()
router.register(r'categories', api_views.GalleryCategoryViewSet, basename='gallery-category')
router.register(r'gallery', api_views.GalleryProjectViewSet, basename='gallery')
router.register(r'images', api_views.GalleryImageViewSet, basename='gallery-image')
router.register(r'reel-categories', api_views.ReelCategoryViewSet, basename='reel-category')
router.register(r'reels', api_views.ReelVideoViewSet, basename='reel')
router.register(r'services', api_views.ServiceViewSet, basename='services')
router.register(r'testimonials', api_views.TestimonialViewSet, basename='testimonials')
router.register(r'inquiries', api_views.InquiryViewSet, basename='inquiries')
router.register(r'chatbot-config', api_views.ChatbotConfigurationViewSet, basename='chatbot-config')
router.register(r'whatsapp-config', api_views.WhatsAppConfigurationViewSet, basename='whatsapp-config')
router.register(r'invoices', api_views.InvoiceViewSet, basename='invoice')

urlpatterns = [
    path('', include(router.urls)),
    path('booking/', api_views.create_booking, name='api_booking'),
    path('contact/', api_views.create_contact, name='api_contact'),
    path('chatbot-config/get/', api_views.get_chatbot_config, name='get_chatbot_config'),
    path('whatsapp-config/get/', api_views.get_whatsapp_config, name='get_whatsapp_config'),
    path('invoices/<int:pk>/update-status/', api_views.update_invoice_status, name='update_invoice_status'),
]
