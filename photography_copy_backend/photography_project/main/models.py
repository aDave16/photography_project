from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver


# =============================================================================
# 1. GALLERY CATEGORY
# =============================================================================
class GalleryCategory(models.Model):
    """
    Categories for organizing gallery images.
    Example: Wedding, Portrait, Commercial, etc.
    """
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True, max_length=100, blank=True)
    description = models.TextField(blank=True)
    display_order = models.PositiveIntegerField(default=0)

    icon = models.CharField(
        max_length=50,
        blank=True,
        help_text="Font Awesome icon class, e.g., 'fa-heart'"
    )
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['display_order', 'name']
        verbose_name = 'Gallery Category'
        verbose_name_plural = 'Gallery Categories'

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

class GalleryProject(models.Model):
    category = models.ForeignKey(
        'GalleryCategory',
        on_delete=models.CASCADE,
        related_name='projects'
    )

    client_name = models.CharField(max_length=200)

    title = models.CharField(max_length=200)

    slug = models.SlugField(unique=True)

    caption = models.TextField(blank=True)

    cover_image = models.ImageField(
        upload_to='gallery/projects/'
    )

    is_featured = models.BooleanField(default=False)

    display_order = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['display_order', '-created_at']

    def __str__(self):
        return self.title
# =============================================================================
# 2. GALLERY IMAGE
# =============================================================================
class GalleryImage(models.Model):
    """
    Individual photographs that appear in the gallery grid.
    Each image belongs to one category.
    """
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, max_length=200, blank=True)
    category = models.ForeignKey(
        GalleryCategory,
        on_delete=models.CASCADE,
        related_name='images',
        null=True,
        blank=True
    )
    image = models.ImageField(
        upload_to='gallery/images/%Y/%m/',
        help_text="Upload high-resolution photo"
    )
    thumbnail = models.ImageField(
        upload_to='gallery/thumbnails/%Y/%m/',
        blank=True,
        null=True,
        help_text="Optional smaller thumbnail version"
    )
    caption = models.CharField(max_length=300, blank=True)
    description = models.TextField(blank=True)
    location = models.CharField(max_length=200, blank=True)
    date_taken = models.DateField(blank=True, null=True)
    display_order = models.PositiveIntegerField(default=0)

    is_featured = models.BooleanField(
        default=False,
        help_text="Featured images appear on homepage and priority sections"
    )
    is_published = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-is_featured', 'order', '-created_at']
        verbose_name = 'Gallery Image'
        verbose_name_plural = 'Gallery Images'

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            slug = base_slug
            counter = 1
            while GalleryImage.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('gallery_detail', kwargs={'slug': self.slug})


# =============================================================================
# 3. REEL CATEGORY
# =============================================================================
class ReelCategory(models.Model):
    """
    Categories for organizing video reels.
    Example: Behind the Scenes, Short Films, Client Stories
    """
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True, max_length=100, blank=True)
    description = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    display_order = models.PositiveIntegerField(default=0)


    class Meta:
        ordering = ['order', 'name']
        verbose_name = 'Reel Category'
        verbose_name_plural = 'Reel Categories'

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


# =============================================================================
# 4. REEL VIDEO
# =============================================================================
class ReelVideo(models.Model):
    """
    Video reels / short films displayed on the reels section.
    Supports MP4 upload with optional thumbnail poster image.
    """
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, max_length=200, blank=True)
    category = models.ForeignKey(
        ReelCategory,
        on_delete=models.SET_NULL,
        related_name='videos',
        null=True,
        blank=True
    )
    video = models.FileField(
        upload_to='reels/videos/%Y/%m/',
        help_text="Upload MP4 video file"
    )
    thumbnail = models.ImageField(
        upload_to='reels/thumbnails/%Y/%m/',
        blank=True,
        null=True,
        help_text="Poster image shown before video plays"
    )
    description = models.TextField(blank=True)
    duration = models.CharField(
        max_length=20,
        blank=True,
        help_text="e.g., '0:45' or '2:30'"
    )
    views_count = models.PositiveIntegerField(default=0)
    is_featured = models.BooleanField(
        default=False,
        help_text="Featured reels appear in the hero reel section"
    )
    is_published = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-is_featured', 'order', '-created_at']
        verbose_name = 'Reel Video'
        verbose_name_plural = 'Reel Videos'

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            slug = base_slug
            counter = 1
            while ReelVideo.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


