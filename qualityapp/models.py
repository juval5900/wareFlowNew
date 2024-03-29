from django.db import models
from django.utils import timezone
from USERAPP.models import Orders



class Inspection(models.Model):
    order = models.ForeignKey(Orders, on_delete=models.CASCADE)
    packing_quality = models.IntegerField(choices=[(i, i) for i in range(1, 6)])
    box_tampered = models.BooleanField()
    product_packing_safe = models.BooleanField()
    seal_tampered = models.BooleanField()
    shipping_quality = models.IntegerField(choices=[(i, i) for i in range(1, 6)])
    inspected_at = models.DateTimeField(default=timezone.now)
    
    # New field for quality check status
    QUALITY_CHECK_CHOICES = [
        ('not_inspected', 'Not Inspected'),
        ('passed', 'Passed'),
        ('failed', 'Failed'),
    ]
    quality_check_status = models.CharField(max_length=20, choices=QUALITY_CHECK_CHOICES, default='not_inspected')

    def __str__(self):
        return f"Inspection for Order ID: {self.order.order_id}"