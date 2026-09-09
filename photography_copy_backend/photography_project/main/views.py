import json
import os
from decimal import Decimal
from django.views.decorators.http import require_POST

from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth import authenticate, login, logout
from django.views.decorators.csrf import ensure_csrf_cookie
from django.db.models import Q, Count
from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from .models import (
    ChatbotConfiguration,
    Inquiry,
    Service,
    GalleryCategory,
    GalleryImage,
    GalleryProject,
    ReelCategory,
    ReelVideo,
    Booking,
    Contact,
    Testimonial,
    HeroSection,
    AboutSection,
)
from .forms import BookingForm, ContactForm, AdminLoginForm


# =============================================================================
# AUTHENTICATION VIEWS
# =============================================================================
class AdminLoginView(LoginView):
    """
    Admin login view using Django's built-in authentication.
    """
    form_class = AdminLoginForm
    template_name = 'main/admin_login.html'
    success_url = reverse_lazy('admin_dashboard')
    redirect_authenticated_user = True

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('admin_dashboard')
        return super().dispatch(request, *args, **kwargs)
    
    def form_invalid(self, form):
        """Show error message on failed login."""
        messages.error(self.request, 'Invalid username or password.')
        return super().form_invalid(form)


class AdminLogoutView(LogoutView):
    """
    Admin logout view using Django's built-in logout.
    """
    next_page = reverse_lazy('home')
    
    def dispatch(self, request, *args, **kwargs):
        """Show success message on logout."""
        messages.success(request, 'You have been logged out successfully.')
        return super().dispatch(request, *args, **kwargs)


#@login_required(login_url='admin_login')
def admin_login_required_redirect(request):
    """Redirect unauthenticated users to login."""
    return redirect('admin_dashboard')


# =============================================================================
# HOME PAGE VIEW
# =============================================================================
@ensure_csrf_cookie
def home(request):
    """
    Home page view.
    Fetches: hero section, featured gallery images, featured reels,
    featured services, featured testimonials.
    """
    # Get the active hero section (only one should be active)
    hero = HeroSection.objects.filter(is_active=True).first()

    # Featured gallery images for hero/carousel sections
    featured_gallery = GalleryImage.objects.filter(
        is_featured=True, is_published=True
    )[:6]

    # All published gallery images for the ticker/grid
    all_gallery = GalleryImage.objects.filter(is_published=True)[:12]

    # Featured reels for the hero reel slider
    featured_reels = ReelVideo.objects.filter(
        is_featured=True, is_published=True
    )[:5]

    # Featured services (packages offered) — synced from admin dashboard
    featured_services = Service.objects.filter(
        is_featured=True, is_active=True
    ).order_by('display_order', '-created_at')[:3]

    # Featured testimonials for homepage slider
    featured_testimonials = Testimonial.objects.filter(
        is_featured=True, is_published=True
    )[:5]

    # All active categories for filter tabs
    gallery_categories = GalleryCategory.objects.filter(is_active=True).order_by('display_order')

    context = {
        'hero': hero,
        'featured_gallery': featured_gallery,
        'all_gallery': all_gallery,
        'featured_reels': featured_reels,
        'featured_services': featured_services,
        'featured_testimonials': featured_testimonials,
        'gallery_categories': gallery_categories,
    }
    return render(request, 'main/index.html', context)


# =============================================================================
# GALLERY PAGE VIEW
# =============================================================================
def gallery(request, slug=None):
    """
    Gallery page view.
    If slug is provided, shows a single image detail.
    Otherwise shows all gallery images with category filtering.
    """
    if slug:
        # Single image detail view
        photo = get_object_or_404(GalleryImage, slug=slug, is_published=True)
        context = {
            'photo': photo,
        }
        return render(request, 'main/gallery.html', context)

    # All gallery images with optional category filter
    category_slug = request.GET.get('category')

    photos = GalleryImage.objects.filter(is_published=True)

    if category_slug:
        photos = photos.filter(category__slug=category_slug)

    # Get all active categories for filter buttons/tabs
    categories = GalleryCategory.objects.filter(is_active=True).order_by('display_order')

    context = {
        'photos': photos,
        'categories': categories,
        'selected_category': category_slug,
    }
    return render(request, 'main/gallery.html', context)


