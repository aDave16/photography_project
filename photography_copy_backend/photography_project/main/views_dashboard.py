from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator
from django.db.models import Count, Sum, Q
from django.utils import timezone
from datetime import datetime, timedelta
from .models import Booking, ChatbotConfiguration, Inquiry, Service, Testimonial, GalleryImage, Availability, BookingSlot
import json
from .models import GalleryCategory, GalleryProject, ReelVideo
from .forms import GalleryCategoryForm, GalleryImageForm, ReelVideoForm, GalleryProjectForm


@login_required
def admin_dashboard(request):
    """
    Main admin dashboard view.
    Fetches stats and lists for the SPA-style dashboard.
    """
    # 1. Booking Stats
    total_bookings = Booking.objects.count()
    pending_bookings = Booking.objects.filter(status='pending').count()
    confirmed_bookings = Booking.objects.filter(status='confirmed').count()
    
    # 2. Content Stats
    gallery_images = GalleryImage.objects.all().order_by('-created_at')
    total_gallery_images = gallery_images.count()
    reels = ReelVideo.objects.all().order_by('-created_at')
    total_reels = reels.count()
    
    # 3. Category Data
    gallery_categories = GalleryCategory.objects.all().order_by('display_order')
    
    # 4. Other Lists
    services_list = Service.objects.all()
    # Note: Contact model was not in original imports, but keeping it as per instruction
    from .models import Contact
    contacts = Contact.objects.all().order_by('-created_at')
    testimonials_list = Testimonial.objects.all()
    inquiries = Inquiry.objects.all().order_by('-created_at')
    
    # Recent items for the activity feed
    recent_gallery = gallery_images[:5]

    chatbot_config = ChatbotConfiguration.objects.first()
    context = {
        'total_bookings': total_bookings,
        'pending_bookings': pending_bookings,
        'confirmed_bookings': confirmed_bookings,
        'total_gallery_images': total_gallery_images,
        'total_reels': total_reels,
        'gallery_images': gallery_images,
        'reels': reels,
        'gallery_categories': gallery_categories,
        'services_list': services_list,
        'contacts': contacts,
        'testimonials_list': testimonials_list,
        'inquiries': inquiries,
        'recent_gallery': recent_gallery,
        'bookings': Booking.objects.all().order_by('-created_at')[:10],
        'chatbot_config': chatbot_config,
    }
    return render(request, 'main/admin_dashboard.html', context)



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


