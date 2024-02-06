from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from USERAPP.models import Orders, Product,Category


# Create your models here.


# class User(AbstractUser):
#     is_admin= models.BooleanField('Is admin', default=False)
#     is_customer = models.BooleanField('Is customer', default=False)
#     is_seller = models.BooleanField('Is seller', default=False)
#     is_legaladvisor= models.BooleanField('Is advisor', default=False)
    
#     groups = models.ManyToManyField(
#         'auth.Group',
#         related_name='user_groups',
#         related_query_name='user_group'
#     )
    
#     user_permissions = models.ManyToManyField(
#         'auth.Permission',
#         related_name='user_permissions',
#         related_query_name='user_permission'
#     )


     
# @receiver(post_save, sender=User)
# def create_seller_profile(sender, instance, created, **kwargs):
#     if created and instance.is_seller:
#         Seller.objects.create(user=instance)

# @receiver(post_save, sender=User)
# def save_seller_profile(sender, instance, **kwargs):
#     if instance.is_seller:
#         instance.seller.save()


class UserProfile(models.Model):
    user = models.OneToOneField(get_user_model(), on_delete=models.CASCADE)
    # Add other fields related to the user profile
    name = models.CharField(max_length=100,null=True, blank=True)
    email = models.EmailField(max_length=255,null=True, blank=True)
    profile_pic = models.ImageField(upload_to='profile_pics/', null=True, blank=True)
    # gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    phone_number = models.CharField(max_length=20, null=True, blank=True)
    address = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return self.user.username