# =============================================================================
# PORTFOLIO PAGE VIEW
# =============================================================================
def portfolio(request):
    category_slug = request.GET.get('category')

    categories = GalleryCategory.objects.filter(
        is_active=True
    ).order_by('display_order')

    images = GalleryImage.objects.filter(
        is_published=True
    ).select_related('category')

    if category_slug:
        images = images.filter(
            category__slug=category_slug
        )

    context = {
        'categories': categories,
        'images': images,
        'selected_category': category_slug,
    }

    return render(
        request,
        'main/portfolio.html',
        context
    )

# =============================================================================
# REELS PAGE VIEW
# =============================================================================
def reels(request):
    """
    Reels/Videos page view.
    Shows all published video reels with category filtering.
    """
    category_slug = request.GET.get('category')

    videos = ReelVideo.objects.filter(is_published=True)

    if category_slug:
        videos = videos.filter(category__slug=category_slug)

    categories = ReelCategory.objects.filter(is_active=True)

    # Featured reel for the top hero player
    featured_reel = ReelVideo.objects.filter(
        is_featured=True, is_published=True
    ).first()

    context = {
        'videos': videos,
        'categories': categories,
        'featured_reel': featured_reel,
        'selected_category': category_slug,
    }
    return render(request, 'main/reels.html', context)


# =============================================================================
# ABOUT PAGE VIEW
# =============================================================================
def about(request):
    """
    About page view.
    Fetches the active AboutSection with photographer bio, stats, images.
    Also shows published testimonials.
    """
    about_section = AboutSection.objects.filter(is_active=True).first()

    testimonials = Testimonial.objects.filter(
        is_published=True
    )[:6]

    context = {
        'about': about_section,
        'testimonials': testimonials,
    }
    return render(request, 'main/about.html', context)


# =============================================================================
# SERVICES PAGE VIEW
# =============================================================================
def services(request):
    """
    Dynamic services page view.
    Shows all active services ordered by display_order, then featured, then created_at.
    """
    # Get all active services ordered by display_order, featured status, and creation date
    all_services = Service.objects.filter(is_active=True).order_by(
        'display_order', '-is_featured', '-created_at'
    )

    # Featured services for prominent display
    featured_services = all_services.filter(is_featured=True)

    # Service types for filtering
    service_types = Service.objects.filter(is_active=True).values_list(
        'service_type', flat=True
    ).distinct()

    # Featured testimonials for the services page
    testimonials = Testimonial.objects.filter(
        is_featured=True, is_published=True
    )[:3]

    context = {
        'services': all_services,
        'featured_services': featured_services,
        'service_types': service_types,
        'testimonials': testimonials,
    }
    return render(request, 'main/services.html', context)


def service_detail(request, slug):
    """
    Dynamic service detail page view.
    Shows individual service with full details, gallery, and booking integration.
    """
    service = get_object_or_404(Service, slug=slug, is_active=True)
    
    # Get related services (same type, excluding current)
    related_services = Service.objects.filter(
        service_type=service.service_type,
        is_active=True
    ).exclude(id=service.id).order_by('display_order')[:3]
    
    # Get all services for booking dropdown
    all_services = Service.objects.filter(is_active=True).order_by(
        'display_order', '-is_featured', '-created_at'
    )
    
    # Featured testimonials
    testimonials = Testimonial.objects.filter(
        is_featured=True, is_published=True
    )[:3]
    
    context = {
        'service': service,
        'related_services': related_services,
        'all_services': all_services,
        'testimonials': testimonials,
    }
    return render(request, 'main/service_detail.html', context)


