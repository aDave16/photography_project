from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from .models import Inquiry


@csrf_exempt
def submit_inquiry(request):
    """
    Handle inquiry submission from contact form.
    POST only with CSRF protection and validation.
    """
    if request.method != 'POST':
        return JsonResponse({
            'success': False,
            'message': 'Invalid request method'
        }, status=405)
    
    try:
        # Extract and validate form data
        name = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip()
        phone = request.POST.get('phone', '').strip()
        event_type = request.POST.get('event_type', 'wedding')
        message = request.POST.get('message', '').strip()
        
        # Basic validation
        if not name or not email or not message:
            return JsonResponse({
                'success': False,
                'message': 'Name, email, and message are required fields'
            }, status=400)
        
        # Create inquiry record
        inquiry = Inquiry.objects.create(
            name=name,
            email=email,
            phone=phone,
            event_type=event_type,
            message=message
        )
        
        # Send confirmation email to customer
        try:
            subject = "Your Inquiry Has Been Received | Dhrumil Bajak Photography"
            customer_message = f"""
Dear {name},

Thank you for your inquiry about {inquiry.get_event_type_display()}.

We have successfully received your inquiry and our team will contact you shortly.

Best regards,
Dhrumil Bajak Photography Team
Studio: +91 99980 0154
Email: bajakdhrumil@gmail.com
            """
            
            send_mail(
                subject=subject,
                message=customer_message,
                from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@example.com'),
                recipient_list=[email],
                fail_silently=False,
            )
        except Exception as e:
            print(f"Failed to send customer email: {e}")
        
        # Send notification email to admin
        try:
            admin_subject = f"New Inquiry: {name} - {inquiry.get_event_type_display()}"
            admin_message = f"""
New inquiry received:

Name: {name}
Email: {email}
Phone: {phone}
Event Type: {inquiry.get_event_type_display()}
Message: {message}

Received: {inquiry.created_at.strftime('%Y-%m-%d %H:%M:%S')}
            """
            
            send_mail(
                subject=admin_subject,
                message=admin_message,
                from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@example.com'),
                recipient_list=[getattr(settings, 'ADMIN_EMAIL', 'bajakdhrumil@gmail.com')],
                fail_silently=False,
            )
        except Exception as e:
            print(f"Failed to send admin notification: {e}")
        
        # Return success response
        return JsonResponse({
            'success': True,
            'message': 'Your inquiry has been successfully sent. Our team will contact you shortly.'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'An error occurred: {str(e)}'
        }, status=500)
