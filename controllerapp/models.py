from django.db import models

from USERAPP.models import Orders

# Create your models here.
class Stock(models.Model):
    order = models.ForeignKey(Orders, on_delete=models.CASCADE)
    is_stored = models.BooleanField(default=False)

    def __str__(self):
        return f'Stock for Order ID: {self.order.order_id}'