# =============================================================================
# CONTACT PAGE VIEW
# =============================================================================
@ensure_csrf_cookie
def contact(request):
    """
    Contact page view with form handling.
    Also fetches featured gallery for visual context.
    """
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(
                request,
                'Your message has been sent successfully! We will get back to you soon.'
            )
            return redirect('contact')
    else:
        form = ContactForm()

    # A few featured images for visual decoration on contact page
    featured_images = GalleryImage.objects.filter(
        is_featured=True, is_published=True
    )[:4]

    context = {
        'form': form,
        'featured_images': featured_images,
    }
    return render(request, 'main/contact.html', context)


# =============================================================================
# BOOKING PAGE VIEW
# =============================================================================
def booking(request):
    """
    Booking page view with form handling.
    Also shows active services so users know what to book.
    """
    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(
                request,
                'Your booking request has been submitted! We will contact you shortly.'
            )
            return redirect('booking')
    else:
        form = BookingForm()

    # Show all active services on the booking page
    all_services = Service.objects.filter(is_active=True)

    context = {
        'form': form,
        'services': all_services,
    }
    return render(request, 'main/booking.html', context)


# =============================================================================
# AJAX HELPERS (Optional but useful for dynamic frontend)
# =============================================================================
def ajax_gallery_by_category(request, category_slug):
    """
    AJAX endpoint to fetch gallery images by category.
    Returns JSON for dynamic frontend filtering without page reload.
    """
    photos = GalleryImage.objects.filter(
        category__slug=category_slug,
        is_published=True
    ).values('title', 'slug', 'image', 'caption')

    data = {
        'photos': list(photos),
        'count': photos.count(),
    }
    return JsonResponse(data)


def ajax_reels_by_category(request, category_slug):
    """
    AJAX endpoint to fetch reels by category.
    """
    videos = ReelVideo.objects.filter(
        category__slug=category_slug,
        is_published=True
    ).values('title', 'slug', 'thumbnail', 'video', 'duration')

    data = {
        'videos': list(videos),
        'count': videos.count(),
    }
    return JsonResponse(data)


# =============================================================================
# ADMIN DASHBOARD VIEWS
# =============================================================================


def edit_gallery_category(request, id):

    category = get_object_or_404(
        GalleryCategory,
        id=id
    )

    if request.method == 'POST':

        category.name = request.POST.get('name', '')

        category.description = request.POST.get(
            'description',
            ''
        )

        category.display_order = int(
            request.POST.get('display_order') or 0
        )

        category.save()

        return redirect(
            'dashboard_gallery_categories'
        )

    return render(
        request,
        'main/dashboard/edit_gallery_category.html',
        {
            'category': category
        }
    )


def delete_gallery_category(request, category_id):

    category = get_object_or_404(
        GalleryCategory,
        id=category_id
    )

    category.delete()

    return redirect(
        'dashboard_gallery_categories'
    )

def _get_dashboard_stats():
    """
    Helper to compute common dashboard statistics.
    Called by every admin view so the sidebar stat cards always have data.
    """
    return {
        'total_bookings': Booking.objects.count(),
        'total_contacts': Contact.objects.count(),
        'total_gallery_images': GalleryImage.objects.count(),
        'total_reels': ReelVideo.objects.count(),
        'total_services': Service.objects.count(),
        'total_testimonials': Testimonial.objects.count(),
        'pending_bookings': Booking.objects.filter(status='pending').count(),
        'completed_bookings': Booking.objects.filter(status='completed').count(),
        'services_list': Service.objects.order_by('display_order'),
    }


def _get_booked_dates_json():
    """
    Helper to serialize booked event dates for the Alpine.js calendar.
    Returns a JSON string like: '["2026-05-10", "2026-05-15"]'
    """
    dates = Booking.objects.exclude(
        event_date__isnull=True
    ).values_list('event_date', flat=True)
    formatted = [d.isoformat() for d in dates if d]
    return json.dumps(formatted)


def _get_bookings_json():
    """
    Helper to serialize all bookings for the Alpine.js table.
    Preserves name, email, date, slot, service, and status.
    """
    bookings = Booking.objects.select_related('service').order_by('-created_at')
    data = []
    for b in bookings:
        data.append({
            'id': b.id,
            'name': b.name,
            'email': b.email,
            'date': str(b.event_date) if b.event_date else 'TBD',
            'slot': b.time_slot or 'N/A',
            'service': b.service.title if b.service else 'Custom',
            'status': b.status,
        })
    return json.dumps(data)


