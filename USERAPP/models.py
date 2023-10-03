from django.db import models
from django.utils import timezone
from django.conf import settings
from django.contrib.auth.models import User

class Category(models.Model):
    category_id = models.AutoField(primary_key=True)
    category_name = models.CharField(max_length=100)

    def __str__(self):
        return self.category_name
    
class Subcategory(models.Model):
    subcategory_id = models.AutoField(primary_key=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    subcategory_name = models.CharField(max_length=100)

    def __str__(self):
        return self.subcategory_name


class Product(models.Model):
    product_id = models.AutoField(primary_key=True)
    product_name = models.CharField(max_length=255)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    subcategory = models.ForeignKey(Subcategory, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    threshold_value = models.PositiveIntegerField()
    product_image = models.ImageField(upload_to='product_images/')  # Add this field
    is_active = models.BooleanField(default=True)  # Flag to indicate whether the product is active
    deleted_at = models.DateTimeField(null=True, blank=True)  # Timestamp when the product was soft-deleted

    def soft_delete(self):
        self.is_active = False
        self.deleted_at = timezone.now()
        self.save()

    def undelete(self):
        self.is_active = True
        self.deleted_at = None
        self.save()

    def __str__(self):
        return self.product_name  
    
   
class Supplier(models.Model):
    supplier_id = models.AutoField(primary_key=True)
    supplier_name = models.CharField(max_length=255)
    supplier_address = models.TextField()  # You can adjust the max_length as needed
    contact_number = models.CharField(max_length=15, unique=True)  # Make contact_number unique
    supplier_email = models.CharField(max_length=255, unique=True)  
    supplier_type = models.CharField(max_length=50)  # You can adjust the max_length as needed
    supplier_image = models.ImageField(upload_to='supplier_images/')  # Field for supplier image
    is_active = models.BooleanField(default=True)  # Flag to indicate whether the supplier is active
    deleted_at = models.DateTimeField(null=True, blank=True)  # Timestamp when the supplier was soft-deleted

    def soft_delete(self):
        self.is_active = False
        self.deleted_at = timezone.now()
        self.save()

    def undelete(self):
        self.is_active = True
        self.deleted_at = None
        self.save()

    def __str__(self):
        return self.supplier_name
    
class Orders(models.Model):
    order_id = models.AutoField(primary_key=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE)
    order_datetime = models.DateTimeField(unique=True)
    order_status = models.CharField(max_length=255)
    warehouse = models.CharField(max_length=255, null=True)
    quantity = models.PositiveIntegerField()
    buying_price = models.DecimalField(max_digits=10, decimal_places=2,default='100')  # New field for buying price
    total_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)  # New field for total price
    is_active = models.BooleanField(default=True)
    cancelled_at = models.DateTimeField(null=True, blank=True)
    is_stored = models.BooleanField(default=False)
    delivered_at = models.DateTimeField(null=True)

    def soft_delete(self):
        self.is_active = False
        self.cancelled_at = timezone.now()
        self.save()

    def undelete(self):
        self.is_active = True
        self.cancelled_at = None
        self.save()

    def save(self, *args, **kwargs):
        # Calculate the total price based on buying price and quantity
        self.total_price = self.buying_price * self.quantity
        super().save(*args, **kwargs)

    def __str__(self):
        return str(self.order_id)

class UserProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, blank=True, null=True)
    country = models.CharField(max_length=15, blank=True, null=True)
    district = models.CharField(max_length=15, blank=True, null=True)
    addressline1 = models.CharField(max_length=15, blank=True, null=True)
    addressline2 = models.CharField(max_length=15, blank=True, null=True)
    phone_no = models.CharField(max_length=15, blank=True, null=True)
    state = models.CharField(max_length=15, blank=True, null=True)
    city = models.CharField(max_length=15, blank=True, null=True)
    pin_code = models.CharField(max_length=6, blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)  # Add this line for date of birth
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)  # Add this line for profile picture
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        if self.user:
            return self.user.first_name
        else:
            return "UserProfile with no associated user"
        
        
class StorageLocation(models.Model):
    id = models.AutoField(primary_key=True)
    location_name = models.CharField(max_length=255, unique=True)
    row_capacity = models.IntegerField(default=0)
    column_capacity = models.IntegerField(default=0)
    shelf_capacity = models.PositiveIntegerField(blank=True, null=True)  # Added shelf_capacity field

    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.location_name

        
        
class ProductLocation(models.Model):
    id = models.AutoField(primary_key=True)
    order = models.ForeignKey(Orders, on_delete=models.CASCADE,default=0)
    storage_location = models.ForeignKey(StorageLocation, on_delete=models.CASCADE)
    shelf_number = models.CharField(max_length=50)  # Added shelf_number field
    row_number = models.CharField(max_length=50)
    column_number = models.CharField(max_length=50)

    def allocate_location(self, storage_location, shelf_number, row_number, column_number):
        self.storage_location = storage_location
        self.shelf_number = shelf_number
        self.row_number = row_number
        self.column_number = column_number
        self.save()

    def deallocate_location(self):
        self.storage_location = None
        self.shelf_number = ""
        self.row_number = ""
        self.column_number = ""
        self.save()

    def __str__(self):
        return f"{self.storage_location.location_name} ({self.quantity})"
    
class UserRole(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=255)  # Define your roles appropriately, e.g., 'admin', 'user', 'manager', etc.
    is_allocated = models.BooleanField(default=False)  # Added the is_allocated field with a default value of False

    def __str__(self):
        return self.user.username
