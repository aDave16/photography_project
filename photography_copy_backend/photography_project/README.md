# Photography Website - Django Backend

A professional photography website backend built with Django, featuring dynamic gallery management, booking system, contact forms, REST API support, AI chatbot integration, and real-time WebSocket support.

## Project Overview

This is a production-ready Django backend for a photography portfolio and booking website. It includes:

- Custom User Model with roles
- Gallery system with categories and multiple images
- Service/Packages management with pricing
- Booking system with calendar availability
- Contact form with priority levels
- Testimonials with ratings
- Reels/Video management
- REST API with Django REST Framework
- Professional admin panel
- AI Chatbot integration (OpenAI)
- WebSocket/Channels support for real-time features
- Payment integration structure
- Email notification system

## Project Structure

```
photography_project/
├── manage.py
├── db.sqlite3
├── .env                          # Environment variables
├── .gitignore
├── requirements.txt
├── photography_project/          # Project configuration
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
├── main/                         # Main Django app
│   ├── __init__.py
│   ├── admin.py                  # Admin configurations
│   ├── api_urls.py               # API URL routing
│   ├── api_views.py              # API view functions
│   ├── apps.py
│   ├── base_models.py            # Abstract base classes
│   ├── consumers.py              # WebSocket consumers
│   ├── forms.py                  # Django forms
│   ├── management/               # Custom management commands
│   ├── migrations/               # Database migrations
│   ├── models.py                 # Database models
│   ├── routing.py                # WebSocket routing
│   ├── serializers.py            # REST API serializers
│   ├── static/                   # Static files (CSS, JS, images, videos)
│   │   ├── css/
│   │   ├── js/
│   │   ├── images/
│   │   └── videos/
│   ├── templates/                # HTML templates
│   │   └── main/
│   ├── urls.py                   # URL configurations
│   ├── views.py                  # Main view functions
│   ├── views_booking.py          # Booking-specific views
│   ├── views_dashboard.py        # Dashboard views
│   └── views_inquiry.py          # Inquiry views
├── accounts/                     # Authentication app
│   ├── admin.py
│   ├── apps.py
│   ├── forms.py
│   ├── migrations/
│   ├── models.py
│   ├── templates/
│   ├── urls.py
│   └── views.py
├── payments/                     # Payment integration app
│   ├── admin.py
│   ├── apps.py
│   ├── migrations/
│   ├── models.py
│   ├── urls.py
│   └── views.py
├── media/                        # User uploaded files
│   └── gallery/
└── venv/                         # Virtual environment (DO NOT DELETE)
```

## Technology Stack

- **Backend Framework**: Django 4.2+
- **REST API**: Django REST Framework
- **Database**: SQLite (development), MySQL (production-ready)
- **Real-time**: Django Channels
- **AI Integration**: OpenAI API
- **Authentication**: Django Auth System
- **Static Files**: Django static files system
- **Media Files**: Django media files system

## Installation

### Prerequisites

- Python 3.8 or higher installed
- pip (Python package manager)

### 1. Navigate to Project Directory

```bash
cd photography_project
```

### 2. Create Virtual Environment

```bash
python -m venv venv
```

### 3. Activate Virtual Environment

**On Windows:**
```bash
venv\Scripts\activate
```

**On Mac/Linux:**
```bash
source venv/bin/activate
```

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

### 5. Environment Variables

Create a `.env` file in the project root with the following variables:

```env
DJANGO_SECRET_KEY=your-secret-key-here
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=localhost 127.0.0.1
CSRF_TRUSTED_ORIGINS=http://localhost:8000

# OpenAI Configuration (optional)
OPENAI_API_KEY=your-openai-api-key
OPENAI_MODEL=gpt-4o-mini
OPENAI_MAX_TOKENS=300

# Email Configuration (optional)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=your-email@gmail.com
DEFAULT_FROM_NAME=Dhrumil Bajak Photography
ADMIN_EMAIL=bajakdhrumil@gmail.com
```

### 6. Run Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### 7. Create Superuser (Admin Account)