# =============================================================================
# 5. SERVICE
# =============================================================================
class Service(models.Model):
    """
    Photography services/packages offered to clients.
    Example: Wedding Package, Portrait Session, Commercial Shoot
    """
    SERVICE_TYPE_CHOICES = [
        ('portrait', 'Portrait'),
        ('wedding', 'Wedding'),
        ('commercial', 'Commercial'),
        ('event', 'Event'),
        ('pre-wedding', 'Pre-Wedding'),
        ('baby-shower', 'Baby Shower'),
        ('birthday', 'Birthday'),
        ('other', 'Other'),
    ]

    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, max_length=200, blank=True)
    service_type = models.CharField(
        max_length=50,
        choices=SERVICE_TYPE_CHOICES,
        default='wedding'
    )
    tagline = models.CharField(
        max_length=300,
        blank=True,
        help_text="Short catchy line under the title"
    )
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        help_text="Base price in your currency"
    )
    price_note = models.CharField(
        max_length=100,
        blank=True,
        help_text="e.g., 'Starting from' or 'per hour'"
    )
    description = models.TextField()
    features = models.JSONField(
        default=list,
        help_text="List of features as JSON: ['Feature 1', 'Feature 2']"
    )
    icon = models.ImageField(
        upload_to='services/icons/',
        blank=True,
        null=True,
        help_text="Service icon or representative image"
    )
    image = models.ImageField(
        upload_to='services/images/',
        blank=True,
        null=True,
        help_text="Hero image for service card"
    )
    duration = models.CharField(
        max_length=100,
        blank=True,
        help_text="e.g., '3 Hour Session' or 'Full Day Coverage'"
    )
    short_description = models.TextField(
        blank=True,
        help_text="Brief description for service cards (max 150 words)"
    )
    full_description = models.TextField(
        blank=True,
        help_text="Detailed description for service detail page"
    )
    cover_image = models.ImageField(
        upload_to='services/covers/',
        blank=True,
        null=True,
        help_text="Main cover image for service"
    )
    gallery_images = models.JSONField(
        default=list,
        blank=True,
        help_text="List of gallery image URLs"
    )
    display_order = models.PositiveIntegerField(
        default=0,
        help_text="Order for display on services page"
    )
    is_featured = models.BooleanField(
        default=False,
        help_text="Featured services appear prominently on the services page"
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['display_order', '-is_featured', '-created_at']
        verbose_name = 'Service'
        verbose_name_plural = 'Services'

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            slug = base_slug
            counter = 1
            while Service.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        """Get the absolute URL for this service"""
        return reverse('service_detail', kwargs={'slug': self.slug})

    def formatted_price(self):
        """Return formatted price with currency symbol"""
        if self.price:
            return f"₹{int(self.price):,}"
        return "Price on request"

    def get_main_image(self):
        """Get the main image for this service (cover_image, fallback to image)"""
        if self.cover_image:
            return self.cover_image.url
        elif self.image:
            return self.image.url
        return None

    def get_features_list(self):
        """Return features as a clean list"""
        if isinstance(self.features, list):
            return self.features
        elif isinstance(self.features, str):
            try:
                import json
                return json.loads(self.features)
            except:
                return []
        return []

    def get_short_description_text(self):
        """Get short description, fallback to truncated description"""
        if self.short_description:
            return self.short_description
        elif self.description:
            words = self.description.split()
            if len(words) > 30:
                return ' '.join(words[:30]) + '...'
            return self.description
        return ""

    def get_full_description_text(self):
        """Get full description, fallback to description"""
        if self.full_description:
            return self.full_description
        return self.description


# =============================================================================
# 6. BOOKING
# =============================================================================
class Booking(models.Model):
    """
    Client booking inquiries submitted through the website.
    Admins can approve, reject, or mark as completed.
    """
    SERVICE_CHOICES = [
        ('wedding', 'The Legacy (Wedding)'),
        ('pre-wedding', 'Pre-Wedding'),
        ('baby-shower', 'Baby Shower'),
        ('birthday', 'Birthday'),
        ('portrait', 'The Editorial (Portrait)'),
        ('commercial', 'The Visionary (Commercial)'),
        ('event', 'Event Coverage'),
        ('other', 'Other'),
    ]

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('confirmed', 'Confirmed'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('rejected', 'Rejected'),
    ]

    name = models.CharField(max_length=200)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True)
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='bookings')
    event_date = models.DateField(blank=True, null=True)
    time_slot = models.CharField(max_length=50, blank=True)
    location = models.CharField(max_length=300, blank=True)
    message = models.TextField(blank=True)
    budget_range = models.CharField(
        max_length=100,
        blank=True,
        help_text="e.g., '$1,000 - $2,000'"
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )
    admin_notes = models.TextField(
        blank=True,
        help_text="Internal notes visible only in admin"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Booking'
        verbose_name_plural = 'Bookings'

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='bookings'
    )
    payment_status = models.CharField(
        max_length=20,
        choices=[
            ('unpaid', 'Unpaid'),
            ('paid', 'Paid'),
            ('pending', 'Pending'),
            ('refunded', 'Refunded'),
        ],
        default='unpaid'
    )

    def __str__(self):
        return f"{self.name} | {self.get_service_display()} | {self.status}"


