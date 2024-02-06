from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, UserProfile
from django.contrib import admin
from .models import Certification
from .models import Category, Product
from .models import Seller  # Import the Seller model from your models.py file


class UserProfileInline(admin.StackedInline):
    model = UserProfile

class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'is_active', 'is_admin', 'is_seller', 'is_legaladvisor')

    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal Info', {'fields': ('first_name', 'last_name', 'email')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_admin', 'is_seller', 'is_legaladvisor', 'groups', 'user_permissions')}),
        ('Important Dates', {'fields': ('last_login', 'date_joined')}),
    )
# admin.site.register(Seller)
# admin.site.register(User, CustomUserAdmin)

@admin.register(Certification)  # Update the model name to OrganicCertification
class CertificationAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'certification_authority', 'certification_number','address', 'certification_image', 'timestamp','is_approved')  # Add 'certification_number' to list_display
    list_filter = ('certification_authority',)  # Add a comma to make it a tuple
    search_fields = ('first_name', 'last_name', 'certification_authority')

    # @admin.register(Category)
    # class CategoryAdmin(admin.ModelAdmin):
    #     list_display = ('category_name','category_description')  # Customize the fields to display
    #     list_filter = ('category_name',)  # Add filters if needed
    #     search_fields = ('category_name', 'category_description')  # Add search fields if needed

# @admin.register(Product)
# class ProductAdmin(admin.ModelAdmin):
#     list_display = ('product_name', 'category', 'product_price','product_image','seller','product_stock')  # Customize the fields to display
#     list_filter = ('category', 'product_price')  # Add filters if needed
#     search_fields = ('product_name', 'product_description')  # Add search fields if needed

from .models import ProductSummary

@admin.register(ProductSummary)
class ProductSummaryAdmin(admin.ModelAdmin):
    list_display = ('product_name', 'total_stock')
    
@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'name', 'email', 'phone_number')
    
    fieldsets = (
        ('User Info', {
            'fields': ('user', 'name', 'email', 'phone_number'),
        }),
        ('Additional Info', {
            'fields': ('profile_pic', 'address'),
        }),
    )

from .models import Cart

class CartAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'quantity', 'date_added')
    list_filter = ('user', 'date_added')
    search_fields = ('user__username', 'product__product_name')

admin.site.register(Cart, CartAdmin)

from .models import Payment, BillingDetails
@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('user', 'order_id', 'amount', 'currency', 'payment_status', 'payment_date')
    list_filter = ('payment_status', 'currency')
    search_fields = ('user__username', 'order_id')

@admin.register(BillingDetails)
class BillingDetailsAdmin(admin.ModelAdmin):
    list_display = ('user', 'first_name', 'last_name', 'email', 'phone')
    search_fields = ('user__username', 'email')

from .models import Order
from .models import OrderItem

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('user', 'total_price', 'order_date', 'payment_status')
    list_filter = ('payment_status', 'order_date')
    search_fields = ('user__username', 'razorpay_order_id')
    readonly_fields = ('razorpay_order_id',)  # If you want to make razorpay_order_id read-only in the admin

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'product', 'seller', 'quantity', 'price', 'total_price')
    list_filter = ('order', 'product', 'seller')
    search_fields = ('order__user__username', 'product__product_name', 'seller__username')

from .models import Wishlist

class WishlistAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'quantity', 'date_added')
    list_filter = ('user', 'date_added')
    search_fields = ('user__username', 'product__product_name')

admin.site.register(Wishlist, WishlistAdmin)

from .models import Review  # Import the Review model
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['product', 'user', 'rating']
    list_filter = ['product', 'user']
    search_fields = ['product__product_name', 'user__username']
    list_per_page = 20  # Number of items displayed per page in the admin list view

# Register the Review model with the custom admin options
admin.site.register(Review, ReviewAdmin)