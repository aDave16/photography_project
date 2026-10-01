from django.urls import path
from . import views
from . import views_booking
from . import views_inquiry
from . import views_dashboard
from . import views_financial

urlpatterns = [
    # Authentication
    path('login/', views.AdminLoginView.as_view(), name='admin_login'),
    path('logout/', views.AdminLogoutView.as_view(), name='admin_logout'),
    
    # Main public pages
    path('', views.home, name='home'),
    path('gallery/', views.gallery, name='gallery'),
    path('gallery/<slug:slug>/', views.gallery, name='gallery_detail'),
    path('portfolio/', views.portfolio, name='portfolio'),
    path('reels/', views.reels, name='reels'),
    path('about/', views.about, name='about'),
    path('services/', views.services, name='services'),
    path('services/<slug:slug>/', views.service_detail, name='service_detail'),
    path('contact/', views.contact, name='contact'),
    path('booking/', views_booking.booking_page, name='booking'),
    
    # Inquiry system
    path('submit-inquiry/', views_inquiry.submit_inquiry, name='submit_inquiry'),

    # Admin Dashboard pages
    path('dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('dashboard/bookings/', views.admin_bookings, name='admin_bookings'),
    path('dashboard/availability/', views_dashboard.dashboard_availability, name='dashboard_availability'),
    path('dashboard/inquiries/', views.dashboard_inquiries, name='dashboard_inquiries'),

    path('dashboard/gallery/', views.admin_gallery, name='admin_gallery'),
    path('dashboard/gallery/images/', views_dashboard.gallery_images, name='dashboard_gallery_images'),
    path('dashboard/gallery/categories/', views_dashboard.gallery_categories, name='dashboard_gallery_categories'),
    path('dashboard/gallery/categories/create/', views_dashboard.create_gallery_category, name='create_gallery_category'),
path(
    'dashboard/gallery/categories/edit/<int:category_id>/',
    views.edit_gallery_category,
    name='edit_gallery_category'
),path(
    'dashboard/gallery/categories/delete/<int:category_id>/',
    views.delete_gallery_category,
    name='delete_gallery_category'
),
path(
    'dashboard/gallery/images/create/',
    views_dashboard.create_gallery_image,
    name='create_gallery_image'
),
path(
    'dashboard/gallery/images/upload/',
    views_dashboard.upload_gallery_images,
    name='upload_gallery_images'
),

path(
    'dashboard/gallery/images/edit/<int:image_id>/',
    views_dashboard.edit_gallery_image,
    name='edit_gallery_image'
),

path(
    'dashboard/gallery/images/delete/<int:image_id>/',
    views_dashboard.delete_gallery_image,
    name='delete_gallery_image'
),
    path('dashboard/services/', views.admin_services, name='admin_services'),
    path('dashboard/services/manage/', views_dashboard.dashboard_services, name='dashboard_services'),
    path('dashboard/contacts/', views.admin_contacts, name='admin_contacts'),
    path('dashboard/ai-concierge/', views.admin_ai_concierge, name='admin_ai_concierge'),
    path('dashboard/testimonials/', views.admin_testimonials, name='admin_testimonials'),
    
    # Financial Cloud
    path('dashboard/financial-cloud/', views_financial.financial_cloud_overview, name='financial_cloud_overview'),
    path('dashboard/financial-cloud/record/', views_financial.record_payment, name='financial_record_payment'),
    path('dashboard/financial-cloud/expenses/', views_financial.manage_expenses, name='manage_expenses'),
    path('dashboard/financial-cloud/invoice/<int:booking_id>/', views_financial.generate_invoice, name='generate_invoice'),
    path('dashboard/financial-cloud/reminder/<int:booking_id>/', views_financial.payment_reminder, name='payment_reminder'),

    # Dashboard create/update endpoints
    path('dashboard/create-service/', views.admin_create_service, name='dashboard_create_service'),
    path('dashboard/bulk-upload/', views_dashboard.dashboard_bulk_upload, name='dashboard_bulk_upload'),
    path('dashboard/add-reel/', views_dashboard.dashboard_add_reel, name='dashboard_add_reel'),
    path('dashboard/update-service/', views_dashboard.dashboard_service_ajax, name='dashboard_service_ajax'),
    path('dashboard/update-service/<int:service_id>/', views.dashboard_update_service, name='dashboard_update_service'),
    path('dashboard/sync-s' \
    'ervice-prices/', views.dashboard_sync_service_prices, name='dashboard_sync_service_prices'),
    path('dashboard/update-inquiry-status/', views.dashboard_update_inquiry_status, name='dashboard_update_inquiry_status'),
    path('dashboard/reply-inquiry/', views.dashboard_reply_inquiry, name='dashboard_reply_inquiry'),

    # AJAX endpoints for dynamic filtering
    
    # Booking system endpoints
    path('api/create-booking/', views_booking.create_booking, name='create_booking'),
    path('api/available-slots/', views_booking.get_available_slots, name='get_available_slots'),
    path('api/calendar/', views_booking.get_calendar_data, name='get_calendar_data'),
    path('api/calendar-availability/', views_booking.get_calendar_data, name='calendar_availability'),
    path('api/date-details/', views_booking.get_date_details, name='get_date_details'),
    # Admin availability APIs (v2)
    path('api/admin/calendar-events/', views_booking.admin_calendar_events, name='admin_calendar_events'),
    path('dashboard/calendar-bookings/', views_booking.dashboard_calendar_bookings, name='dashboard_calendar_bookings'),
    path('api/admin/bookings/', views_booking.admin_create_booking_v2, name='admin_create_booking_v2'),
    path('api/admin/blocks/', views_booking.admin_create_block, name='admin_create_block'),
    path('api/admin/blocks/toggle/', views_booking.admin_toggle_block, name='admin_toggle_block'),
    path('api/admin/bookings/<int:booking_id>/', views_booking.admin_get_booking, name='admin_get_booking'),
    path('api/admin/bookings/<int:booking_id>/update/', views_booking.admin_update_booking, name='admin_update_booking'),
    path('api/admin/bookings/<int:booking_id>/cancel/', views_booking.admin_cancel_booking, name='admin_cancel_booking'),
    path('api/admin/bookings/<int:booking_id>/complete/', views_booking.admin_mark_complete, name='admin_mark_complete'),
    
    # Services API endpoints
    path('api/services/', views_booking.api_services, name='api_services'),
    path('api/services/<slug:slug>/', views_booking.api_service_detail, name='api_service_detail'),
    
    path('booking/success/', views_booking.booking_success, name='booking_success'),
    path(
        'ajax/gallery/category/<slug:category_slug>/',
        views.ajax_gallery_by_category,
        name='ajax_gallery_category'
    ),
    path(
        'ajax/reels/category/<slug:category_slug>/',
        views.ajax_reels_by_category,
        name='ajax_reels_category'
    ),

    # AI Chatbot booking endpoint
    path('ai-booking/', views.ai_booking, name='ai_booking'),

    # AI Chatbot OpenAI conversation endpoint
    path('ai-chat/', views.ai_chat, name='ai_chat'),
    path('chat/', views.chat_page, name='chat_page'),

    path(
    'portfolio/',
    views.portfolio,
    name='portfolio'
),

path(
    'dashboard/chatbot/save/',
    views.save_chatbot_config,
    name='save_chatbot_config'
),
]


