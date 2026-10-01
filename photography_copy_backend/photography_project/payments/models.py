from django.db import models
from django.conf import settings
import uuid


class PaymentTransaction(models.Model):
    booking = models.ForeignKey(
        'main.Booking',
        on_delete=models.CASCADE,
        related_name='payment_transactions',
        null=True,
        blank=True,
    )
    transaction_id = models.CharField(max_length=128, blank=True, null=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=10, default='INR')
    payment_method = models.CharField(
        max_length=50, 
        choices=[
            ('Cash', 'Cash'),
            ('UPI', 'UPI'),
            ('Bank Transfer', 'Bank Transfer'),
            ('Cheque', 'Cheque'),
            ('Other', 'Other')
        ],
        blank=True
    )
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
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True
    )
    paid_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Payment Transaction'
        verbose_name_plural = 'Payment Transactions'

    def __str__(self):
        txn_str = self.transaction_id or 'No ID'
        return f'{txn_str} - {self.amount} {self.currency} ({self.status})'

class Expense(models.Model):
    category = models.CharField(
        max_length=50,
        choices=[
            ('Travel', 'Travel'),
            ('Equipment Rental', 'Equipment Rental'),
            ('Editing', 'Editing'),
            ('Album Printing', 'Album Printing'),
            ('Staff', 'Staff'),
            ('Marketing', 'Marketing'),
            ('Food', 'Food'),
            ('Venue', 'Venue-related'),
            ('Other', 'Other'),
        ]
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField()
    description = models.CharField(max_length=255)
    booking = models.ForeignKey(
        'main.Booking',
        on_delete=models.SET_NULL,
        related_name='expenses',
        null=True,
        blank=True,
    )
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date', '-created_at']
        verbose_name = 'Expense'
        verbose_name_plural = 'Expenses'

    def __str__(self):
        return f'{self.category} - {self.amount} on {self.date}'


class Invoice(models.Model):
    booking = models.ForeignKey(
        'main.Booking',
        on_delete=models.CASCADE,
        related_name='invoices',
    )
    invoice_number = models.CharField(max_length=50, unique=True)
    date_issued = models.DateField(auto_now_add=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    pdf_file = models.FileField(upload_to='invoices/%Y/%m/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-date_issued']
        verbose_name = 'Invoice'
        verbose_name_plural = 'Invoices'

    def __str__(self):
        return f'Invoice {self.invoice_number} for {self.booking.name}'