@login_required
def dashboard_bookings(request):
    """
    Bookings management section with full CRUD operations.
    """
    search_query = request.GET.get('search', '')
    status_filter = request.GET.get('status', '')
    
    bookings = Booking.objects.select_related('service')
    
    if search_query:
        bookings = bookings.filter(
            Q(name__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(service__title__icontains=search_query)
        )
    
    if status_filter:
        bookings = bookings.filter(status=status_filter)
    
    # Pagination
    paginator = Paginator(bookings, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'bookings': page_obj,
        'search_query': search_query,
        'status_filter': status_filter,
        'status_choices': Booking.STATUS_CHOICES if hasattr(Booking, 'STATUS_CHOICES') else [],
    }
    
    return render(request, 'main/dashboard/bookings.html', context)


@login_required
def dashboard_availability(request):
    """
    New admin availability dashboard (v2) placeholder view.
    Renders the FullCalendar-powered admin calendar UI.
    """
    from .models import BlockedDateRange

    total_bookings = Booking.objects.count()
    booked_dates = Booking.objects.filter(status__in=['pending', 'approved', 'confirmed']).values('event_date').distinct().count()
    blocked_dates = BlockedDateRange.objects.filter(is_active=True).count()
    available_dates = max(0, 365 - booked_dates - blocked_dates)

    booking_slots = list(BookingSlot.objects.filter(is_active=True).order_by('order').values('id', 'name', 'label', 'capacity'))
    services = Service.objects.filter(is_active=True).order_by('display_order', '-is_featured', '-created_at')
    service_options = list(services.values('id', 'title'))

    context = {
        'total_bookings': total_bookings,
        'booked_dates': booked_dates,
        'blocked_dates': blocked_dates,
        'available_dates': available_dates,
        'booking_slots': booking_slots,
        'services': services,
        'service_options': service_options,
    }
    return render(request, 'main/dashboard/availability_v2.html', context)


@login_required
def dashboard_inquiries(request):
    """
    Inquiries management section with reply functionality.
    """
    search_query = request.GET.get('search', '')
    replied_filter = request.GET.get('replied', '')
    
    inquiries = Inquiry.objects.all()
    
    if search_query:
        inquiries = inquiries.filter(
            Q(name__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(message__icontains=search_query)
        )
    
    if replied_filter == 'replied':
        inquiries = inquiries.filter(replied=True)
    elif replied_filter == 'unreplied':
        inquiries = inquiries.filter(replied=False)
    
    # Pagination
    paginator = Paginator(inquiries, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'inquiries': page_obj,
        'search_query': search_query,
        'replied_filter': replied_filter,
    }
    
    return render(request, 'main/dashboard/inquiries.html', context)


@login_required
def dashboard_services(request):
    """
    Services management section with dynamic service management.
    """
    search_query = request.GET.get('search', '')
    featured_filter = request.GET.get('featured', '')
    active_filter = request.GET.get('active', '')

    services = Service.objects.all().order_by('display_order')
    
    if search_query:
        services = services.filter(
            Q(title__icontains=search_query) |
            Q(short_description__icontains=search_query) |
            Q(full_description__icontains=search_query) |
            Q(tagline__icontains=search_query)
        )
    
    if featured_filter == 'featured':
        services = services.filter(is_featured=True)
    elif featured_filter == 'not_featured':
        services = services.filter(is_featured=False)
    
    if active_filter == 'active':
        services = services.filter(is_active=True)
    elif active_filter == 'inactive':
        services = services.filter(is_active=False)
    
    # Pagination
    paginator = Paginator(services, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'services': page_obj,
        'search_query': search_query,
        'featured_filter': featured_filter,
        'active_filter': active_filter,
    }
    
    return render(request, 'main/dashboard/services.html', context)


@csrf_exempt
@login_required
def dashboard_update_booking_status(request):
    """
    Update booking status via AJAX.
    """
    if request.method == 'POST':
        booking_id = request.POST.get('booking_id')
        new_status = request.POST.get('status')
        
        try:
            booking = Booking.objects.get(id=booking_id)
            booking.status = new_status
            booking.save()
            
            return JsonResponse({
                'success': True,
                'message': 'Booking status updated successfully'
            })
        except Booking.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': 'Booking not found'
            }, status=404)
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Error updating booking: {str(e)}'
            }, status=500)
    
    return JsonResponse({
        'success': False,
        'message': 'Invalid request method'
    }, status=405)


@login_required
def dashboard_bulk_upload(request):
    """
    Handle bulk image uploads from the dashboard.
    """
    if request.method == 'POST':
        category_id = request.POST.get('category')
        files = request.FILES.getlist('images')
        
        if not category_id or not files:
            messages.error(request, 'Please select a category and at least one image.')
            return redirect('admin_dashboard')
            
        category = get_object_or_404(GalleryCategory, id=category_id)
        
        for f in files:
            GalleryImage.objects.create(
                title=f.name.split('.')[0],
                category=category,
                image=f,
                is_published=True
            )
            
        messages.success(request, f'Successfully uploaded {len(files)} images to {category.name}!')
        return redirect('admin_dashboard')
    
    return redirect('admin_dashboard')


@login_required
def dashboard_add_reel(request):
    """
    Handle reel video addition from the dashboard.
    """
    if request.method == 'POST':
        title = request.POST.get('title')
        category_id = request.POST.get('category')
        video = request.FILES.get('video')
        thumbnail = request.FILES.get('thumbnail')
        
        if not title or not category_id or not video:
            messages.error(request, 'Please fill in all required fields.')
            return redirect('admin_dashboard')
            
        category = get_object_or_404(GalleryCategory, id=category_id)
        
        ReelVideo.objects.create(
            title=title,
            category=category,
            video=video,
            thumbnail=thumbnail,
            is_published=True
        )
            
        messages.success(request, f'Successfully added reel "{title}" to {category.name}!')
        return redirect('admin_dashboard')
    
    return redirect('admin_dashboard')


