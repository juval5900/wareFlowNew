from django.contrib import admin
from .models import Product, Category, Subcategory, Supplier, UserProfile, StorageLocation, ProductLocation,Orders,UserRole

admin.site.register(Subcategory)
admin.site.register(Product)
admin.site.register(Category)
admin.site.register(Supplier)
admin.site.register(UserProfile)
admin.site.register(StorageLocation)
admin.site.register(ProductLocation)
admin.site.register(Orders)
admin.site.register(UserRole)