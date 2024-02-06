from django.urls import path
from django.contrib import admin
from ecohiveapp import views
from django.contrib.auth import views as auth_views
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

# from ecohiveapp.views import CustomGoogleLoginView

urlpatterns = [
    path('admin/',admin.site.urls),
    path('customer_index', views.customer_index, name='customer_index'),

    path('register.html', views.register, name='register'),
    # path('seller_register.html', views.seller_register, name='seller_register'),
    path('login.html', views.user_login, name='user_login'),
    path('dashlegal.html', views.dashlegal, name='dashlegal'),
    path('dashseller.html', views.dashseller, name='dashseller'),
    path('successseller.html', views.successseller, name='successseller'),
    path('successaddcategory.html', views.successaddcategory, name='successaddcategory'),
    path('successaddproduct.html', views.successaddproduct, name='successaddproduct'),
    path('admindash', views.admindash, name='admindash'),
    path('addcategory', views.addcategory, name='addcategory'),
    path('viewcategory', views.viewcategory, name='viewcategory'),
    path('sellerorder', views.sellerorder, name='sellerorder'),


    path('viewaddproduct', views.viewaddproduct, name='viewaddproduct'),
    path('addproducts', views.addproducts, name='addproducts'),
    path('viewproducts', views.viewproducts, name='viewproducts'),
    path('edit_product/<int:product_id>/', views.edit_product, name='edit_product'),
    path('delete_product/<int:product_id>/', views.delete_product, name='delete_product'),
    path('category/<int:category_id>/delete/', views.delete_category, name='delete_category'),
    path('edit_category/<int:category_id>/', views.edit_category, name='edit_category'),

    path('approve_certification/<int:certification_id>/', views.approve_certification, name='approve_certification'),
    path('reject_certification/<int:certification_id>/', views.reject_certification, name='reject_certification'), 

    path('delete_add_product/<int:product_id>/', views.delete_add_product, name='delete_add_product'),
    path('logout/', views.loggout, name='loggout'),
    path('check_email/', views.check_email, name='check_email'),
    path('check_username/', views.check_username, name='check_username'),
    # Include allauth URLs for other authentication-related views
    path('accounts/', include('allauth.urls')),
    # Include allauth.socialaccount URLs
    path('accounts/', include('allauth.socialaccount.urls')),

    path('profile', views.profile, name='profile'),
    path('user_dashboard/', views.user_dashboard, name='user_dashboard'),
    path('user_list', views.user_list, name='user_list'),
    path('toggle_user_status/<int:user_id>/', views.user_status_toggle, name='user_status_toggle'),



    path('viewstock', views.view_products, name='viewstock'),
    path('product-summary/<int:pk>/edit/', views.edit_product_stock, name='edit_product_stock'),


    path('password_reset/',auth_views.PasswordResetView.as_view(),name='password_reset'),
    path('password_reset/done/',auth_views.PasswordResetDoneView.as_view(),name='password_reset_done'),
    path('reset/<uidb64>/<token>/',auth_views.PasswordResetConfirmView.as_view(),name='password_reset_confirm'),
    path('reset/done/',auth_views.PasswordResetCompleteView.as_view(),name='password_reset_complete'),

    #customerpages
    path('wishlist', views.wishlist, name='wishlist'),
    path('product/<int:product_id>/', views.product_single, name='product_single'),
    path('checkout', views.checkout, name='checkout'),
    path('cart/', views.cart_view, name='cart'),
    path('remove_from_cart/<int:cart_item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('update_cart_item/<int:cart_item_id>/', views.update_cart_item, name='update_cart_item'),
    # path('payment', views.payment, name='payment'),
    path('orders/', views.orders, name='orders'),
    path('view_orders', views.view_orders, name='view_orders'),
    path('generate_pdf/<int:order_id>/', views.generate_pdf, name='generate_pdf'),



    path('about', views.about, name='about'),
    path('shop', views.shop, name='shop'),
    path('category/vegetables/', views.category_vegetables, name='category_vegetables'),
    path('category/electronics/', views.category_electronics, name='category_electronics'),

    # #payment
    # path('paymenthandler/', views.paymenthandler, name='paymenthandler'),
    # path('paymentsuccess/', views.paymentsuccess, name='productsuccess'),



    path('live_search/', views.live_search, name='live_search'),
    path('submit_review/', views.submit_review, name='submit_review'),

    # path('add_review/', views.add_review, name='add_review'),




]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)