@csrf_exempt
@login_required
def dashboard_update_inquiry_status(request):
    """
    Update inquiry status and reply via AJAX.
    """
    if request.method == 'POST':
        inquiry_id = request.POST.get('inquiry_id')
        action = request.POST.get('action')  # 'status', 'reply', 'delete'
        
        try:
            inquiry = Inquiry.objects.get(id=inquiry_id)
            
            if action == 'status':
                new_status = request.POST.get('status')
                # Update replied boolean based on status
                if new_status in ['replied', 'closed']:
                    inquiry.replied = True
                inquiry.status = new_status
                inquiry.save()
                
                return JsonResponse({
                    'success': True,
                    'message': 'Inquiry status updated successfully'
                })
                
            elif action == 'reply':
                reply_message = request.POST.get('reply_message', '').strip()
                if reply_message:
                    inquiry.admin_reply = reply_message
                    inquiry.replied = True
                    inquiry.save()
                    
                    # Send email to customer
                    try:
                        from django.core.mail import send_mail
                        from django.conf import settings
                        
                        subject = f"Re: Your Inquiry | Dhrumil Bajak Photography"
                        message = f"""
Dear {inquiry.name},

{reply_message}

Best regards,
Dhrumil Bajak Photography Team
                        """
                        
                        send_mail(
                            subject=subject,
                            message=message,
                            from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@example.com'),
                            recipient_list=[inquiry.email],
                            fail_silently=False,
                        )
                        
                        return JsonResponse({
                            'success': True,
                            'message': 'Reply sent successfully'
                        })
                    except Exception as e:
                        return JsonResponse({
                            'success': False,
                            'message': f'Failed to send email: {str(e)}'
                        }, status=500)
                else:
                    return JsonResponse({
                        'success': False,
                        'message': 'Reply message cannot be empty'
                    }, status=400)
                    
            elif action == 'delete':
                inquiry.delete()
                return JsonResponse({
                    'success': True,
                    'message': 'Inquiry deleted successfully'
                })
                
        except Inquiry.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': 'Inquiry not found'
            }, status=404)
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Error updating inquiry: {str(e)}'
            }, status=500)
    
    return JsonResponse({
        'success': False,
        'message': 'Invalid request method'
    }, status=405)


@csrf_exempt
@login_required
def dashboard_service_ajax(request):
    """
    Toggle featured/active or delete a service via AJAX (FormData POST).
    """
    if request.method == 'POST':
        service_id = request.POST.get('service_id')
        action = request.POST.get('action')  # 'toggle_featured', 'toggle_active', 'delete'
        
        try:
            service = Service.objects.get(id=service_id)
            
            if action == 'toggle_featured':
                service.is_featured = not service.is_featured
                service.save()
                
                return JsonResponse({
                    'success': True,
                    'message': f'Service {"featured" if service.is_featured else "unfeatured"} successfully',
                    'is_featured': service.is_featured
                })
                
            elif action == 'toggle_active':
                service.is_active = not service.is_active
                service.save()
                
                return JsonResponse({
                    'success': True,
                    'message': f'Service {"active" if service.is_active else "deactivated"} successfully',
                    'is_active': service.is_active
                })
                
            elif action == 'delete':
                service.delete()
                return JsonResponse({
                    'success': True,
                    'message': 'Service deleted successfully'
                })
                
        except Service.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': 'Service not found'
            }, status=404)
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Error updating service: {str(e)}'
            }, status=500)
    
    return JsonResponse({
        'success': False,
        'message': 'Invalid request method'
    }, status=405)