class Availability(models.Model):
    BLOCK_TYPE_CHOICES = [
        ('fully_booked', 'Fully Booked'),
        ('holiday', 'Holiday'),
        ('personal_leave', 'Personal Leave'),
        ('maintenance', 'Maintenance'),
        ('custom', 'Custom Block'),
    ]

    date = models.DateField(unique=True)
    is_available = models.BooleanField(default=True)
    is_blocked_by_admin = models.BooleanField(default=False)
    block_type = models.CharField(max_length=30, choices=BLOCK_TYPE_CHOICES, blank=True)
    reason = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['date']
        verbose_name = 'Availability'
        verbose_name_plural = 'Availabilities'

    def __str__(self):
        return f"{self.date} - {self.get_block_type_display() or 'Blocked'}"


# ------------------------------
# Signals: keep Availability in sync with Bookings
# ------------------------------


@receiver(post_save, sender=Booking)
def update_availability_on_booking_save(sender, instance, **kwargs):
    """When a booking is created or updated, ensure Availability for that date reflects bookings."""
    event_date = instance.event_date
    if not event_date:
        return

    # Count bookings that should mark the date as booked
    booked_count = Booking.objects.filter(
        event_date=event_date,
        status__in=['pending', 'approved', 'confirmed']
    ).count()

    try:
        avail, created = Availability.objects.get_or_create(date=event_date)
        # If admin manually blocked the date, keep that flag but ensure availability is false
        if avail.is_blocked_by_admin:
            avail.is_available = False
        else:
            avail.is_available = False if booked_count > 0 else True
            avail.is_blocked_by_admin = False
            if booked_count > 0:
                avail.block_type = 'fully_booked'
                avail.reason = 'Auto: bookings'
            else:
                avail.block_type = ''
                avail.reason = ''
        avail.save()
    except Exception:
        # avoid breaking booking flow if availability sync fails
        pass


@receiver(post_delete, sender=Booking)
def update_availability_on_booking_delete(sender, instance, **kwargs):
    """Recalculate availability when a booking is deleted."""
    event_date = instance.event_date
    if not event_date:
        return

    booked_count = Booking.objects.filter(
        event_date=event_date,
        status__in=['pending', 'approved', 'confirmed']
    ).count()

    try:
        avail = Availability.objects.filter(date=event_date).first()
        if not avail:
            return
        if avail.is_blocked_by_admin:
            # preserve manual blocks
            avail.is_available = False
            avail.save()
            return

        if booked_count == 0:
            avail.is_available = True
            avail.block_type = ''
            avail.reason = ''
            avail.save()
        else:
            avail.is_available = False
            avail.block_type = 'fully_booked'
            avail.reason = 'Auto: bookings'
            avail.save()
    except Exception:
        pass


class BlockedDateRange(models.Model):
    """Represents an admin-blocked date or a blocked date range."""
    start_date = models.DateField()
    end_date = models.DateField()
    reason = models.CharField(max_length=255, blank=True)
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name='blocked_ranges'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-start_date']
        verbose_name = 'Blocked Date Range'
        verbose_name_plural = 'Blocked Date Ranges'

    def __str__(self):
        if self.start_date == self.end_date:
            return f"Blocked: {self.start_date}"
        return f"Blocked: {self.start_date} → {self.end_date}"


class BookingSlot(models.Model):
    name = models.CharField(max_length=50, unique=True)
    label = models.CharField(max_length=100)
    order = models.PositiveIntegerField(default=0)
    capacity = models.PositiveIntegerField(default=1)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order', 'name']
        verbose_name = 'Booking Slot'
        verbose_name_plural = 'Booking Slots'

    def __str__(self):
        return self.label