class Certification(models.Model):
    APPROVED = 'approved'
    REJECTED = 'rejected'
    PENDING = 'pending'
    
    APPROVAL_CHOICES = [
        (APPROVED, 'Approved'),
        (REJECTED, 'Rejected'),
        (PENDING, 'Pending'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=1)
    certification_image = models.ImageField(upload_to='certification_image/', null=True, blank=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    expiry_date_from = models.DateField()
    certification_authority = models.CharField(max_length=200)
    phone_number = models.CharField(max_length=15, default="N/A")  # Change the default value as needed
    certification_number = models.CharField(max_length=50, default="N/A")  # Change the default value as needed
    address = models.CharField(max_length=255,default=1)
    timestamp = models.DateTimeField(auto_now_add=True)
    is_approved = models.CharField(
        max_length=10,
        choices=APPROVAL_CHOICES,
        default=PENDING,
    )
class Seller(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    certification = models.ForeignKey(Certification, on_delete=models.CASCADE,default=1)

    # Other fields specific to the Seller model
    def __str__(self):
        return self.user.username 
# class Category(models.Model):
#     category_name = models.CharField(max_length=100)
#     category_description = models.TextField()
#     # default_product_price = models.DecimalField(max_digits=10, decimal_places=2)
#     # category_image = models.ImageField(upload_to='category_images/', null=True, blank=True)  # Default product price for this category
#     # Other fields for the category...

#     def __str__(self):
#         return self.category_name


# class Product(models.Model):
#     product_name = models.CharField(max_length=100)
#     product_description = models.TextField()
#     category = models.ForeignKey(Category, on_delete=models.CASCADE)
#     product_price = models.DecimalField(max_digits=10, decimal_places=2)
#     product_stock = models.IntegerField(default=0)  # Add the default value here
#     product_image = models.ImageField(upload_to='category_images/', null=True, blank=True)
#     seller = models.ForeignKey(Seller, on_delete=models.CASCADE, default=1)  
#     def __str__(self):
#         return self.product_name
    
#     def save(self, *args, **kwargs):
#         super(Product, self).save(*args, **kwargs)
#         # After saving the product, update the ProductSummary
#         summary, created = ProductSummary.objects.get_or_create(product_name=self.product_name)
#         summary.update_total_stock()
    

from django.db.models import Sum
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

class ProductSummary(models.Model):
    product_name = models.CharField(max_length=100, unique=True)  # Make sure product names are unique in this summary model
    total_stock = models.IntegerField(default=0)
    product_image = models.ImageField(upload_to='product_images/', blank=True, null=True)
    product_description = models.TextField(blank=True, null=True)
    product_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)  # Add default value

    def __str__(self):
        return self.product_name

    def update_total_stock(self):
        # Calculate the total stock for this product name from the Product model
        total_stock = Product.objects.filter(product_name=self.product_name).aggregate(total_stock=Sum('product_stock'))['total_stock']
        self.total_stock = total_stock or 0
        self.save()
    @receiver(post_save, sender=Product)
    @receiver(post_delete, sender=Product)
    def update_product_summary(sender, instance, **kwargs):
        product_name = instance.product_name

        # Calculate the total stock for the given product name
        total_stock = Product.objects.filter(product_name=product_name).aggregate(total_stock=Sum('product_stock'))['total_stock']

        # Update or create the corresponding ProductSummary instance
        product_summary, created = ProductSummary.objects.get_or_create(product_name=product_name)
        product_summary.total_stock = total_stock or 0
        product_summary.save()
    
class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    date_added = models.DateTimeField(auto_now_add=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    image = models.ImageField(upload_to='cart_item_images/', blank=True, null=True)  # Add image field

    def __str__(self):
        return f"{self.user.username}'s Cart Item - {self.product.product_name}"

    def save(self, *args, **kwargs):
        # Calculate the price based on the product's price per kg and the quantity
        self.price = self.product.product_price * self.quantity
        super().save(*args, **kwargs)

class Payment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # ForeignKey to the User model
    order_id = models.CharField(max_length=255)  # Razorpay Order ID
    amount = models.DecimalField(max_digits=10, decimal_places=2)  # Amount in INR
    currency = models.CharField(max_length=3, default='INR')  # Currency code
    payment_status = models.CharField(max_length=20)  # Payment status (e.g., 'success', 'pending', 'failed')
    payment_date = models.DateTimeField(auto_now_add=True)  # Date and time of payment
    # Add more fields as needed, such as product, etc.

    def __str__(self):
        return f"Payment ID: {self.id}, Order ID: {self.order_id}"
    
class BillingDetails(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # If you want to associate the billing details with a user
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    state = models.CharField(max_length=255)
    street_address = models.CharField(max_length=255)
    apartment_suite_unit = models.CharField(max_length=255, blank=True, null=True)  # Optional field
    town_city = models.CharField(max_length=255)
    postcode_zip = models.CharField(max_length=20)
    phone = models.CharField(max_length=20)
    email = models.EmailField()

    def __str__(self):
        return f"{self.first_name} {self.last_name}'s Billing Details"


class Order(models.Model):
    class PaymentStatusChoices(models.TextChoices):
        PENDING = 'pending', 'Pending'
        SUCCESSFUL = 'successful', 'Successful'
        FAILED = 'failed', 'Failed'

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    products = models.ManyToManyField(Product)  # Assuming you have a Product model
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    order_date = models.DateTimeField(auto_now_add=True)
    razorpay_order_id = models.CharField(max_length=255, default=None)
    payment_status = models.CharField(
        max_length=20, choices=PaymentStatusChoices.choices, default=PaymentStatusChoices.PENDING)
    def _str_(self):
        return self.user.username 
class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    seller = models.ForeignKey(Seller, on_delete=models.CASCADE)  # Assuming the seller is also a User
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)

    def save(self, *args, **kwargs):
        # Calculate the total price for this order item based on quantity and price
        self.total_price = self.quantity * self.price
        super(OrderItem, self).save(*args, **kwargs)
        
        # Update the total order price in the associated Order model
        order = self.order
        order.total_order_price = sum(order_item.total_price for order_item in order.orderitem_set.all())
        order.save()
    
class Wishlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    date_added = models.DateTimeField(auto_now_add=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    image = models.ImageField(upload_to='Wishlist_item_images/', blank=True, null=True)  # Add image field

    def __str__(self):
        return f"{self.user.username}'s Wishlist Item - {self.product.product_name}"
    
class Review(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.PositiveIntegerField()  # You can define the rating field according to your requirements (e.g., 1 to 5 stars)
    comment = models.TextField(blank=True, null=True)  # Optional comment field

    def __str__(self):
        return f"Review for {self.product.product_name} by {self.user.username}"