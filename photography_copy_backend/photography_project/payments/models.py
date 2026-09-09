from django.db import models
from django.conf import settings


class PaymentTransaction(models.Model):
    booking = models.ForeignKey(
        'main.Booking',
        on_delete=models.CASCADE,
        related_name='payment_transactions',
        null=True,
        blank=True,
    )
    transaction_id = models.CharField(max_length=128, unique=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=10, default='INR')
    payment_method = models.CharField(max_length=50, blank=True)
    status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending'),
            ('paid', 'Paid'),
            ('failed', 'Failed'),
            ('refunded', 'Refunded'),
        ],
        default='pending',
    )
    paid_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Payment Transaction'
        verbose_name_plural = 'Payment Transactions'

    def __str__(self):
        return f'{self.transaction_id} - {self.amount} {self.currency} ({self.status})'