```bash
python manage.py createsuperuser
```

Follow the prompts to create username, email, and password.

### 8. Collect Static Files (Optional for Development)

```bash
python manage.py collectstatic
```

### 9. Run Development Server

```bash
python manage.py runserver
```

### 10. Access the Application

- **Website:** http://127.0.0.1:8000/
- **Admin Panel:** http://127.0.0.1:8000/admin/
- **API Endpoints:** http://127.0.0.1:8000/api/

## Features

### Core Features

- **Dynamic Gallery**: Manage photo projects through admin panel
- **Booking System**: Accept and manage booking inquiries with calendar availability
- **Contact Forms**: Collect and manage contact messages with priority levels
- **Services Management**: Display photography services and pricing
- **Admin Panel**: Full Django admin interface with custom actions
- **REST API**: Built-in API endpoints for mobile/frontend integration
- **Image Upload**: Easy image management through admin
- **Reels/Video Management**: Upload and manage video content
- **Testimonials**: Client reviews with ratings
- **AI Chatbot**: OpenAI-powered chatbot integration
- **WebSocket Support**: Real-time features via Django Channels

### Advanced Features

- **Calendar Booking System**: Real-time availability management
- **Payment Integration**: Structure for Stripe/Razorpay integration
- **Email Notifications**: Automated email system
- **User Authentication**: Custom user model with roles
- **Dashboard**: Admin dashboard for managing bookings, inquiries, and content
- **API Authentication**: Token-based authentication for API endpoints
- **Static/Media File Management**: Organized file structure

## Admin Panel Usage

1. Login with superuser credentials at `/admin/`
2. Add Services under "Services" section
3. Create Gallery projects under "Gallery" section
4. Upload images to each gallery project
5. Manage bookings and contact messages
6. Add testimonials
7. Configure chatbot settings
8. Manage calendar availability

## API Endpoints

### Public API

- `GET /api/gallery/` - List all gallery projects
- `GET /api/gallery/<slug>/` - Get specific project
- `GET /api/services/` - List all services
- `GET /api/services/<slug>/` - Get service details
- `GET /api/testimonials/` - List all testimonials
- `POST /api/booking/` - Create booking
- `POST /api/contact/` - Send contact message

### Booking API

- `POST /api/create-booking/` - Create booking
- `GET /api/available-slots/` - Get available time slots
- `GET /api/calendar/` - Get calendar data
- `GET /api/calendar-availability/` - Get calendar availability
- `GET /api/date-details/` - Get details for specific date

### Admin API

- `GET /api/admin/calendar-events/` - Admin calendar events
- `POST /api/admin/bookings/` - Admin create booking
- `POST /api/admin/blocks/` - Create blocked dates
- `POST /api/admin/blocks/toggle/` - Toggle blocked dates
- `GET /api/admin/bookings/<id>/` - Get booking details
- `PUT /api/admin/bookings/<id>/update/` - Update booking
- `POST /api/admin/bookings/<id>/cancel/` - Cancel booking
- `POST /api/admin/bookings/<id>/complete/` - Mark booking complete

### AI Chatbot

- `POST /ai-booking/` - AI booking endpoint
- `POST /ai-chat/` - AI chat endpoint (OpenAI)

## Database

### Development (SQLite)

Currently using SQLite for development. The database file is `db.sqlite3`.

### Production (MySQL)

For production, switch to MySQL by updating `settings.py`:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'photography_db',
        'USER': 'your_mysql_user',
        'PASSWORD': 'your_mysql_password',
        'HOST': 'localhost',
        'PORT': '3306',
    }
}
```

## Static & Media Files

### Static Files

Static files (CSS, JS, images, videos) are located in `main/static/`:

- `css/` - Stylesheets
- `js/` - JavaScript files
- `images/` - Images and main background video
- `videos/` - Reel videos

### Media Files

User-uploaded files are stored in `media/`:

- `gallery/` - Gallery images uploaded via admin
- Other user uploads as configured

### Template Usage

In templates, use:

```html
{% load static %}