def _get_reels_json():
    """
    Helper to serialize video reels for any Alpine.js widgets.
    """
    reels = ReelVideo.objects.select_related('category').order_by('-created_at')
    data = []
    for r in reels:
        data.append({
            'id': r.id,
            'title': r.title,
            'category': r.category.name if r.category else '',
            'thumbnail': r.thumbnail.url if r.thumbnail else '',
            'video': r.video.url if r.video else '',
            'duration': r.duration or '',
        })
    return json.dumps(data)


@login_required(login_url='admin_login')
def admin_dashboard(request):
    """
    Admin Dashboard Overview.
    Fetches:
      - Count statistics (bookings, contacts, gallery, reels, services, testimonials)
      - Pending vs completed booking counts
      - Latest 5 bookings (for recent activity + bookings table)
      - Latest 5 contact messages
      - Latest 5 gallery uploads
      - Latest 3 video reels
      - Booked dates for the calendar
    """
    context = _get_dashboard_stats()

    # Recent data for quick-glance widgets
    context['recent_bookings'] = Booking.objects.select_related('service').order_by('-created_at')[:5]
    context['recent_contacts'] = Contact.objects.order_by('-created_at')[:5]
    context['recent_gallery'] = GalleryImage.objects.select_related('category').order_by('-created_at')[:5]
    context['recent_reels'] = ReelVideo.objects.select_related('category').order_by('-created_at')[:3]

    # All data needed for tabs that might be visited from this page
    context['bookings'] = Booking.objects.select_related('service').order_by('-created_at')
    context['gallery_images'] = GalleryImage.objects.select_related('category').order_by('-created_at')
    context['gallery_categories'] = GalleryCategory.objects.filter(is_active=True)
    context['reels'] = ReelVideo.objects.select_related('category').order_by('-created_at')
    context['inquiries'] = Inquiry.objects.all().order_by('-created_at')
    context['contacts'] = Contact.objects.order_by('-created_at')
    context['testimonials_list'] = Testimonial.objects.order_by('-created_at')

    # JSON data for Alpine.js interactivity
    context['bookings_json'] = _get_bookings_json()
    context['reels_json'] = _get_reels_json()
    context['booked_dates_json'] = _get_booked_dates_json()

    # Which tab is active when this view loads
    context['active_tab'] = 'dashboard'

    return render(request, 'main/admin_dashboard.html', context)


@login_required(login_url='admin_login')
def admin_bookings(request):
    """
    Admin Bookings Page.
    Fetches:
      - All bookings ordered by newest first
      - Booking statistics
      - Booked dates for calendar integration
    """
    context = _get_dashboard_stats()
    context['bookings'] = Booking.objects.select_related('service').order_by('-created_at')
    context['bookings_json'] = _get_bookings_json()
    context['booked_dates_json'] = _get_booked_dates_json()
    context['active_tab'] = 'manage_bookings'
    return render(request, 'main/admin_dashboard.html', context)


@login_required(login_url='admin_login')
def admin_gallery(request):
    """
    Admin Gallery Page.
    Fetches:
      - All gallery images with category
      - All active gallery categories (for dropdowns/filters)
      - Gallery statistics
    """
    context = _get_dashboard_stats()
    context['gallery_images'] = GalleryImage.objects.select_related('category').order_by('-created_at')
    context['gallery_categories'] = GalleryCategory.objects.filter(is_active=True).order_by('display_order')
    context['reels'] = ReelVideo.objects.select_related('category').order_by('-created_at')
    context['reels_json'] = _get_reels_json()
    context['active_tab'] = 'upload_images'
    return render(request, 'main/admin_dashboard.html', context)


@login_required(login_url='admin_login')
def admin_services(request):
    """
    Admin Services / Pricing Page.
    Fetches:
      - All active services ordered by display order
      - Service statistics
    """
    context = _get_dashboard_stats()
    context['active_tab'] = 'pricing'
    return render(request, 'main/admin_dashboard.html', context)


