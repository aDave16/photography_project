from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db.models import Sum
from main.models import Booking
from payments.models import PaymentTransaction, Expense, Invoice
from datetime import date
from django.utils import timezone
from django.http import JsonResponse
import uuid

def is_admin(user):
    return user.is_authenticated and user.is_staff

@login_required
@user_passes_test(is_admin)
def financial_cloud_overview(request):
    # Calculations
    bookings = Booking.objects.all()
    
    # Revenue (only paid transactions)
    total_revenue = PaymentTransaction.objects.filter(status='paid').aggregate(Sum('amount'))['amount__sum'] or 0
    
    current_month = timezone.now().month
    current_year = timezone.now().year
    month_revenue = PaymentTransaction.objects.filter(
        status='paid', 
        paid_at__month=current_month, 
        paid_at__year=current_year
    ).aggregate(Sum('amount'))['amount__sum'] or 0
    
    total_expenses = Expense.objects.aggregate(Sum('amount'))['amount__sum'] or 0
    net_profit = total_revenue - total_expenses
    
    # Calculate pending properly (iterate over bookings or annotated queries)
    advance_received = 0
    pending_payments_total = 0
    overdue_bookings = []
    pending_bookings = []
    
    for b in bookings:
        rb = b.remaining_balance
        if rb > 0:
            pending_payments_total += rb
            pending_bookings.append(b)
            # Overdue logic: if event_date is past or near past. (Assume due date is event_date)
            # or if it exists on booking. We'll use event_date as due date for now.
            if b.event_date and b.event_date < date.today():
                overdue_bookings.append(b)
                
        # advance received is roughly "partially paid" or just all total_paid
        advance_received += b.total_paid

    recent_expenses = Expense.objects.all()[:5]
    recent_payments = PaymentTransaction.objects.filter(status='paid').order_by('-paid_at')[:5]

    from main.views import _get_dashboard_stats
    context = _get_dashboard_stats()
    
    context.update({
        'total_revenue': total_revenue,
        'month_revenue': month_revenue,
        'total_expenses': total_expenses,
        'net_profit': net_profit,
        'pending_payments_total': pending_payments_total,
        'advance_received': advance_received,
        'fc_total_bookings': bookings.count(),
        'fc_pending_bookings': pending_bookings[:10],
        'fc_overdue_bookings': overdue_bookings,
        'fc_recent_expenses': recent_expenses,
        'fc_recent_payments': recent_payments,
        'active_tab': 'invoices'
    })
    return render(request, 'main/admin_dashboard.html', context)


@login_required
@user_passes_test(is_admin)
def record_payment(request, booking_id=None):
    if request.method == 'POST':
        b_id = booking_id or request.POST.get('booking_id')
        booking = get_object_or_404(Booking, id=b_id)
        
        amount = request.POST.get('amount', 0)
        payment_method = request.POST.get('payment_method', 'Other')
        transaction_id = request.POST.get('transaction_reference', '')
        notes = request.POST.get('payment_notes', '')
        payment_date_str = request.POST.get('payment_date')
        
        try:
            amount = float(amount)
            if amount <= 0:
                messages.error(request, "Amount must be greater than zero.")
                return redirect('financial_cloud_overview')
                
            payment_date = timezone.now()
            if payment_date_str:
                from django.utils.dateparse import parse_datetime
                payment_date = parse_datetime(payment_date_str) or timezone.now()

            # Create Record
            tx = PaymentTransaction.objects.create(
                booking=booking,
                transaction_id=transaction_id or f"TXN-{uuid.uuid4().hex[:8].upper()}",
                amount=amount,
                payment_method=payment_method,
                status='paid',
                notes=notes,
                created_by=request.user,
                paid_at=payment_date
            )
            
            # Update Booking Status Logic
            if booking.remaining_balance == 0:
                booking.payment_status = 'paid'
            elif booking.total_paid > 0:
                booking.payment_status = 'pending' # or 'partially_paid' if it was available, we'll keep it pending/unpaid
            booking.save()
            
            messages.success(request, f"Successfully recorded payment of ₹{amount} for {booking.name}")
            
        except Exception as e:
            messages.error(request, f"Error recording payment: {str(e)}")
            
        return redirect('admin_bookings')
        
    return redirect('financial_cloud_overview')


@login_required
@user_passes_test(is_admin)
def manage_expenses(request):
    if request.method == 'POST':
        category = request.POST.get('category')
        amount = request.POST.get('amount')
        date_str = request.POST.get('date')
        description = request.POST.get('description')
        booking_id = request.POST.get('booking_id')
        notes = request.POST.get('notes')
        
        try:
            booking = Booking.objects.get(id=booking_id) if booking_id else None
            Expense.objects.create(
                category=category,
                amount=amount,
                date=date_str,
                description=description,
                booking=booking,
                notes=notes
            )
            messages.success(request, "Expense added successfully.")
        except Exception as e:
            messages.error(request, f"Error adding expense: {str(e)}")
            
        return redirect('manage_expenses')
        
    expenses = Expense.objects.all()
    bookings = Booking.objects.all()
    context = {
        'expenses': expenses,
        'bookings': bookings,
        'active_menu': 'financial_cloud'
    }
    return render(request, 'main/admin/financial_cloud/expenses.html', context)


@login_required
@user_passes_test(is_admin)
def generate_invoice(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    # Generate simple Invoice record if not exists
    invoice = booking.invoices.first()
    if not invoice:
        invoice = Invoice.objects.create(
            booking=booking,
            invoice_number=f"INV-{str(booking.id).zfill(4)}-{timezone.now().strftime('%y%m')}",
            total_amount=booking.calculated_total_amount
        )
    
    context = {
        'booking': booking,
        'invoice': invoice,
        'transactions': booking.payment_transactions.filter(status='paid')
    }
    return render(request, 'main/admin/financial_cloud/invoice_template.html', context)


@login_required
@user_passes_test(is_admin)
def payment_reminder(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    context = {
        'booking': booking
    }
    return render(request, 'main/admin/financial_cloud/reminder_template.html', context)