<!-- Static files -->
<link rel="stylesheet" href="{% static 'css/style.css' %}">
<script src="{% static 'js/script.js' %}"></script>
<img src="{% static 'images/photo.jpg' %}" alt="Photo">

<!-- Media files (database uploads) -->
<img src="{{ gallery_image.image.url }}" alt="Gallery Image">
```

## Frontend Integration

The backend is designed to work with a separate frontend. Key integration points:

- **API Endpoints**: Use REST API for data fetching
- **Authentication**: Token-based authentication for API
- **Static Files**: Frontend can consume static assets
- **Media Files**: Frontend displays user-uploaded content
- **WebSocket**: Real-time updates via Django Channels

## Chatbot/OpenAI Setup

### Configuration

1. Add OpenAI API key to `.env`:
```env
OPENAI_API_KEY=your-openai-api-key
OPENAI_MODEL=gpt-4o-mini
OPENAI_MAX_TOKENS=300
```

2. The chatbot is already integrated in views.py:
- `/ai-chat/` - Main chat endpoint
- `/ai-booking/` - Booking-specific AI endpoint

### Usage

The chatbot can:
- Handle booking inquiries
- Provide service information
- Answer general questions
- Assist with scheduling

## Deployment

### Production Checklist

1. **Change Debug Mode**: Set `DEBUG = False` in settings.py
2. **Database**: Switch to MySQL/PostgreSQL
3. **Static Files**: Run `collectstatic` and configure web server
4. **Media Files**: Configure media file serving
5. **Allowed Hosts**: Add production domain to `ALLOWED_HOSTS`
6. **Secret Key**: Use a strong, random secret key
7. **HTTPS/SSL**: Configure SSL certificates
8. **Email**: Configure email backend for notifications
9. **Payment**: Set up payment gateway (Stripe/Razorpay)
10. **Web Server**: Use Gunicorn + Nginx

### Gunicorn Command

```bash
gunicorn photography_project.wsgi:application --bind 0.0.0.0:8000
```

### Nginx Configuration

Configure Nginx to:
- Serve static files
- Serve media files
- Proxy requests to Gunicorn
- Handle SSL/HTTPS

## Troubleshooting

### Migration Issues

If you encounter migration errors:

```bash
# Backup database
cp db.sqlite3 db.sqlite3.backup

# Reset migrations (WARNING: Deletes data)
rm db.sqlite3
rm main/migrations/*.py
echo "" > main/migrations/__init__.py

# Recreate migrations
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
```

### Static Files Not Loading

```bash
# Check static file configuration
python manage.py findstatic css/style.css

# Collect static files
python manage.py collectstatic
```

### Import Errors

Ensure virtual environment is activated:
```bash
# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate
```

### Database Locked

If SQLite database is locked:
1. Stop the Django server
2. Delete `db.sqlite3-journal` file if it exists
3. Restart server

## Project Architecture

### Django MTV Pattern

- **Model**: Database schema (models.py) - Defines data structure
- **Template**: Presentation (HTML templates) - Dynamic content rendering
- **View**: Business logic (views.py) - Processes HTTP requests

### App Structure

- **main/** - Core application with gallery, services, booking
- **accounts/** - Authentication and user management
- **payments/** - Payment integration

### Separation of Concerns

Views are separated by responsibility:
- `views.py` - General and public views
- `views_booking.py` - Booking-specific functionality
- `views_dashboard.py` - Admin dashboard views
- `views_inquiry.py` - Inquiry handling
- `api_views.py` - REST API endpoints

## Security

- CSRF protection enabled
- SQL injection prevention (ORM)
- XSS prevention (template escaping)
- File upload validation
- Secure password hashing
- Environment variable management

## Support

For issues or questions:
1. Check Django documentation: https://docs.djangoproject.com/
2. Review DRF documentation: https://www.django-rest-framework.org/
3. Check OpenAI documentation: https://platform.openai.com/docs

## License

This project is proprietary software. All rights reserved.