@login_required(login_url='admin_login')
def admin_contacts(request):
    """
    Admin Contacts / Messages Page.
    Fetches:
      - All contact messages ordered by newest first
      - Unread count for badges
    """
    context = _get_dashboard_stats()
    context['contacts'] = Contact.objects.order_by('-created_at')
    context['unread_contacts'] = Contact.objects.filter(is_read=False).count()
    context['active_tab'] = 'wa_settings'
    return render(request, 'main/admin_dashboard.html', context)


@login_required(login_url='admin_login')
def admin_testimonials(request):
    """
    Admin Testimonials Page.
    Fetches:
      - All testimonials ordered by newest first
      - Testimonial statistics
    """
    context = _get_dashboard_stats()
    context['testimonials_list'] = Testimonial.objects.order_by('-created_at')
    context['active_tab'] = 'dashboard'  # Testimonials shown in dashboard context
    return render(request, 'main/admin_dashboard.html', context)


# =============================================================================
# AI CHATBOT BOOKING ENDPOINT
# =============================================================================
def ai_booking(request):
    """
    POST endpoint for the AI chatbot / booking widget.
    Accepts JSON with booking details and creates a real Booking record.
    No login required — public bookings from the website.
    """
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'POST required'}, status=405)

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'Invalid JSON'}, status=400)

    # Extract fields from frontend
    name = data.get('name', '').strip()
    email = data.get('email', '').strip()
    phone = data.get('phone', '').strip()
    service_type_raw = data.get('service_type', '').strip()
    event_date_str = data.get('event_date', '').strip()
    time_slot = data.get('time_slot', '').strip()
    hours = data.get('hours', '')
    message = data.get('message', '').strip()

    if not name:
        return JsonResponse({'success': False, 'error': 'Name is required'}, status=400)

    # Map frontend value to model service_type
    service_type_map = {
        'wedding': 'wedding',
        'prewedding': 'pre-wedding',
        'commercial': 'commercial',
        'portrait': 'portrait',
        'event': 'event',
        'birthday': 'birthday',
        'baby-shower': 'baby-shower',
        'other': 'other',
    }
    service_type = service_type_map.get(service_type_raw, service_type_raw)

    # Look up Service by service_type
    try:
        service = Service.objects.get(service_type=service_type)
    except Service.DoesNotExist:
        # Fallback: use first available service so booking is never lost
        service = Service.objects.first()
        if not service:
            return JsonResponse({'success': False, 'error': 'No services configured'}, status=400)

    # Parse date if provided
    from datetime import datetime
    event_date = None
    if event_date_str:
        try:
            event_date = datetime.strptime(event_date_str, '%Y-%m-%d').date()
        except ValueError:
            pass

    # Build message with extra info
    full_message = message
    if hours:
        full_message = f"Duration: {hours} hours. {full_message}".strip()

    # Create booking
    booking = Booking.objects.create(
        name=name,
        email=email or 'guest@luxe.com',
        phone=phone,
        service=service,
        event_date=event_date,
        time_slot=time_slot,
        message=full_message,
        status='pending',
    )

    return JsonResponse({
        'success': True,
        'booking_id': booking.id,
        'message': 'Booking received successfully',
        'status': booking.status,
    })


# =============================================================================
# AI CHATBOT OPENAI ENDPOINT
# =============================================================================