@login_required
def dashboard_create_service(request):
    """
    Create new service via AJAX.
    """
    if request.method == 'POST':
        try:
            # Extract form data
            title = request.POST.get('title', '').strip()
            service_type = request.POST.get('service_type', 'wedding')
            price = request.POST.get('price', '0')
            description = request.POST.get('description', '').strip()
            
            if not title or not description:
                return JsonResponse({
                    'success': False,
                    'message': 'Title and description are required'
                }, status=400)
            
            # Create service
            service = Service.objects.create(
                title=title,
                service_type=service_type,
                price=price,
                description=description,
                display_order=Service.objects.count()  # Auto-increment order
            )
            
            return JsonResponse({
                'success': True,
                'message': 'Service created successfully',
                'service_id': service.id
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Error creating service: {str(e)}'
            }, status=500)
    
    return JsonResponse({
        'success': False,
        'message': 'Invalid request method'
    }, status=405)


@login_required
def gallery_categories(request):
    search_query = request.GET.get('q', '')
    categories = GalleryCategory.objects.all().order_by('display_order')
    
    if search_query:
        categories = categories.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query)
        )
        
    return render(request, 'main/dashboard/gallery_categories.html', {
        'categories': categories,
        'search_query': search_query
    })


@login_required
def create_gallery_category(request):
    if request.method == 'POST':
        form = GalleryCategoryForm(request.POST, request.FILES)
        if form.is_valid():
            category = form.save(commit=False)
            category.is_active = True
            category.save()
            form.save()
            messages.success(request, 'Category created successfully!')
            return redirect('dashboard_gallery_categories')
    else:
        form = GalleryCategoryForm()
    return render(request, 'main/dashboard/create_gallery_category.html', {'form': form})


@login_required
def edit_gallery_category(request, category_id):
    category = get_object_or_404(GalleryCategory, id=category_id)
    if request.method == 'POST':
        form = GalleryCategoryForm(request.POST, request.FILES, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, 'Category updated successfully!')
            return redirect('dashboard_gallery_categories')
    else:
        form = GalleryCategoryForm(instance=category)
    return render(request, 'main/dashboard/category_form.html', {'form': form, 'category': category, 'action': 'Edit'})


@login_required
def delete_gallery_category(request, category_id):
    category = get_object_or_404(GalleryCategory, id=category_id)
    if request.method == 'POST':
        category.delete()
        messages.success(request, 'Category deleted successfully!')
        return redirect('dashboard_gallery_categories')
    return render(request, 'main/dashboard/delete_gallery_category.html', {'category': category})


@login_required
def gallery_projects(request):
    projects = GalleryProject.objects.all().order_by('display_order')
    return render(request, 'main/dashboard/gallery_projects.html', {'projects': projects})


@login_required
def gallery_images(request):
    images = GalleryImage.objects.select_related('category').order_by('-created_at')
    categories = GalleryCategory.objects.filter(is_active=True).order_by('display_order')
    return render(request, 'main/dashboard/gallery_images.html', {
        'images': images,
        'categories': categories
    })


from .models import GalleryImage, GalleryCategory
from django.contrib import messages
from django.shortcuts import redirect

@login_required
def upload_gallery_images(request):
    if request.method == "POST":

        category_id = request.POST.get("category")
        category = get_object_or_404(
            GalleryCategory,
            id=category_id,
            is_active=True
        )

        images = request.FILES.getlist("images")

        if not images:
            messages.error(request, 'Please select at least one image to upload.')
            return redirect('create_gallery_image')

        for image in images:
            GalleryImage.objects.create(
                title=image.name,
                category=category,
                image=image,
                is_published=True
            )

        messages.success(
            request,
            f"{len(images)} images uploaded successfully."
        )

    return redirect('create_gallery_image')


