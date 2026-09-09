import json
import os
from django.views.decorators.http import require_POST
from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import ensure_csrf_cookie
from django.db.models import Q, Count, Sum
from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
from .models import Service, Booking, Availability, BookingSlot
from datetime import datetime
from django.utils import timezone
from datetime import datetime, timedelta, date
#from channels.layers import get_channel_layer
#from asgiref.sync import async_to_sync

# =============================================================================
# BOOKING SYSTEM VIEWS
# =============================================================================

def booking_page(request):
    """
    Main booking page with calendar, service selection, and booking form
    """
    services = Service.objects.filter(is_active=True).order_by('display_order', '-is_featured', '-created_at')
    
    context = {
        'services': services,
        'time_slots': [
            '09:00 AM', '10:00 AM', '11:00 AM', '12:00 PM',
            '01:00 PM', '02:00 PM', '03:00 PM', '04:00 PM', '05:00 PM'
        ]
    }
    return render(request, 'main/booking.html', context)


@require_POST
def create_booking(request):
    """
    Create new booking via AJAX with enhanced validation and email notifications
    """
    try:
        data = json.loads(request.body)
        
        # Validate required fields
        required_fields = ['name', 'email', 'service_id', 'event_date', 'time_slot']
        for field in required_fields:
            if not data.get(field):
                return JsonResponse({
                    'success': False,
                    'error': f'{field} is required'
                }, status=400)
        
        # Validate email format
        email = data.get('email', '').strip()
        if not email or '@' not in email:
            return JsonResponse({
                'success': False,
                'error': 'Please provide a valid email address'
            }, status=400)
        
        # Validate phone (optional but check if provided)
        phone = data.get('phone', '').strip()
        if phone and (len(phone) < 10 or not phone.replace('-', '').isdigit()):
            return JsonResponse({
                'success': False,
                'error': 'Please provide a valid phone number'
            }, status=400)
        
        # Get service
        service = get_object_or_404(Service, id=data['service_id'], is_active=True)
        
        # Parse date
        event_date = datetime.strptime(data['event_date'], '%Y-%m-%d').date()
        
        # Check if date is in the past
        if event_date < timezone.now().date():
            return JsonResponse({
                        'success': False,
        'message': 'Past dates are not allowed.'
                    }, status=400)

        # Check if date is too far in future (more than 1 year)
        max_date = timezone.now().date() + timedelta(days=365)
        if event_date > max_date:
            return JsonResponse({
                'success': False,
                'error': 'Booking date cannot be more than 1 year in advance'
            }, status=400)
        
        # Check if slot is already booked for this service and time slot
        existing_booking = Booking.objects.filter(
            service=service,
            event_date=event_date,
            time_slot=data['time_slot'],
            status__in=['pending', 'approved', 'confirmed']
        ).exists()
        
        if existing_booking:
            return JsonResponse({
                'success': False,
                'error': 'This time slot is already booked'
            }, status=400)

        # Check manual block and per-slot capacity
        from .models import Availability, BlockedDateRange
        blocked_entry = Availability.objects.filter(
            date=event_date,
            is_blocked_by_admin=True
        ).first()
        blocked_range = BlockedDateRange.objects.filter(start_date__lte=event_date, end_date__gte=event_date, is_active=True).first()

        if blocked_entry:
            return JsonResponse({
                'success': False,
                'error': f'This date is blocked: {blocked_entry.reason or "Blocked by admin"}'
            }, status=400)
        if blocked_range:
            return JsonResponse({
                'success': False,
                'error': f'This date is blocked: {blocked_range.reason or "Blocked by admin"}'
            }, status=400)

        # Enforce per-slot capacity using BookingSlot
        slot_name = data['time_slot']
        slot_obj = BookingSlot.objects.filter(name=slot_name, is_active=True).first()
        capacity = slot_obj.capacity if slot_obj else 1
        used_slots = Booking.objects.filter(
            event_date=event_date,
            time_slot=slot_name,
            status__in=['pending', 'approved', 'confirmed']
        ).count()

        if used_slots >= capacity:
            return JsonResponse({
                'success': False,
                'error': 'This time slot is fully booked'
            }, status=400)

        # Create booking
        booking = Booking.objects.create(
            name=data['name'],
            email=data['email'],
            phone=data.get('phone', ''),
            service=service,
            event_date=event_date,
            time_slot=data['time_slot'],
            location=data.get('location', ''),
            message=data.get('message', ''),
            status='pending'
        )
        
        # Send confirmation email to customer
        try:
            send_customer_confirmation_email(booking)
            print(f"✅ Customer confirmation email sent to {booking.email}")
        except Exception as e:
            print(f"❌ Failed to send customer email: {e}")
        
        # Send notification email to admin
        try:
            send_admin_booking_notification(booking)
            print(f"✅ Admin notification email sent for new booking")
        except Exception as e:
            print(f"❌ Failed to send admin email: {e}")
        
        return JsonResponse({
            'success': True,
            'booking_id': booking.id,
            'message': 'Booking confirmed successfully!'
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Invalid request data'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


def send_customer_confirmation_email(booking):
    """
    Send booking confirmation email to customer
    """
    try:
        subject = f'Your Booking Has Been Confirmed | {settings.DEFAULT_FROM_NAME}'
        
        # Render email template with context
        html_content = render_to_string('emails/booking_confirmation.html', {
            'name': booking.name,
            'from_email': settings.DEFAULT_FROM_EMAIL,
            'service_title': booking.service.title,
            'event_date': booking.event_date,
            'time_slot': booking.time_slot,
            'location': booking.location,
            'message': booking.message,
            'status': booking.get_status_display(),
        })
        
        # Create email message
        email_message = EmailMultiAlternatives(
            subject=subject,
            body=html_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[booking.email],
        )
        
        # Send email
        email_message.send()
        
    except Exception as e:
        print(f"Error sending customer confirmation email: {e}")


def send_admin_booking_notification(booking):
    """
    Send notification email to admin about new booking
    """
    try:
        subject = f'New Booking Received | {settings.DEFAULT_FROM_NAME}'
        
        # Render admin email template
        html_content = render_to_string('emails/admin_booking_alert.html', {
            'name': booking.name,
            'email': booking.email,
            'phone': booking.phone,
            'service_title': booking.service.title,
            'event_date': booking.event_date,
            'time_slot': booking.time_slot,
            'location': booking.location,
            'message': booking.message,
        })
        
        # Create email message
        email_message = EmailMultiAlternatives(
            subject=subject,
            body=html_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[settings.DEFAULT_FROM_EMAIL],
        )
        
        # Send email
        email_message.send()
        
    except Exception as e:
        print(f"Error sending admin notification email: {e}")


def get_available_slots(request):
    """
    Get available time slots for a specific date with enhanced validation
    """
    date_str = request.GET.get('date')
    service_id = request.GET.get('service_id')
    
    if not date_str or not service_id:
        return JsonResponse({'error': 'Date and service_id required'}, status=400)
    
    try:
        event_date = datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        return JsonResponse({'error': 'Invalid date format'}, status=400)

    try:
        # Use BookingSlot definitions and capacity to determine available slots
        slot_objs = list(BookingSlot.objects.filter(is_active=True).order_by('order'))
        if slot_objs:
            slot_names = [s.name for s in slot_objs]
        else:
            slot_names = [
                '09:00 AM', '10:00 AM', '11:00 AM', '12:00 PM',
                '01:00 PM', '02:00 PM', '03:00 PM', '04:00 PM', '05:00 PM'
            ]

        booked_counts = Booking.objects.filter(
            event_date=event_date,
            service_id=service_id,
            status__in=['confirmed', 'pending']
        ).values('time_slot').annotate(count=Count('id'))
        booked_map = {b['time_slot']: b['count'] for b in booked_counts}

        available_slots = []
        slot_info = {}
        for name in slot_names:
            slot_obj = next((s for s in slot_objs if s.name == name), None)
            capacity = slot_obj.capacity if slot_obj else 1
            booked = booked_map.get(name, 0)
            remaining = max(0, capacity - booked)
            slot_info[name] = {'capacity': capacity, 'booked': booked, 'remaining': remaining}
            if remaining > 0:
                available_slots.append(name)

        # If admin blocked the whole date, return blocked
        from .models import BlockedDateRange
        blocked = BlockedDateRange.objects.filter(start_date__lte=event_date, end_date__gte=event_date, is_active=True).exists()
        if blocked:
            return JsonResponse({'available_slots': [], 'booked_slots': list(booked_map.keys()), 'blocked': True, 'slot_info': slot_info})

        return JsonResponse({
            'available_slots': available_slots,
            'booked_slots': list(booked_map.keys()),
            'slot_info': slot_info
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def get_date_details(request):
    """
    Get booking and block details for a specific calendar date.
    """
    date_str = request.GET.get('date')
    if not date_str:
        return JsonResponse({'error': 'Date is required'}, status=400)

    try:
        event_date = datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        return JsonResponse({'error': 'Invalid date format'}, status=400)

    bookings = Booking.objects.filter(
        event_date=event_date,
        status__in=['pending', 'approved', 'confirmed']
    ).select_related('service')

    availability = Availability.objects.filter(date=event_date).first()
    from .models import BlockedDateRange
    blocked_range = BlockedDateRange.objects.filter(start_date__lte=event_date, end_date__gte=event_date, is_active=True).first()
    booked_slots = list(bookings.values_list('time_slot', flat=True))

    slot_objs = list(BookingSlot.objects.filter(is_active=True).order_by('order'))
    if slot_objs:
        all_slots = [s.label for s in slot_objs]
    else:
        all_slots = [
            '09:00 AM', '10:00 AM', '11:00 AM', '12:00 PM',
            '01:00 PM', '02:00 PM', '03:00 PM', '04:00 PM', '05:00 PM'
        ]

    # Build slot summary with capacities and remaining counts
    slot_summary = {'total': len(all_slots), 'booked_slots': booked_slots, 'available_slots': [], 'all_slots': all_slots, 'slot_info': {}}
    for s in slot_objs:
        name = s.name
        capacity = s.capacity
        booked = booked_slots.count(name) if isinstance(booked_slots, list) else booked_slots.count(name)
        remaining = max(0, capacity - booked)
        slot_summary['slot_info'][name] = {'capacity': capacity, 'booked': booked, 'remaining': remaining}
        if remaining > 0:
            slot_summary['available_slots'].append(name)

    return JsonResponse({
        'date': date_str,
        'bookings': [
            {
                'id': booking.id,
                'name': booking.name,
                'email': booking.email,
                'phone': booking.phone,
                'service': booking.service.title,
                'time_slot': booking.time_slot,
                'event_date': booking.event_date.strftime('%Y-%m-%d'),
                'location': booking.location,
                'status': booking.status,
                'payment_status': booking.payment_status,
                'message': booking.message,
                'budget_range': booking.budget_range,
                'admin_notes': booking.admin_notes,
            }
            for booking in bookings
        ],
        'availability': {
            'blocked': bool(availability and availability.is_blocked_by_admin) or bool(blocked_range),
            'is_available': (bool(availability.is_available) if availability else True) and not bool(blocked_range),
            'block_type': availability.block_type if availability else '',
            'reason': (availability.reason if availability else '') or (blocked_range.reason if blocked_range else ''),
        },
        'slot_summary': slot_summary
    })




# admin_block_date and admin_create_booking removed; admin availability UI deprecated.


def get_calendar_data(request):
    """Get calendar data with booked/unavailable dates."""
    try:
        year = int(request.GET.get('year', timezone.now().year))
        month = int(request.GET.get('month', timezone.now().month))

        calendar_data = {}

        # Bookings aggregated by date for the requested month
        bookings = Booking.objects.filter(
            event_date__year=year,
            event_date__month=month
        ).values('event_date').annotate(count=Count('id'))

        # Availability manual blocks for the month
        blocked_entries = Availability.objects.filter(
            date__year=year,
            date__month=month,
            is_blocked_by_admin=True
        )

        # Availability entries that are explicitly marked unavailable (auto or manual)
        unavailable_entries = Availability.objects.filter(
            date__year=year,
            date__month=month,
            is_available=False
        )

        # Total capacity is the sum of active BookingSlot capacities
        total_capacity = BookingSlot.objects.filter(is_active=True).aggregate(total=Sum('capacity'))['total'] or 0
        if total_capacity == 0:
            total_capacity = 9

        # Add booked dates
        for booking in bookings:
            key = booking['event_date'].strftime('%Y-%m-%d')
            calendar_data[key] = {
                'booked_count': booking['count'],
                'status': 'booked',
                'label': f"{booking['count']} booking(s)",
                'available': booking['count'] < total_capacity,
            }

        # Add manual blocked dates
        for entry in blocked_entries:
            key = entry.date.strftime('%Y-%m-%d')
            calendar_data[key] = {
                'booked_count': calendar_data.get(key, {}).get('booked_count', 0),
                'status': 'blocked',
                'label': (entry.block_type.replace('_', ' ').title() if getattr(entry, 'block_type', None) else 'Blocked'),
                'reason': entry.reason,
                'available': False,
            }

        # Add unavailable availability entries (not manually blocked)
        for entry in unavailable_entries:
            key = entry.date.strftime('%Y-%m-%d')
            # Do not override manual blocked entries
            if key in calendar_data and calendar_data[key].get('status') == 'blocked':
                continue
            calendar_data[key] = {
                'booked_count': calendar_data.get(key, {}).get('booked_count', 0),
                'status': 'booked',
                'label': entry.reason or 'Unavailable',
                'reason': entry.reason,
                'available': False,
            }

        # Add blocked date ranges
        from .models import BlockedDateRange

        # Calculate ranges that overlap this month
        month_start = date(year, month, 1)
        # get last day of the month safely
        if month == 12:
            month_end = date(year, 12, 31)
        else:
            month_end = date(year, month + 1, 1) - timedelta(days=1)

        ranges = BlockedDateRange.objects.filter(
            is_active=True,
            start_date__lte=month_end,
            end_date__gte=month_start,
        )

        for r in ranges:
            cur = r.start_date
            while cur <= r.end_date:
                if cur.year == year and cur.month == month:
                    key = cur.strftime('%Y-%m-%d')
                    calendar_data[key] = {
                        'booked_count': calendar_data.get(key, {}).get('booked_count', 0),
                        'status': 'blocked',
                        'label': r.reason or 'Blocked by admin',
                        'reason': r.reason,
                        'available': False,
                    }
                cur = cur + timedelta(days=1)

        # Calculate global stats for the dashboard
        from .models import BlockedDateRange
        total_bookings = Booking.objects.count()
        pending_bookings = Booking.objects.filter(status='pending').count()
        confirmed_bookings = Booking.objects.filter(status__in=['confirmed', 'approved']).count()
        
        # Blocked dates count: we need to count unique days that are blocked
        blocked_ranges = BlockedDateRange.objects.filter(is_active=True)
        blocked_days = set()
        for r in blocked_ranges:
            curr = r.start_date
            while curr <= r.end_date:
                blocked_days.add(curr)
                curr += timedelta(days=1)
        
        # Also include manual blocks from Availability model
        manual_blocks = Availability.objects.filter(is_blocked_by_admin=True)
        for mb in manual_blocks:
            blocked_days.add(mb.date)
            
        blocked_dates_count = len(blocked_days)
        
        # Available dates: For simplicity, let's say available in the next 365 days
        today = timezone.now().date()
        year_later = today + timedelta(days=365)
        
        # Dates with at least one booking
        booked_dates = set(Booking.objects.filter(
            event_date__range=[today, year_later],
            status__in=['pending', 'approved', 'confirmed']
        ).values_list('event_date', flat=True))
        
        # All blocked days in the next year
        blocked_in_year = {d for d in blocked_days if today <= d <= year_later}
        
        # Available = Total days - (Booked or Blocked)
        available_dates_count = 365 - len(booked_dates.union(blocked_in_year))

        return JsonResponse({
            'calendar_data': calendar_data,
            'year': year,
            'month': month,
            'stats': {
                'total_bookings': total_bookings,
                'pending_bookings': pending_bookings,
                'confirmed_bookings': confirmed_bookings,
                'blocked_dates': blocked_dates_count,
                'available_dates': available_dates_count,
            }
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@login_required
def admin_calendar_events(request):
    """Return calendar events for admin calendar (bookings + blocked ranges)."""
    try:
        events = []
        # Bookings
        bookings = Booking.objects.filter(status__in=['pending', 'approved', 'confirmed'])
        for b in bookings:
            if not b.event_date:
                continue
            events.append({
                'id': f'booking-{b.id}',
                'title': f"{b.name} — {b.service.title}",
                'start': b.event_date.strftime('%Y-%m-%d'),
                'allDay': True,
                'extendedProps': {
                    'type': 'booking',
                    'booking_id': b.id,
                    'time_slot': b.time_slot,
                    'status': b.status,
                },
                'color': '#ef4444',
            })

        # Blocked date ranges
        from .models import BlockedDateRange
        blocks = BlockedDateRange.objects.filter(is_active=True)
        for blk in blocks:
            events.append({
                'id': f'block-{blk.id}',
                'title': blk.reason or 'Blocked',
                'start': blk.start_date.strftime('%Y-%m-%d'),
                'end': (blk.end_date + timedelta(days=1)).strftime('%Y-%m-%d'),
                'allDay': True,
                'extendedProps': {
                    'type': 'block',
                    'block_id': blk.id,
                    'reason': blk.reason,
                },
                'color': '#fb923c',
            })

        # Availability entries marked unavailable (auto/booked)
        unavailable = Availability.objects.filter(is_available=False)
        for a in unavailable:
            # avoid duplicating blocked ranges
            if a.is_blocked_by_admin:
                continue
            events.append({
                'id': f'avail-{a.id}',
                'title': a.reason or 'Unavailable',
                'start': a.date.strftime('%Y-%m-%d'),
                'allDay': True,
                'extendedProps': {
                    'type': 'availability',
                    'availability_id': a.id,
                    'reason': a.reason,
                },
                'color': '#dc2626',
            })

        return JsonResponse({'events': events})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)



@login_required
@require_POST
def admin_create_booking_v2(request):
    """Admin creates a booking via API (safer replacement for old endpoint)."""
    try:
        data = json.loads(request.body)
        required_fields = ['name', 'email', 'service_id', 'event_date', 'time_slot']
        for field in required_fields:
            if not data.get(field):
                return JsonResponse({'success': False, 'error': f'{field} is required'}, status=400)

        service = get_object_or_404(Service, id=data['service_id'], is_active=True)
        event_date = datetime.strptime(data['event_date'], '%Y-%m-%d').date()
        if event_date < timezone.now().date():
            return JsonResponse({'success': False, 'error': 'Cannot create a booking for a past date'}, status=400)

        # Check blocks
        from .models import BlockedDateRange
        blocked = BlockedDateRange.objects.filter(is_active=True, start_date__lte=event_date, end_date__gte=event_date).exists()
        if blocked:
            return JsonResponse({'success': False, 'error': 'This date is blocked'}, status=400)

        existing_booking = Booking.objects.filter(
            service=service,
            event_date=event_date,
            time_slot=data['time_slot'],
            status__in=['pending', 'approved', 'confirmed']
        ).exists()
        if existing_booking:
            return JsonResponse({'success': False, 'error': 'This time slot is already booked'}, status=400)

        # Enforce per-slot capacity
        slot_name = data['time_slot']
        slot_obj = BookingSlot.objects.filter(name=slot_name, is_active=True).first()
        capacity = slot_obj.capacity if slot_obj else 1
        used_slots = Booking.objects.filter(event_date=event_date, time_slot=slot_name, status__in=['pending', 'approved', 'confirmed']).count()
        if used_slots >= capacity:
            return JsonResponse({'success': False, 'error': 'This time slot is fully booked'}, status=400)

        booking = Booking.objects.create(
            name=data['name'],
            email=data['email'],
            phone=data.get('phone', ''),
            service=service,
            event_date=event_date,
            time_slot=data['time_slot'],
            location=data.get('location', ''),
            message=data.get('message', ''),
            budget_range=data.get('budget_range', ''),
            status=data.get('status', 'confirmed'),
            payment_status=data.get('payment_status', 'unpaid'),
            admin_notes=data.get('admin_notes', ''),
            user=request.user if request.user.is_authenticated else None,
        )

        return JsonResponse({'success': True, 'booking_id': booking.id})
    except ValueError:
        return JsonResponse({'success': False, 'error': 'Invalid date format'}, status=400)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@login_required
@require_POST
def admin_create_block(request):
    """Create a blocked date or range for admin calendar."""
    try:
        data = json.loads(request.body)
        start_date = data.get('start_date')
        end_date = data.get('end_date') or start_date
        reason = data.get('reason', '')
        if not start_date:
            return JsonResponse({'success': False, 'error': 'start_date required'}, status=400)
        s = datetime.strptime(start_date, '%Y-%m-%d').date()
        e = datetime.strptime(end_date, '%Y-%m-%d').date()
        from .models import BlockedDateRange
        blk = BlockedDateRange.objects.create(start_date=s, end_date=e, reason=reason, created_by=request.user)
        # notify websocket listeners
       
        return JsonResponse({'success': True, 'block_id': blk.id})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@login_required
@require_POST
def admin_toggle_block(request):
    """Toggle (create or deactivate) a block for a single date."""
    try:
        data = json.loads(request.body)
        # accept either 'date' or 'start_date'
        date_str = data.get('date') or data.get('start_date')
        if not date_str:
            return JsonResponse({'success': False, 'error': 'date is required'}, status=400)

        target = datetime.strptime(date_str, '%Y-%m-%d').date()
        from .models import BlockedDateRange

        # Find active ranges that include this date
        existing = BlockedDateRange.objects.filter(is_active=True, start_date__lte=target, end_date__gte=target)
        if existing.exists():
            # deactivate all overlapping ranges (simple toggle)
            count = existing.update(is_active=False)
            return JsonResponse({'success': True, 'message': f'Unblocked {count} range(s)'})

        # create a single-day block
        reason = data.get('reason', '')
        blk = BlockedDateRange.objects.create(start_date=target, end_date=target, reason=reason, created_by=request.user)
        # notify websocket listeners
        
        return JsonResponse({'success': True, 'block_id': blk.id})
    except ValueError:
        return JsonResponse({'success': False, 'error': 'Invalid date format'}, status=400)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@login_required
def admin_get_booking(request, booking_id):
    """Return detailed booking info for admin modal."""
    try:
        booking = get_object_or_404(Booking, id=booking_id)
        data = {
            'id': booking.id,
            'name': booking.name,
            'email': booking.email,
            'phone': booking.phone,
            'service_id': booking.service_id,
            'service': booking.service.title if booking.service else '',
            'event_date': booking.event_date.strftime('%Y-%m-%d') if booking.event_date else '',
            'time_slot': booking.time_slot,
            'location': booking.location,
            'message': booking.message,
            'budget_range': booking.budget_range,
            'status': booking.status,
            'payment_status': booking.payment_status,
            'admin_notes': booking.admin_notes,
            'created_at': booking.created_at.strftime('%Y-%m-%d %H:%M:%S')
        }
        return JsonResponse({'booking': data})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def dashboard_calendar_bookings(request):
    """Return bookings for a specific date (used by admin calendar date click)."""
    date_str = request.GET.get('date')
    if not date_str:
        return JsonResponse({'error': 'date is required'}, status=400)
    try:
        event_date = datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        return JsonResponse({'error': 'invalid date format'}, status=400)

    bookings = Booking.objects.filter(
        event_date=event_date,
        status__in=['pending', 'approved', 'confirmed']
    ).select_related('service')

    result = []
    for b in bookings:
        result.append({
            'id': b.id,
            'name': b.name,
            'email': b.email,
            'phone': b.phone,
            'service': b.service.title if b.service else '',
            'time_slot': b.time_slot,
            'location': b.location,
            'message': b.message,
            'status': b.status,
            'created_at': b.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'payment_status': getattr(b, 'payment_status', ''),
        })

    return JsonResponse({
        'date': date_str,
        'status': 'booked' if len(result) > 0 else 'available',
        'bookings': result
    })


@login_required
@require_POST
def admin_update_booking(request, booking_id):
    try:
        booking = get_object_or_404(Booking, id=booking_id)
        data = json.loads(request.body)
        # Allow updating select fields
        booking.name = data.get('name', booking.name)
        booking.email = data.get('email', booking.email)
        booking.phone = data.get('phone', booking.phone)
        service_id = data.get('service_id')
        if service_id:
            try:
                service = Service.objects.get(id=service_id)
                booking.service = service
            except Service.DoesNotExist:
                pass
        if data.get('event_date'):
            booking.event_date = datetime.strptime(data.get('event_date'), '%Y-%m-%d').date()
        booking.time_slot = data.get('time_slot', booking.time_slot)
        booking.location = data.get('location', booking.location)
        booking.admin_notes = data.get('admin_notes', booking.admin_notes)
        if data.get('status'):
            booking.status = data.get('status')
        if data.get('payment_status'):
            booking.payment_status = data.get('payment_status')
        booking.save()
        # notify websocket listeners
        try:
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)('calendar', {
                'type': 'calendar.message',
                'message': {'action': 'booking_updated', 'booking_id': booking.id}
            })
        except Exception:
            pass
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@login_required
@require_POST
def admin_cancel_booking(request, booking_id):
    try:
        booking = get_object_or_404(Booking, id=booking_id)
        booking.status = 'cancelled'
        booking.save()
        # notify websocket listeners
        try:
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)('calendar', {
                'type': 'calendar.message',
                'message': {'action': 'booking_cancelled', 'booking_id': booking.id}
            })
        except Exception:
            pass
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@login_required
@require_POST
def admin_mark_complete(request, booking_id):
    try:
        booking = get_object_or_404(Booking, id=booking_id)
        booking.status = 'completed'
        booking.save()
        # notify websocket listeners
        try:
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)('calendar', {
                'type': 'calendar.message',
                'message': {'action': 'booking_completed', 'booking_id': booking.id}
            })
        except Exception:
            pass
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


def booking_success(request):
    """
    Booking success page with booking details
    """
    # Get the most recent booking for this session (if available)
    booking = None
    booking_id = request.GET.get('booking_id')
    
    if booking_id:
        try:
            booking = Booking.objects.get(id=booking_id)
        except Booking.DoesNotExist:
            pass
    else:
        # Get the most recent booking (fallback)
        booking = Booking.objects.order_by('-created_at').first()
    
    context = {
        'booking': booking,
        'booking_id': booking.id if booking else f"BK{timezone.now().strftime('%Y%m%d%H%M')}",
        'customer_name': booking.name if booking else 'Client',
        'customer_email': booking.email if booking else 'client@example.com'
    }
    
    return render(request, 'main/booking_success.html', context)


# =============================================================================
# SERVICES API ENDPOINTS
# =============================================================================

def api_services(request):
    """
    API endpoint to get all active services
    """
    services = Service.objects.filter(is_active=True).order_by('display_order', '-is_featured', '-created_at')
    
    services_data = []
    for service in services:
        services_data.append({
            'id': service.id,
            'title': service.title,
            'slug': service.slug,
            'service_type': service.service_type,
            'service_type_display': service.get_service_type_display(),
            'tagline': service.tagline,
            'description': service.description,
            'short_description': service.get_short_description_text(),
            'full_description': service.get_full_description_text(),
            'price': str(service.price),
            'formatted_price': service.formatted_price(),
            'price_note': service.price_note,
            'duration': service.duration,
            'features': service.get_features_list(),
            'main_image': service.get_main_image(),
            'cover_image': service.cover_image.url if service.cover_image else None,
            'image': service.image.url if service.image else None,
            'icon': service.icon.url if service.icon else None,
            'gallery_images': service.gallery_images,
            'is_featured': service.is_featured,
            'is_active': service.is_active,
            'display_order': service.display_order,
            'url': service.get_absolute_url(),
            'created_at': service.created_at.isoformat(),
            'updated_at': service.updated_at.isoformat()
        })
    
    return JsonResponse({
        'services': services_data,
        'count': len(services_data)
    })


def api_service_detail(request, slug):
    """
    API endpoint to get single service details
    """
    service = get_object_or_404(Service, slug=slug, is_active=True)
    
    service_data = {
        'id': service.id,
        'title': service.title,
        'slug': service.slug,
        'service_type': service.service_type,
        'service_type_display': service.get_service_type_display(),
        'tagline': service.tagline,
        'description': service.description,
        'short_description': service.get_short_description_text(),
        'full_description': service.get_full_description_text(),
        'price': str(service.price),
        'formatted_price': service.formatted_price(),
        'price_note': service.price_note,
        'duration': service.duration,
        'features': service.get_features_list(),
        'main_image': service.get_main_image(),
        'cover_image': service.cover_image.url if service.cover_image else None,
        'image': service.image.url if service.image else None,
        'icon': service.icon.url if service.icon else None,
        'gallery_images': service.gallery_images,
        'is_featured': service.is_featured,
        'is_active': service.is_active,
        'display_order': service.display_order,
        'url': service.get_absolute_url(),
        'created_at': service.created_at.isoformat(),
        'updated_at': service.updated_at.isoformat()
    }
    
    return JsonResponse(service_data)