def ai_chat(request):
    """
    POST endpoint for the AI chatbot.
    Receives user message, sends to OpenAI with dynamic business context,
    and returns AI reply as JSON.
    No login required.
    """
    if request.method != 'POST':
        return JsonResponse({'reply': 'Please use POST.'}, status=405)

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'reply': 'Invalid message format.'}, status=400)

    user_message = data.get('message', '').strip()
    if not user_message:
        return JsonResponse({'reply': 'Please type a message.'}, status=400)

    # -------------------------------------------------------------------------
    # Build dynamic business context from Django database
    # -------------------------------------------------------------------------
    services = Service.objects.filter(is_active=True).select_related()
    service_lines = []
    for svc in services:
        features = ', '.join(svc.features) if isinstance(svc.features, list) else str(svc.features)
        price_note = svc.price_note or 'Fixed price'
        short_desc = svc.get_short_description_text()[:120]
        service_lines.append(
            f"- {svc.title} ({svc.get_service_type_display()}): {price_note} {svc.formatted_price()}. "
            f"Features: {features}. {short_desc}"
        )
    services_text = '\n'.join(service_lines) if service_lines else 'Contact us for package details.'

    # -------------------------------------------------------------------------
    # System prompt with real business data
    # -------------------------------------------------------------------------
    system_prompt = f"""You are LUXE AI Concierge — the official AI assistant for Dhrumil Bajak Photography, a premium cinematic photography studio based in Gujarat, India.

BUSINESS CONTEXT (from live database):
Available Services & Pricing:
{services_text}

Studio Details:
- Brand: Dhrumil Bajak Photography (LUXE PHOTO)
- Location: Gujarat, India
- Specialties: Wedding cinematography, pre-wedding films, baby showers, maternity shoots, commercial projects, portrait sessions, birthday events
- Style: Premium, cinematic, storytelling-focused
- Contact: WhatsApp +91 99980 01549, Instagram @dhrumil_bajak
- Booking: Users can book directly through the website booking flow

STRICT INSTRUCTIONS:
- Answer only questions related to Dhrumil Bajak Photography, its services, pricing, portfolio, booking process, availability guidance, or studio contact information.
- If the user asks about anything unrelated to photography or this studio, politely redirect: "I can help with photography services, portfolio details, and booking for Dhrumil Bajak Photography."
- Stay elegant, helpful, warm, and concise.
- Use only the pricing and service data from the context above.
- If a user asks about a service not listed, say: "We can create a custom package for you. Let me connect you with the team."
- If user asks about availability, encourage them to use the booking widget or contact the studio directly.
- If user wants to book, guide them step by step: ask for name, service type, preferred date, and time slot.
- Never make up prices or facts.
- Respond in the same language the user uses (English, Hindi, or Gujarati).
"""

    # -------------------------------------------------------------------------
    # Call OpenAI API
    # -------------------------------------------------------------------------
    api_key = settings.GEMINI_API_KEY
    if not api_key:
        return JsonResponse({
            'reply': 'AI assistant is currently offline. Please contact us on WhatsApp at +91 99980 01549.'
        }, status=503)

    try:
        from google import genai
        from google.genai import types

        client = genai.Client(api_key=api_key)

        response = client.models.generate_content(
        model="gemini-2.5-flash-lite",
        contents=user_message,
        config=types.GenerateContentConfig(
            system_instruction=system_prompt,
            max_output_tokens=settings.GEMINI_MAX_TOKENS,
            temperature=0.7,
        ),
    )
        ai_reply = response.text.strip()

    except Exception as e:
        # Log error for debugging but return a graceful message
        print(f'Gemini API error: {e}')
        return JsonResponse({
            'reply': 'I apologize, I am having trouble connecting to my knowledge base right now. '
                     'Please reach out on WhatsApp at +91 99980 01549 and we will assist you immediately.'
        }, status=500)

    return JsonResponse({'reply': ai_reply})


def _parse_service_features(raw_value):
    """Parse features from newline-separated text or JSON."""
    if not raw_value:
        return []
    raw_value = raw_value.strip()
    if raw_value.startswith('['):
        try:
            parsed = json.loads(raw_value)
            if isinstance(parsed, list):
                return [str(item).strip() for item in parsed if str(item).strip()]
        except json.JSONDecodeError:
            pass
    return [line.strip() for line in raw_value.splitlines() if line.strip()]


