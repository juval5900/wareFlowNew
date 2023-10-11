from django.utils import timezone 
from django.db import models
from django.db.models import Sum
from USERAPP.models import Orders, Product


from django.db import models

class Stock(models.Model):
    order = models.ForeignKey(Orders, on_delete=models.CASCADE, related_name='stocks')  # Add related_name='stocks'
    is_stored = models.BooleanField(default=False)
    sector = models.CharField(max_length=255, null=True, blank=True)
    row_start = models.CharField(max_length=255, null=True, blank=True)
    column_start = models.CharField(max_length=255, null=True, blank=True)  
    column_end = models.CharField(max_length=255, null=True, blank=True)
    remaining_quantity = models.PositiveIntegerField(null=True, blank=True)
    is_active = models.BooleanField(default=True)  # Add the is_active field

    def save(self, *args, **kwargs):
        # Set the default value of remaining_quantity to order.quantity if it's not provided
        if self.remaining_quantity is None:
            self.remaining_quantity = self.order.quantity
        super().save(*args, **kwargs)  # Call the superclass's save method

    def __str__(self):
        return f'Stock for Order ID: {self.order.order_id}'
    



class Sales(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE)
    date_field = models.DateTimeField(default=timezone.now, editable=False)
    quantity = models.PositiveIntegerField()
    delivery_address = models.TextField()
    sales_price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=255)
    buyer_name = models.CharField(max_length=255)
    buyer_contact_info = models.CharField(max_length=255)
    deleted = models.BooleanField(default=False) 

    # New fields
    total_sales_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, editable=False)
    total_buying_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, editable=False)
    profit = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, editable=False)

    def save(self, *args, **kwargs):
        # Calculate total sales price
        self.total_sales_price = self.sales_price * self.quantity

        # Calculate total buying price by following the ForeignKey relationship
        self.total_buying_price = self.stock.order.buying_price * self.quantity

        # Calculate profit
        self.profit = self.total_sales_price - self.total_buying_price

        super().save(*args, **kwargs)  # Call the superclass's save method

    def calculate_total_profit_per_week(self):
        # Calculate the total profit for each week
        sales_by_week = Sales.objects.filter(
            date_field__week=self.date_field.week,  # Filter by week
            date_field__year=self.date_field.year  # Filter by year
        ).aggregate(total_profit=Sum('profit'))['total_profit']

        return sales_by_week
    def __str__(self):
        return f'Sales for Product: {self.product.product_name}'