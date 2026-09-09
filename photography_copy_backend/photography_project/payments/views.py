from django.http import JsonResponse
from django.views.decorators.http import require_POST


@require_POST
def process_payment(request):
    # Placeholder endpoint for payment gateway integration.
    return JsonResponse({
        'success': False,
        'message': 'Payment gateway integration not configured yet.',
    }, status=501)


def payment_success(request):
    return JsonResponse({
        'success': True,
        'message': 'Payment successful placeholder.',
    })
