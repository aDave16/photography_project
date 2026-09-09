"""
Abstract base models for reusable functionality across all models.
These provide common fields like timestamps, SEO, and status management.
"""
from django.db import models
from django.utils.text import slugify
from django.core.exceptions import ValidationError
import os


class TimestampMixin(object):
    """
    Abstract base class for adding timestamp fields to models.
    Automatically tracks when records are created and last updated.
    """
    created_at = models.DateTimeField(auto_now_add=True, help_text="Date and time when record was created")
    updated_at = models.DateTimeField(auto_now=True, help_text="Date and time when record was last updated")

    class Meta:
        abstract = True


class SEOMixin(object):
    """
    Abstract base class for SEO-related fields.
    Helps with search engine optimization.
    """
    slug = models.SlugField(unique=True, max_length=200, help_text="URL-friendly version of title")
    meta_title = models.CharField(max_length=200, blank=True, help_text="SEO title for search engines")
    meta_description = models.TextField(blank=True, help_text="SEO description for search engines")
    meta_keywords = models.CharField(max_length=255, blank=True, help_text="SEO keywords (comma-separated)")

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        """
        Auto-generate slug from title if not provided.
        """
        if not self.slug and hasattr(self, 'title'):
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)


class StatusMixin(object):
    """
    Abstract base class for status management.
    Common status choices for published/unpublished content.
    """
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('archived', 'Archived'),
    ]

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='draft',
        help_text="Current status of the record"
    )

    class Meta:
        abstract = True


class OrderMixin(object):
    """
    Abstract base class for ordering records.
    Used for sorting items in lists.
    """
    order = models.IntegerField(default=0, help_text="Order for sorting (lower number appears first)")

    class Meta:
        abstract = True
        ordering = ['order']


class FeaturedMixin(object):
    """
    Abstract base class for featured items.
    Used to highlight important content.
    """
    is_featured = models.BooleanField(default=False, help_text="Mark as featured to display prominently")

    class Meta:
        abstract = True


def validate_image_extension(value):
    """
    Validator to ensure uploaded files are images.
    """
    ext = os.path.splitext(value.name)[1].lower()
    valid_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp']
    if ext not in valid_extensions:
        raise ValidationError(f'Unsupported file extension. Allowed: {", ".join(valid_extensions)}')


def validate_video_extension(value):
    """
    Validator to ensure uploaded files are videos.
    """
    ext = os.path.splitext(value.name)[1].lower()
    valid_extensions = ['.mp4', '.mov', '.avi', '.webm', '.mkv']
    if ext not in valid_extensions:
        raise ValidationError(f'Unsupported file extension. Allowed: {", ".join(valid_extensions)}')


class ImageUploadMixin(object):
    """
    Abstract base class for models with image uploads.
    Includes validation for file types.
    """
    class Meta:
        abstract = True


class VideoUploadMixin(object):
    """
    Abstract base class for models with video uploads.
    Includes validation for file types.
    """
    class Meta:
        abstract = True