def _apply_service_form_data(service, request, is_create=False):
    """Apply POST/FILES fields from dashboard service forms onto a Service instance."""
    title = request.POST.get('title', '').strip()
    if title:
        service.title = title

    service.service_type = request.POST.get('service_type', service.service_type)

    price_raw = request.POST.get('price', '').strip()
    if price_raw:
        try:
            service.price = Decimal(price_raw)
        except Exception:
            service.price = 0

    service.price_note = request.POST.get('price_note', '').strip()
    service.tagline = request.POST.get('tagline', '').strip()
    service.short_description = request.POST.get('short_description', '').strip()
    service.full_description = request.POST.get('full_description', '').strip()
    service.duration = request.POST.get('duration', '').strip()

    description = request.POST.get('description', '').strip()
    if description:
        service.description = description
    elif service.full_description:
        service.description = service.full_description
    elif service.short_description:
        service.description = service.short_description
    elif is_create:
        service.description = service.title

    features_raw = request.POST.get('features', '')
    if features_raw:
        service.features = _parse_service_features(features_raw)
    elif is_create:
        service.features = []

    display_order = request.POST.get('display_order')
    if display_order not in (None, ''):
        service.display_order = int(display_order)

    service.is_featured = request.POST.get('is_featured') == 'on'
    service.is_active = request.POST.get('is_active') == 'on' if not is_create else request.POST.get('is_active', 'on') == 'on'

    if request.FILES.get('image'):
        service.image = request.FILES['image']
    if request.FILES.get('cover_image'):
        service.cover_image = request.FILES['cover_image']


@login_required(login_url='admin_login')
def admin_create_service(request):
    """Create a new service from the dashboard form."""
    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        description = request.POST.get('description', '').strip()
        if not title:
            messages.error(request, 'Service title is required.')
            return render(request, 'main/dashboard/create_service.html')

        service = Service(
            title=title,
            description=description or title,
        )
        _apply_service_form_data(service, request, is_create=True)
        service.save()
        messages.success(request, f'Service "{service.title}" created successfully.')
        return redirect('admin_services')

    return render(request, 'main/dashboard/create_service.html')


@login_required(login_url='admin_login')
def dashboard_update_service(request, service_id):
    """Update an existing service with all dashboard fields."""
    service = get_object_or_404(Service, id=service_id)

    if request.method == 'POST':
        _apply_service_form_data(service, request)
        service.save()
        messages.success(request, f'Service "{service.title}" updated successfully.')
        return redirect('admin_services')

    return render(request, 'main/dashboard/update_service.html', {
        'service': service,
    })


@login_required(login_url='admin_login')
@require_POST
def dashboard_sync_service_prices(request):
    """Sync price updates from the admin pricing tab to the database."""
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'message': 'Invalid JSON'}, status=400)

    updates = data.get('services', [])
    if not updates:
        return JsonResponse({'success': False, 'message': 'No services to update'}, status=400)

    updated = 0
    for item in updates:
        service_id = item.get('id')
        price = item.get('price')
        if service_id is None or price is None:
            continue
        try:
            service = Service.objects.get(pk=service_id)
            service.price = price
            service.save(update_fields=['price', 'updated_at'])
            updated += 1
        except Service.DoesNotExist:
            continue

    return JsonResponse({
        'success': True,
        'message': f'Updated {updated} service price(s).',
        'updated': updated,
    })

def dashboard_inquiries(request):
    inquiries = Inquiry.objects.all().order_by('-created_at')
    print("in dashboard_inquiries ........")
    return render(request, 'main/dashboard/inquiries.html', {
        'inquiries': inquiries
    })
@require_POST
def dashboard_update_inquiry_status(request):
    inquiry_id = request.POST.get('id')
    status = request.POST.get('status')

    try:
        inquiry = Inquiry.objects.get(id=inquiry_id)
        inquiry.status = status
        inquiry.save()

        return JsonResponse({
            'success': True,
            'message': 'Inquiry status updated successfully'
        })

    except Inquiry.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Inquiry not found'
        })
    

from django.http import JsonResponse
from django.views.decorators.http import require_POST

@require_POST
def save_chatbot_config(request):

    config, created = ChatbotConfiguration.objects.get_or_create(id=1)

    config.welcome_message = request.POST.get(
        'welcome_message',
        ''
    )

    config.system_prompt = request.POST.get(
        'system_prompt',
        ''
    )

    config.save()

    return JsonResponse({
        'success': True
    })