@login_required
def create_gallery_image(request):
    categories = GalleryCategory.objects.filter(is_active=True).order_by('display_order')
    images = GalleryImage.objects.select_related('category').order_by('-created_at')

    if request.method == 'POST':

        form = GalleryImageForm(
            request.POST,
            request.FILES
        )

        if form.is_valid():
            form.save()

            messages.success(
                request,
                'Image uploaded successfully!'
            )

            return redirect(
                'create_gallery_image'
            )

    else:
        form = GalleryImageForm()

    return render(
        request,
        'main/dashboard/gallery_images.html',
        {
            'form': form,
            'categories': categories,
            'images': images,
        }
    )

@login_required
def edit_gallery_image(request, image_id):

    image = get_object_or_404(
        GalleryImage,
        id=image_id
    )

    if request.method == 'POST':

        form = GalleryImageForm(
            request.POST,
            request.FILES,
            instance=image
        )

        if form.is_valid():

            form.save()

            messages.success(
                request,
                'Image updated successfully!'
            )

            return redirect(
                'create_gallery_image'
            )

    else:

        form = GalleryImageForm(
            instance=image
        )

    return render(
        request,
        'main/dashboard/edit_gallery_image.html',
        {
            'form': form,
            'image': image
        }
    )

@login_required
def delete_gallery_image(request, image_id):

    image = get_object_or_404(
        GalleryImage,
        id=image_id
    )

    if request.method == 'POST':

        image.delete()

        messages.success(
            request,
            'Image deleted successfully!'
        )

        return redirect(
            'admin_dashboard'
        )

    return render(
        request,
        'main/dashboard/delete_gallery_image.html',
        {
            'image': image
        }
    )


@login_required
def gallery_reels(request):
    reels = ReelVideo.objects.all().order_by('display_order')
    categories = GalleryCategory.objects.all()
    return render(request, 'main/dashboard/gallery_reels.html', {
        'reels': reels,
        'categories': categories
    })


@csrf_exempt
@login_required
def api_gallery_categories(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        category = GalleryCategory.objects.create(
            name=data['name'],
            slug=data['slug'],
            description=data.get('description', ''),
            display_order=data.get('display_order', 0),
            is_active=data.get('is_active', True)
        )
        return JsonResponse({'id': category.id, 'name': category.name})
    return JsonResponse({'error': 'Invalid request'}, status=400)


@csrf_exempt
@login_required
def api_gallery_projects(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        project = GalleryProject.objects.create(
            title=data['title'],
            slug=data['slug'],
            category_id=data['category_id'],
            client_name=data.get('client_name', ''),
            description=data.get('description', ''),
            location=data.get('location', ''),
            event_type=data.get('event_type', ''),
            shoot_date=data.get('shoot_date', None),
            tags=data.get('tags', ''),
            cover_image=data.get('cover_image', ''),
            is_featured=data.get('is_featured', False),
            is_published=data.get('is_published', True),
            display_order=data.get('display_order', 0)
        )
        return JsonResponse({'id': project.id, 'title': project.title})
    return JsonResponse({'error': 'Invalid request'}, status=400)


@csrf_exempt
@login_required
def api_gallery_images(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        image = GalleryImage.objects.create(
            title=data['title'],
            slug=data['slug'],
            category_id=data['category_id'],
            image=data['image'],
            caption=data.get('caption', ''),
            description=data.get('description', ''),
            location=data.get('location', ''),
            date_taken=data.get('date_taken', None),
            is_featured=data.get('is_featured', False),
            is_published=data.get('is_published', True),
            display_order=data.get('display_order', 0)
        )
        return JsonResponse({'id': image.id, 'title': image.title})
    return JsonResponse({'error': 'Invalid request'}, status=400)


@csrf_exempt
@login_required
def api_gallery_reels(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        reel = ReelVideo.objects.create(
            title=data['title'],
            slug=data['slug'],
            category_id=data['category_id'],
            video=data['video'],
            thumbnail=data.get('thumbnail', ''),
            description=data.get('description', ''),
            is_featured=data.get('is_featured', False),
            is_published=data.get('is_published', True),
            display_order=data.get('display_order', 0)
        )
        return JsonResponse({'id': reel.id, 'title': reel.title})
    return JsonResponse({'error': 'Invalid request'}, status=400)
