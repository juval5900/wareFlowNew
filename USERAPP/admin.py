from django.contrib import admin
from .models import Product, Category,Subcategory,Supplier,Orders,UserProfile


admin.site.register(Subcategory)
admin.site.register(Product)
admin.site.register(Category)
admin.site.register(Supplier)
admin.site.register(Orders)
admin.site.register(UserProfile)