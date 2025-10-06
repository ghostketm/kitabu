from django.db import models
from django.conf import settings

class Payment(models.Model):
    """
    Track M-Pesa payment transactions.
    Essential for reconciliation and customer support.
    """
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    ]
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='payments'
    )
    
    # M-Pesa details
    phone_number = models.CharField(max_length=15)
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=87.00)
    merchant_request_id = models.CharField(max_length=100, unique=True)
    checkout_request_id = models.CharField(max_length=100, unique=True)
    
    # Transaction tracking
    mpesa_receipt_number = models.CharField(max_length=100, blank=True, null=True)
    transaction_date = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    callback_response = models.JSONField(null=True, blank=True)  # Store full callback
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['checkout_request_id']),
            models.Index(fields=['status', '-created_at']),
        ]
    
    def __str__(self):
        return f"Payment {self.merchant_request_id} - {self.status}"