# =============================================================================
# 7. CONTACT
# =============================================================================
class Contact(models.Model):
    """
    Contact form messages submitted by website visitors.
    """
    SUBJECT_CHOICES = [
        ('wedding', 'The Legacy (Wedding)'),
        ('pre-wedding', 'Pre-Wedding'),
        ('baby-shower', 'Baby Shower'),
        ('birthday', 'Birthday'),
        ('portrait', 'The Editorial (Portrait)'),
        ('commercial', 'The Visionary (Commercial)'),
        ('collaboration', 'Collaboration'),
        ('general', 'General Inquiry'),
        ('other', 'Other'),
    ]

    name = models.CharField(max_length=200)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True)
    subject = models.CharField(max_length=50, choices=SUBJECT_CHOICES)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    is_replied = models.BooleanField(default=False)
    admin_notes = models.TextField(
        blank=True,
        help_text="Internal notes for follow-up tracking"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Contact Message'
        verbose_name_plural = 'Contact Messages'

    def __str__(self):
        return f"{self.name} | {self.get_subject_display()}"


# =============================================================================
# 8. TESTIMONIAL
# =============================================================================
class Testimonial(models.Model):
    """
    Client reviews and testimonials displayed on the website.
    """
    RATING_CHOICES = [
        (1, '1 Star'),
        (2, '2 Stars'),
        (3, '3 Stars'),
        (4, '4 Stars'),
        (5, '5 Stars'),
    ]

    client_name = models.CharField(max_length=200)
    client_role = models.CharField(
        max_length=200,
        blank=True,
        help_text="e.g., 'Bride', 'CEO', 'Model'"
    )
    project = models.CharField(
        max_length=200,
        blank=True,
        help_text="e.g., 'Wedding Photography', 'Brand Campaign'"
    )
    testimonial = models.TextField()
    rating = models.IntegerField(
        choices=RATING_CHOICES,
        default=5,
        help_text="Client rating out of 5 stars"
    )
    image = models.ImageField(
        upload_to='testimonials/clients/',
        blank=True,
        null=True,
        help_text="Client photo or project image"
    )
    is_featured = models.BooleanField(
        default=False,
        help_text="Featured testimonials appear in homepage slider"
    )
    is_published = models.BooleanField(default=True)
    display_order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-is_featured', 'display_order', '-created_at']
        verbose_name = 'Testimonial'
        verbose_name_plural = 'Testimonials'

    def __str__(self):
        return f"{self.client_name} | {self.rating} Stars"


# =============================================================================
# 9. HERO SECTION
# =============================================================================
class HeroSection(models.Model):
    """
    Editable homepage hero / banner section.
    Only one instance should be active at a time.
    """
    title = models.CharField(
        max_length=300,
        default="Capturing Moments That Last Forever"
    )
    subtitle = models.TextField(
        blank=True,
        default="Professional photography services for weddings, portraits, and commercial projects"
    )
    cta_text = models.CharField(
        max_length=100,
        default="Book a Session",
        help_text="Call-to-action button text"
    )
    cta_link = models.CharField(
        max_length=200,
        default="/booking/",
        help_text="URL the CTA button links to"
    )
    secondary_cta_text = models.CharField(
        max_length=100,
        blank=True,
        default="View Portfolio",
        help_text="Second button text (optional)"
    )
    secondary_cta_link = models.CharField(
        max_length=200,
        blank=True,
        default="/portfolio/",
        help_text="Second button URL"
    )
    background_image = models.ImageField(
        upload_to='hero/backgrounds/',
        blank=True,
        null=True,
        help_text="Main hero background image"
    )
    background_video = models.FileField(
        upload_to='hero/videos/',
        blank=True,
        null=True,
        help_text="Optional background video (MP4)"
    )
    show_reel_slider = models.BooleanField(
        default=True,
        help_text="Show the reels/video slider in hero"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Only one hero section should be active"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-is_active', '-updated_at']
        verbose_name = 'Hero Section'
        verbose_name_plural = 'Hero Sections'

    def __str__(self):
        return f"Hero: {self.title[:50]}..."

    def save(self, *args, **kwargs):
        """Ensure only one hero section is active at a time."""
        if self.is_active:
            HeroSection.objects.filter(is_active=True).update(is_active=False)
        super().save(*args, **kwargs)


# =============================================================================
# 10. ABOUT SECTION
# =============================================================================
class AboutSection(models.Model):
    """
    Editable About page content.
    Stores photographer bio, story, stats, and images.
    """
    headline = models.CharField(
        max_length=300,
        default="The Story Behind the Lens"
    )
    story = models.TextField(
        default="Share your photography journey and passion here..."
    )
    photographer_name = models.CharField(
        max_length=200,
        default="Your Name"
    )
    photographer_title = models.CharField(
        max_length=200,
        default="Professional Photographer",
        help_text="e.g., 'Wedding & Portrait Photographer'"
    )
    profile_image = models.ImageField(
        upload_to='about/profile/',
        blank=True,
        null=True,
        help_text="Main photographer portrait"
    )
    signature_image = models.ImageField(
        upload_to='about/signature/',
        blank=True,
        null=True,
        help_text="Handwritten signature image"
    )
    experience_years = models.PositiveIntegerField(
        default=5,
        help_text="Years of experience displayed in stats"
    )
    projects_completed = models.PositiveIntegerField(
        default=500,
        help_text="Number of projects for stats counter"
    )
    happy_clients = models.PositiveIntegerField(
        default=300,
        help_text="Number of happy clients for stats counter"
    )
    awards_won = models.PositiveIntegerField(
        default=15,
        help_text="Awards/recognitions count"
    )
    philosophy = models.TextField(
        blank=True,
        help_text="Your photography philosophy or approach"
    )
    equipment = models.TextField(
        blank=True,
        help_text="List of cameras, lenses, and gear you use"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Only one about section should be active"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-is_active', '-updated_at']
        verbose_name = 'About Section'
        verbose_name_plural = 'About Sections'

    def __str__(self):
        return f"About: {self.photographer_name}"

    def save(self, *args, **kwargs):
        """Ensure only one about section is active at a time."""
        if self.is_active:
            AboutSection.objects.filter(is_active=True).update(is_active=False)
        super().save(*args, **kwargs)


# =============================================================================
# INQUIRY MANAGEMENT SYSTEM
# =============================================================================

class Inquiry(models.Model):
    """
    Simple inquiry/contact management for Dhrumil Bajak Photography.
    Handles customer inquiries from the contact form with admin management.
    """
    
    # Event Type Choices
    EVENT_WEDDING = 'wedding'
    EVENT_PREWEDDING = 'pre-wedding'
    EVENT_PORTRAIT = 'portrait'
    EVENT_COMMERCIAL = 'commercial'
    EVENT_BABY_SHOWER = 'baby-shower'
    EVENT_BIRTHDAY = 'birthday'
    EVENT_OTHER = 'other'
    
    EVENT_TYPE_CHOICES = [
        (EVENT_WEDDING, 'The Legacy (Wedding)'),
        (EVENT_PREWEDDING, 'Pre-Wedding'),
        (EVENT_PORTRAIT, 'The Editorial (Portrait)'),
        (EVENT_COMMERCIAL, 'The Visionary (Commercial)'),
        (EVENT_BABY_SHOWER, 'Baby Shower'),
        (EVENT_BIRTHDAY, 'Birthday'),
        (EVENT_OTHER, 'Other'),
    ]
    
    # Required Fields
    name = models.CharField(
        max_length=200,
        help_text="Customer's full name"
    )
    
    email = models.EmailField(
        max_length=254,
        help_text="Customer's email address"
    )
    
    phone = models.CharField(
        max_length=20,
        blank=True,
        help_text="Customer's phone number"
    )
    
    event_type = models.CharField(
        max_length=50,
        choices=EVENT_TYPE_CHOICES,
        default=EVENT_WEDDING,
        help_text="Type of photography service inquiry"
    )
    
    message = models.TextField(
        help_text="Customer's detailed inquiry message"
    )
    
    # Admin Management Fields
    admin_reply = models.TextField(
        blank=True,
        help_text="Admin's reply to the customer"
    )
    
    replied = models.BooleanField(
        default=False,
        help_text="Whether admin has replied to this inquiry"
    )
    
    STATUS_NEW = 'new'
    STATUS_IN_PROGRESS = 'in_progress'
    STATUS_REPLIED = 'replied'
    STATUS_CLOSED = 'closed'

    STATUS_CHOICES = [
        (STATUS_NEW, 'New'),
        (STATUS_IN_PROGRESS, 'In Progress'),
        (STATUS_REPLIED, 'Replied'),
        (STATUS_CLOSED, 'Closed'),
    ]

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_NEW,
        help_text="Current status of the inquiry"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Inquiry'
        verbose_name_plural = 'Inquiries'
    
    def __str__(self):
        return f"Inquiry from {self.name} - {self.get_event_type_display()}"
    
    def get_absolute_url(self):
        """Get admin URL for this inquiry."""
        return f"/admin/main/inquiry/{self.id}/change/"


# =============================================================================
# 11. CHATBOT CONFIGURATION
# =============================================================================
class ChatbotConfiguration(models.Model):
    """
    Singleton model for chatbot settings.
    Stores welcome message, system prompt, and FAQ items.
    """
    welcome_message = models.TextField(
        default="Hello! I am your AI concierge. How can I help you today?",
        help_text="Welcome message displayed when user opens chatbot"
    )
    
    system_prompt = models.TextField(
        default="You are a helpful photography assistant for Dhrumil Bajak Photography.",
        help_text="System prompt for the AI model"
    )
    
    faq_items = models.JSONField(
        default=list,
        blank=True,
        help_text="FAQ items as JSON: [{\"q\": \"Question\", \"a\": \"Answer\"}, ...]"
    )
    
    is_active = models.BooleanField(
        default=True,
        help_text="Enable or disable chatbot"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Chatbot Configuration'
        verbose_name_plural = 'Chatbot Configuration'
    
    def __str__(self):
        return "Chatbot Configuration"
    
    def save(self, *args, **kwargs):
        """Ensure only one chatbot configuration exists."""
        if not self.pk and ChatbotConfiguration.objects.exists():
            ChatbotConfiguration.objects.all().delete()
        super().save(*args, **kwargs)


# =============================================================================
# 12. WHATSAPP CONFIGURATION
# =============================================================================
class WhatsAppConfiguration(models.Model):
    """
    Singleton model for WhatsApp settings.
    Stores WhatsApp number and message template.
    """
    whatsapp_number = models.CharField(
        max_length=20,
        default="919106093868",
        help_text="WhatsApp business number (with country code, no + or spaces)"
    )
    
    message_template = models.TextField(
        default="Hi! I'm inquiring about a {service} session. Est: {price}.",
        help_text="Message template for WhatsApp quotes. Use {service} and {price} placeholders"
    )
    
    is_active = models.BooleanField(
        default=True,
        help_text="Enable or disable WhatsApp contact option"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'WhatsApp Configuration'
        verbose_name_plural = 'WhatsApp Configuration'
    
    def __str__(self):
        return f"WhatsApp: {self.whatsapp_number}"
    
    def save(self, *args, **kwargs):
        """Ensure only one WhatsApp configuration exists."""
        if not self.pk and WhatsAppConfiguration.objects.exists():
            WhatsAppConfiguration.objects.all().delete()
        super().save(*args, **kwargs)


# =============================================================================
# 13. INVOICE
# =============================================================================
class Invoice(models.Model):
    """
    Invoice model for booking-related invoices.
    Tracks invoice generation, payment status, and PDF storage.
    """
    STATUS_CHOICES = [
        ('unpaid', 'Unpaid'),
        ('paid', 'Paid'),
        ('pending', 'Pending'),
        ('refunded', 'Refunded'),
        ('overdue', 'Overdue'),
    ]
    
    booking = models.OneToOneField(
        Booking,
        on_delete=models.CASCADE,
        related_name='invoice',
        help_text="Associated booking"
    )
    
    invoice_number = models.CharField(
        max_length=50,
        unique=True,
        help_text="Unique invoice identifier (e.g., INV-2026-001)"
    )
    
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Invoice total amount"
    )
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='unpaid',
        help_text="Payment status"
    )
    
    pdf_file = models.FileField(
        upload_to='invoices/pdfs/',
        blank=True,
        null=True,
        help_text="Generated PDF invoice file"
    )
    
    notes = models.TextField(
        blank=True,
        help_text="Additional notes or terms"
    )
    
    generated_at = models.DateTimeField(auto_now_add=True)
    paid_at = models.DateTimeField(
        blank=True,
        null=True,
        help_text="Date when payment was received"
    )
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-generated_at']
        verbose_name = 'Invoice'
        verbose_name_plural = 'Invoices'
    
    def __str__(self):
        return f"{self.invoice_number} - {self.booking.name}"
    
    def get_absolute_url(self):
        return f"/admin/main/invoice/{self.id}/change/"
    
    def mark_as_paid(self):
        """Mark invoice as paid and update timestamp."""
        from django.utils import timezone
        self.status = 'paid'
        self.paid_at = timezone.now()
        self.save()

