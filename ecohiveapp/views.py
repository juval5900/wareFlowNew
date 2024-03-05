from audioop import reverse
from django.shortcuts import render, redirect
from django.db.models import Sum, F, Value
from django.db.models.functions import Coalesce
from USERAPP import models
from controllerapp.models import Stock
from .forms import SignUpForm, LoginForm
from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect, HttpResponse
from django.contrib.auth import authenticate, login as auth_login, logout, get_user_model
from django.contrib import messages
from django.contrib.auth.models import User
from django.http import JsonResponse
from .models import User
from .forms import SignUpForm, LoginForm
from .forms import CertificationForm
from django.contrib.auth import authenticate, login
from ecohiveapp.models import User 
from .models import Certification
from django.shortcuts import get_object_or_404

from django.http import JsonResponse
from django.contrib.auth.decorators import login_required 
from .models import Category,Product,Seller,UserProfile
from django.db import IntegrityError  
from allauth.socialaccount.providers.oauth2.views import OAuth2LoginView
from allauth.account.views import SignupView
from allauth.socialaccount.providers.oauth2.client import OAuth2Error
from allauth.socialaccount.providers.oauth2.views import OAuth2LoginView
from .models import Cart
from django.core.mail import send_mail
from django.conf import settings

# from .forms import CustomUserCreationForm
  
# Make sure the import path is correct

# Create your views here.


from .models import ProductSummary  # Import your ProductSummary model


def customer_index(request):
    products = Product.objects.all()
    if request.user.is_authenticated:
        user_cart_items = Cart.objects.filter(user=request.user)
        cart_item_count = user_cart_items.count()
    else:
        cart_item_count = 0

    context = {
            'products': products,
            'cart_item_count': cart_item_count,
        }  # Fetch all ProductSummary instances
    return render(request, 'templates2/index.html', context)

def register(request):
    msg = None
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            msg = 'user created'
            return redirect('user_login')
        else:
            msg = 'form is not valid'
    else:
        form = SignUpForm()
    return render(request,'templates2/register.html', {'form': form, 'msg': msg})



def user_login(request):
    form = LoginForm(request.POST or None)
    msg = None

    if request.method == 'POST':
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)

            if user is not None:
                login(request, user)
                auth_login(request,user)
                request.session['customer_id'] = user.id
                request.session['user_type'] = 'customer'
                return redirect('customer_index')
            else:
                msg = 'Invalid credentials'
        else:
            msg = 'Error validating form'

    return render(request, 'templates2/login.html', {'form': form, 'msg': msg})

@login_required
def dashseller(request):
    existing_certification = Certification.objects.filter(user=request.user).first()

    if existing_certification:
        return render(request, 'dashseller.html', {'existing_certification': existing_certification})

    if request.method == 'POST':
        form = CertificationForm(request.POST, request.FILES)
        if form.is_valid():
            print("Form is valid")  # Debug statement
            certification = form.save(commit=False)
            certification.user = request.user
            certification.save()
            subject = 'Your Certification Details has been sent to Legal Advisor'
            message = 'Your Request for certification details has been sent to the Legal Advisor and pednding '
            from_email = settings.EMAIL_HOST_USER  # Your sender email address
            recipient_list = [certification.user.email]
            send_mail(subject, message, from_email,recipient_list)
            print("Certification saved successfully")  # Debug statement
            return redirect('successseller')  # Redirect to a success page
        else:
            messages.error(request, 'Please fill in all required fields.')
            # Debug statement
    else:
        form = CertificationForm()

    return render(request, 'templates2/dashseller.html', {
        'form': form,
        'existing_certification': existing_certification,
    })

@login_required
def dashlegal(request):
    # Retrieve Certification objects
    seller_applications = Certification.objects.all()

    # Retrieve User roles for each Certification applicant
    user_roles = {}
    for application in seller_applications:
        # Ensure the user associated with the Certification exists
        user = get_object_or_404(User, id=application.user_id)

        # Retrieve user roles
        user_roles[application.id] = {
            'is_admin': user.is_admin,
            'is_customer': user.is_customer,
            'is_seller': user.is_seller,
            'is_legaladvisor': user.is_legaladvisor,
        }

    context = {
        'seller_applications': seller_applications,
        'user_roles': user_roles,  # Include user roles in the context
    }
    return render(request, 'templates2/dashlegal.html', context)


def loggout(request):
    print('Logged Out')
    logout(request)
    if 'username' in request.session:
        del request.session['username']
        request.session.clear()
    return redirect('user_login')

def check_email(request):
    email = request.GET.get('email')
    exists = User.objects.filter(email=email).exists()
    return JsonResponse({'exists': exists})

def check_username(request):
    username = request.GET.get('username')
    exists = User.objects.filter(username=username).exists()
    return JsonResponse({'exists': exists})

import json

@login_required
def admindash(request):
    # Calculate the total number of users
    total_users = User.objects.count()

    # Calculate the number of products added
    total_products = Product.objects.count()

    # Calculate the number of certified users
    total_certified_users = Certification.objects.filter(is_approved='approved').count()

    # Calculate the total number of orders
    total_orders = Order.objects.count()

    # Prepare data for the chart
    order_labels = ['Total Orders']
    order_data = [total_orders]

    context = {
        'total_users': total_users,
        'total_products': total_products,
        'total_certified_users': total_certified_users,
        'total_orders': total_orders,
        'order_labels': json.dumps(order_labels),  # Convert to JSON format for JavaScript
        'order_data': json.dumps(order_data),      # Convert to JSON format for JavaScript
    }
    return render(request, 'templates2/admindash/admindash.html', context)

@login_required
def addcategory(request):
    if request.method == 'POST':
        try:
            # Retrieve form data directly from the request
            category_name = request.POST.get('category_name')
            formatted_category_name = category_name.capitalize()
            category_description = request.POST.get('category_description')

            # Check if the category already exists
            category, created = Category.objects.get_or_create(
                category_name=formatted_category_name,
                defaults={'category_description': category_description}
            )

            if created:
                # The category was created
                messages.success(request, 'Category created successfully.')
            else:
                # The category already exists
                messages.error(request, 'Category already exists.')

            return redirect('successaddcategory')  # Redirect back to the admin page

        except IntegrityError as e:
            # Handle other database integrity errors if needed
            messages.error(request, 'Error creating category: {}'.format(str(e)))

    return render(request, 'templates2/admindash/addcategory.html')

def viewcategory(request):
    categories = Category.objects.all()
    return render(request, 'templates2/admindash/viewcategory.html', {'categories': categories})

def successseller(request):
    return render(request, 'templates2/sellerdash/successseller.html')

def successaddcategory(request):
    return render(request, 'templates2/admindash/successaddcategory.html')

def successaddproduct(request):
    return render(request, 'templates2/sellerdash/successaddproduct.html')

@login_required
def viewaddproduct(request):
    existing_certification = Certification.objects.filter(user=request.user).first()

    seller_instance = Seller.objects.get(user=request.user)
    if not existing_certification:
        messages.error(request, 'You need an approved certification to add products.')
        return redirect('dashseller')
        # Query the Product model to retrieve products associated with the current user's Seller instance
    user_products = Product.objects.filter(seller=seller_instance)

    # Your other view logic goes here...

    return render(request, 'templates2/sellerdash/viewaddproduct.html', {'user_products': user_products})

@login_required
def viewproducts(request):
    # Retrieve all products
    all_products = Product.objects.all()

    context = {
        'all_products': all_products,
    }
    return render(request, 'templates2/admindash/viewproducts.html', context)

@login_required
def delete_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    if request.method == 'POST':
        # Handle form submission for deleting the product
        product.delete()
        return redirect('viewproducts')

    # Render the delete product template
    return render(request, 'templates2/admindash/delete_product.html', {'product': product})

# @login_required
# def addproducts(request):
#     existing_certification = Certification.objects.filter(user=request.user).first()

#     if existing_certification:
#         certification_status = existing_certification.is_approved
#     else:
#         certification_status = 'pending'  # Set a default value if no certification exists

#     if certification_status == 'approved':

#         if request.method == 'POST':
#             product_name = request.POST.get('product_name')
#             formatted_product_name = product_name.capitalize()
#             product_description = request.POST.get('product_description')
#             select_category_id = request.POST.get('select_category')
#             product_price = request.POST.get('product_price')
#             product_stock = request.POST.get('product_stock')
#             product_image = request.FILES.get('product_image')

#         # Retrieve the selected category
#             category = Category.objects.get(id=select_category_id)

#         # Check if a product with the same name already exists in the selected category
#         # Check if the current user has already added a product with the same name in this category
#             existing_product = Product.objects.filter(
#                 product_name=formatted_product_name,
#                 category=category,
#                 seller__user=request.user  # Filter by the current user
#             )

#             if existing_product.exists():
#                 error_message = "You have already added a product with this name in the selected category."
#                 return render(request, 'sellerdash/addproducts.html', {'error_message': error_message})

#         # Retrieve the seller associated with the currently logged-in user
#             seller = Seller.objects.get(user=request.user)

#         # Create and save the Product instance
#             product = Product(
#                 product_name=formatted_product_name,
#                 product_description=product_description,
#                 category=category,
#                 product_price=product_price,
#                 product_stock=product_stock,
#                 product_image=product_image,
#                 seller=seller  # Associate the seller with the product
#             )
#             product.save()

#             return redirect('successaddproduct')  # Redirect to a success page or your desired destination

#         categories = Category.objects.all()  # Retrieve all Category objects from the database

#         context = {
#         'categories': categories,
#         'certification_status': certification_status,
#   # Pass the categories queryset to the template context
#          }
#         return render(request, 'templates2/sellerdash/addproducts.html', context)
#     else:
#         return render(request, 'templates2/sellerdash/addproducts.html', {'certification_status': certification_status})

def delete_category(request, category_id):
    # Get the category object to delete
    category = get_object_or_404(Category, pk=category_id)

    associated_products = Product.objects.filter(category=category)

    if request.method == 'POST':
        # Delete all associated products
        associated_products.delete()
        
        # Delete the category
        category.delete()
        
        return redirect('viewcategory')  # Redirect to the category list page

    return render(request, 'templates2/admindash/delete_category.html', {'category': category, 'associated_products': associated_products})

def edit_category(request, category_id):
    category = get_object_or_404(Category, id=category_id)

    if request.method == 'POST':
        new_category_name = request.POST['category_name']
        
        # Check if a category with the same name already exists
        if Category.objects.filter(category_name=new_category_name).exclude(id=category.id).exists():
            messages.error(request, 'Category with this name already exists.')
        else:
            # Update the category if no duplicate name found
            category.category_name = new_category_name
            category.category_description = request.POST['category_description']
            category.save()
            messages.success(request, 'Category updated successfully.')
            return redirect('viewcategory')  # Replace 'category_list' with your category list URL name

    return render(request, 'templates2/admindash/edit_category.html', {'category': category})

def delete_certification(request, certification_id):
    certification = get_object_or_404(Certification, id=certification_id)
    certification.delete()
    return redirect('dashlegal')

#USER DASHBOARD
@login_required
def profile(request):
    try:
        user_profile = UserProfile.objects.get(user=request.user)
    except UserProfile.DoesNotExist:
        # If UserProfile doesn't exist, create one for the user
        user_profile = UserProfile(user=request.user)

    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        profile_pic = request.FILES.get('profile_pic')
        phone_number = request.POST.get('phone_number')
        address = request.POST.get('address')

        if 'profile_pic' in request.FILES:
            profile_pic = request.FILES['profile_pic']
            user_profile.profile_pic = profile_pic

        user_profile.name = name
        user_profile.phone_number = phone_number
        user_profile.address = address
        request.user.email = email

        user_profile.save()
        request.user.save()
        messages.success(request, 'Profile updated successfully')
        return redirect('profile')

    return render(request, 'templates2/userprofile/user_profile.html', {'user_profile': user_profile})


def user_dashboard(request):
    return render(request,'templates2/userprofile/user_dashboard.html')

def user_list(request):
    users = User.objects.all()
    return render(request, 'templates2/admindash/userlist.html', {'users': users})
    
def user_status_toggle(request, user_id):
    if request.method == "POST":
        action = request.POST.get("action")
        user = User.objects.get(pk=user_id)  # Use your custom user model

        if action == "deactivate":
            user.is_active = False
        elif action == "activate":
            user.is_active = True

        user.save()

    # Redirect back to the user list page after processing the request.
    return redirect('user_list')


def approve_certification(request, certification_id):
    certification = get_object_or_404(Certification, id=certification_id)
    if request.method == 'POST':
        certification.is_approved = Certification.APPROVED  # Set it to 'approved'
        certification.save()
        subject = 'Congratulations! Your License Has Been Approved'
        message = 'We are delighted to inform you that your license application has been successfully approved. Your dedication and compliance with the necessary requirements have made this approval possible. We appreciate your patience throughout the process. With your approved license, you are now officially recognized and authorized to add your plants. '
        from_email = settings.EMAIL_HOST_USER  # Your sender email address
        recipient_list = [certification.user.email]
        send_mail(subject, message, from_email,recipient_list)
    return redirect('dashlegal')

def reject_certification(request, certification_id):
    certification = get_object_or_404(Certification, id=certification_id)
    if request.method == 'POST':
        certification.is_approved = Certification.REJECTED  # Set it to 'rejected'
        certification.save()
        subject = 'Important Notice: Your License Application Has Been Declined'
        message = 'We regret to inform you that your recent seller application has been declined, and as a result, you will not be able to add your products on our platform. '
        from_email = settings.EMAIL_HOST_USER  # Your sender email address
        recipient_list = [certification.user.email]
        send_mail(subject, message, from_email,recipient_list)
    return redirect('dashlegal')

from .models import ProductSummary

def view_products(request):
    product_summaries = ProductSummary.objects.all()
    return render(request, 'templates2/admindash/viewstock.html', {'product_summaries': product_summaries})

def edit_product_stock(request, pk):
    product_summary = get_object_or_404(ProductSummary, pk=pk)

    if request.method == 'POST':
        # Handle the form submission and update the product details directly in the model
        product_summary.product_description = request.POST['product_description']
        product_summary.product_price = request.POST['product_price']
        product_summary.product_image = request.FILES['product_image']
        product_summary.save()
        return redirect('viewstock')  # Redirect to the product summary page after editing

    return render(request, 'templates2/admindash/editstock.html', {'product_summary': product_summary})

# def edit_product(request, product_id):
#     product = get_object_or_404(Product, id=product_id)
#     categories = Category.objects.all()

#     if request.method == 'POST':
#         # Update the product fields based on form input
#         product.product_description = request.POST['product_description']

#         category_id = request.POST.get('select_category')
#         if category_id:
#             category = get_object_or_404(Category, id=category_id)
#             product.category = category

#         product.product_price = request.POST['product_price']
#         product.product_stock = request.POST['product_stock']

#         if 'product_image' in request.FILES:
#             product.product_image = request.FILES['product_image']

#         product.save()
#         messages.success(request, 'Product updated successfully.')
#         return redirect('viewaddproduct')

#     return render(request, 'templates2/sellerdash/edit_product.html', {'product': product, 'categories': categories})


def delete_add_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    if request.method == 'POST':
        # Handle form submission for deleting the product
        product.delete()
        return redirect('viewaddproduct')  # Redirect to the product list page

    return render(request, 'templates2/sellerdash/delete_add_product.html', {'product': product})

def wishlist(request):
    # Add your logic here
    return render(request, 'wishlist.html')

from django.db.models import Avg


@login_required
def product_single(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    user = request.user
    # product = Product.objects.get(pk=product_id)

    # Retrieve reviews for the specific product
    reviews = Review.objects.filter(product_id=product_id)
    user_ratings = [review.rating for review in reviews]
    # In your view
    average_rating = Review.objects.filter(product=product).aggregate(Avg('rating'))['rating__avg']
    star_rating = convert_to_star_rating(average_rating)

    # Check if the product is already in the user's cart
    existing_cart_item = Cart.objects.filter(user=user, product=product).first()
    is_in_cart = existing_cart_item is not None

    # Retrieve related products with the same seller
    # related_products = Product.objects.exclude(id=product.product_id).filter(seller__id__in=Product.objects.filter(id=product.product_id).values('seller__id'))[:4]
    # other_related_products = Product.objects.exclude(id=product.product_id).exclude(seller=product.seller)[:4]

    # seller_address = product.seller.certification.address

            # Calculate total stock count as the sum of remaining stock and quantity of orders where order status is 'order placed'
    total_stock_count = Stock.objects.filter(order__product=product).aggregate(total_stock=Coalesce(Sum('remaining_quantity'), Value(0)))['total_stock']


    if request.method == 'POST':
        # If it's a POST request, get the quantity from the form
        quantity = int(request.POST.get('quantity', 1))  # Default to 1 if not provided

        if quantity <= total_stock_count:
            # If the quantity is valid, proceed to add/update the cart
            image = product.product_image

            if not is_in_cart:
                # If the product is not in the cart, add it to the cart with the specified quantity
                Cart.objects.create(user=user, product=product, quantity=quantity, image=image)
            else:
                # If the product is already in the cart, update the quantity
                existing_cart_item.quantity += quantity
                existing_cart_item.save()

            return redirect('cart')  # Redirect to the cart page or any other page you prefer
        else:
            # If the quantity is greater than the available stock, display an error message
            messages.error(request, 'Not enough stock available.')

    # Include the product stock and related products in the context
    context = {
        'product': product,
        'is_in_cart': is_in_cart,
        # 'product_stock': product.product_stock,  # Pass the product stock to the template
        # 'related_products': related_products,
        # 'other_related_products': other_related_products,  # Pass other related products to the template
        # 'seller_address': seller_address,
        'reviews': reviews,
        'user_ratings': user_ratings,  
        'average_rating': star_rating, # A list of user ratings.


    }

    return render(request, 'templates2/product-single.html', context)


def remove_from_cart(request, cart_item_id):
    cart_item = get_object_or_404(Cart, id=cart_item_id)

    if request.method == 'POST':
        cart_item.delete()

    return redirect('cart')

def about(request):
    # Add your logic here
    return render(request, 'templates2/about.html')
def shop(request):
    products = Product.objects.all()
    
    return render(request, 'templates2/shop.html', {'products': products})

def category_vegetables(request):
    # Filter products by the "Vegetables" category
    vegetables_category = Category.objects.get(category_name='Vegetables')
    vegetable_products = Product.objects.filter(category=vegetables_category)

    # Pass the filtered products to the template
    context = {
        'category_products': {'Vegetables': vegetable_products},
    }

    return render(request, 'category_vegetables.html', context)

# def category_electronics(request):
#     electronics_category = Category.objects.get(category_name='Electronics')
#     electronics_products = Product.objects.filter(category=electronics_category)
#     total_stock_count = Stock.objects.filter(order__product=product).aggregate(total_stock=Coalesce(Sum('remaining_quantity'), Value(0)))['total_stock']

#     # Pass the filtered products to the template
#     context = {
#         'category_products': {'Fruits': electronics_products},
#         'total_stock_count': total_stock_count,
#     }
#     print(electronics_products)
#     return render(request, 'templates2/category_fruits.html', context)




def category_electronics(request):
    electronics_category = Category.objects.get(category_name='Electronics')
    electronics_products = Product.objects.filter(category=electronics_category)

    # Dictionary to store total stock count for each product
    product_stock_counts = {}
    for product in electronics_products:
        total_stock_count = Stock.objects.filter(order__product=product).aggregate(total_stock=Coalesce(Sum('remaining_quantity'), Value(0)))['total_stock']
        product_stock_counts[product] = total_stock_count

    context = {
        'category_products': {'Fruits': electronics_products},
        'product_stock_counts': product_stock_counts,
    }
    return render(request, 'templates2/category_fruits.html', context)

def paymentsuccess(request):
    # Add your logic here
    return render(request, 'templates2/paymentsuccess.html')

@login_required
def cart_view(request):
    # Assuming you have user authentication and each user has a unique cart
    user = request.user

    # Retrieve the user's cart items
    cart_items = Cart.objects.filter(user=user)
    cart_item_count = cart_items.count()

    # Calculate the total price of items in the cart
    total_price = sum(cart_item.product.product_price * cart_item.quantity for cart_item in cart_items)

    context = {
        'cart_items': cart_items,
        'total_price': total_price,
        'cart_item_count': cart_item_count,
    }

    return render(request, 'templates2/cart.html', context)

def update_cart_item(request, cart_item_id):
    if request.method == 'POST':
        # Retrieve the cart item
        cart_item = Cart.objects.get(id=cart_item_id)

        # Get the new quantity from the form
        new_quantity = int(request.POST.get('quantity'))
        
        product = cart_item.product
            
        product_name = product.product_name
        total_remaining_stock = Stock.objects.filter(order__product__product_name=product_name).aggregate(
            total_remaining_stock=Sum('remaining_quantity'))['total_remaining_stock'] or 0

        if new_quantity > 0 and new_quantity <= total_remaining_stock:
            # Update the cart item's quantity if it's a valid value
            cart_item.quantity = new_quantity
            cart_item.save()
        else:
            # Display an error message if the quantity is invalid
            messages.error(request, 'Invalid quantity.')

    # Redirect back to the cart view
    return redirect('cart')


from .models import BillingDetails, Cart, Order, OrderItem  # Import your models here
from django.shortcuts import render, redirect
from decimal import Decimal

from django.db import transaction

@transaction.atomic
def checkout(request):
    total_price = 0  # Initialize total_price outside the if block
    cart_items = Cart.objects.filter(user=request.user)  # Define cart_items here
    billing_details = None  # Initialize billing_details to None

    # Check if billing details exist for the user
    if BillingDetails.objects.filter(user=request.user).exists():
        billing_details = BillingDetails.objects.get(user=request.user)

    if request.method == 'POST' and 'place_order' in request.POST:
        # If billing details already exist, you can skip processing the form and just calculate the total price
        if not billing_details:
            # Retrieve and process the form data for billing details
            first_name = request.POST.get('firstname')
            last_name = request.POST.get('lastname')
            state = request.POST.get('state')
            street_address = request.POST.get('streetaddress')
            apartment_suite_unit = request.POST.get('apartmentsuiteunit')
            town_city = request.POST.get('towncity')
            postcode_zip = request.POST.get('postcodezip')
            phone = request.POST.get('phone')
            email = request.POST.get('emailaddress')

            # Create BillingDetails object (assuming BillingDetails is a separate model)
            billing_details = BillingDetails(
                user=request.user,
                first_name=first_name,
                last_name=last_name,
                state=state,
                street_address=street_address,
                apartment_suite_unit=apartment_suite_unit,
                town_city=town_city,
                postcode_zip=postcode_zip,
                phone=phone,
                email=email,
            )
            billing_details.save()

        total_price = sum(item.product.product_price * item.quantity for item in cart_items)

        # Convert total_price to a float before storing it in the session
        request.session['order_total'] = float(total_price)

        # Redirect to the payment page to complete the order
        return redirect('payment')

    # If it's not a POST request or not a place order request, continue displaying the cart items
    total_price = sum(item.product.product_price * item.quantity for item in cart_items)

    # Convert total_price to a float before passing it to the template
    context = {
        'cart_items': cart_items,
        'total_price': float(total_price),
        'billing_details': billing_details,  # Pass billing_details to the template
    }

    return render(request, 'templates2/checkout.html', context)

#payment
from django.shortcuts import render
import razorpay
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponseBadRequest

razorpay_client = razorpay.Client(
    auth=(settings.RAZOR_KEY_ID, settings.RAZOR_KEY_SECRET))

def payment(request):
    cart_items = Cart.objects.filter(user=request.user)
    total_price = Decimal(sum(cart_item.product.product_price * cart_item.quantity for cart_item in cart_items))
    
    currency = 'INR'

    # Set the 'amount' variable to 'total_price'
    amount = int(total_price*100)
    # amount=20000

    # Create a Razorpay Order
    razorpay_order = razorpay_client.order.create(dict(
        amount=amount,
        currency=currency,
        payment_capture='0'
    ))

    # Order id of the newly created order
    razorpay_order_id = razorpay_order['id']
    callback_url = '/paymenthandler/'

    order = Order.objects.create(
        user=request.user,
        total_price=total_price,
        razorpay_order_id=razorpay_order_id,
        payment_status=Order.PaymentStatusChoices.PENDING,
    )

    # Add the products to the order
    for cart_item in cart_items:
        product = cart_item.product
        price = product.product_price
        quantity = cart_item.quantity
        total_item_price = price * quantity


        seller = product.suppliers.first()  # Get the first supplier
        # Create an OrderItem for this product
        order_item = OrderItem.objects.create(
            order=order,
            product=product,
            seller=seller,  # Use the selected seller  # Set the seller of the product as the seller of the order item
            quantity=quantity,
            price=price,
            total_price=total_item_price,
        )

    # Save the order to generate an order ID
    order.save()

    # Create a context dictionary with all the variables you want to pass to the template
    context = {
        'cart_items': cart_items,
        'total_price': total_price,
        'razorpay_order_id': razorpay_order_id,
        'razorpay_merchant_key': settings.RAZOR_KEY_ID,
        'razorpay_amount': amount,  # Set to 'total_price'
        'currency': currency,
        'callback_url': callback_url,
    }

    return render(request, 'templates2/payment.html', context=context)

from django.db.models import Sum



@csrf_exempt
def paymenthandler(request):
    if request.method == "POST":
        payment_id = request.POST.get('razorpay_payment_id', '')
        razorpay_order_id = request.POST.get('razorpay_order_id', '')
        signature = request.POST.get('razorpay_signature', '')

        # Verify the payment signature.
        params_dict = {
            'razorpay_order_id': razorpay_order_id,
            'razorpay_payment_id': payment_id,
            'razorpay_signature': signature
        }
        result = razorpay_client.utility.verify_payment_signature(params_dict)

        if not result:
            # Signature verification failed.
            return render(request, 'templates2/paymentfail.html')

        # Signature verification succeeded.
        # Retrieve the order from the database
        try:
            order = Order.objects.get(razorpay_order_id=razorpay_order_id)
        except Order.DoesNotExist:
            return HttpResponseBadRequest("Order not found")

        if order.payment_status == Order.PaymentStatusChoices.SUCCESSFUL:
            # Payment is already marked as successful, ignore this request.
            return HttpResponse("Payment is already successful")

        if order.payment_status != Order.PaymentStatusChoices.PENDING:
            # Order is not in a pending state, do not proceed with stock update.
            return HttpResponseBadRequest("Invalid order status")

        # Capture the payment amount
        amount = int(order.total_price * 100)  # Convert Decimal to paise
        razorpay_client.payment.capture(payment_id, amount)

        # Update the order with payment ID and change status to "Successful"
        order.payment_id = payment_id
        order.payment_status = Order.PaymentStatusChoices.SUCCESSFUL
        order.save()

        # Remove the products from the cart and update stock
        cart_items = Cart.objects.filter(user=request.user)
        for cart_item in cart_items:
            product = cart_item.product
            
            product_name = product.product_name
            total_remaining_stock = Stock.objects.filter(order__product__product_name=product_name).aggregate(
                total_remaining_stock=Sum('remaining_quantity'))['total_remaining_stock'] or 0

            
            
            
            
            if total_remaining_stock >= cart_item.quantity:
                # Decrease the product stock and update ProductSummary
                total_remaining_stock -= cart_item.quantity
                product.save()
                summary, created = ProductSummary.objects.get_or_create(product_name=product.product_name)
                summary.update_total_stock()
                # Remove the item from the cart
                cart_item.delete()
            else:
                # Handle insufficient stock, you can redirect or show an error message
                return HttpResponseBadRequest("Insufficient stock for some items")

        # Redirect to a payment success page
        return redirect('orders')
    

    return HttpResponseBadRequest("Invalid request method")


@login_required
def orders(request):
    # Retrieve orders for the currently logged-in user
    user_orders = Order.objects.filter(user=request.user)
    
    context = {
        'orders': user_orders,
    }
    
    return render(request, 'templates2/orders.html', context)

def view_orders(request):
    all_orders = Order.objects.all()

    return render(request, 'templates2/admindash/view_orders.html', {'all_orders': all_orders})

@login_required
def sellerorder(request):
    current_user = request.user

    # Check if the current user is a seller
    if current_user.is_seller:
        # If the user is a seller, retrieve the seller profile
        current_seller = current_user.seller

        # Retrieve the orders for the current seller
        seller_orders = OrderItem.objects.filter(seller=current_seller)

        context = {
            'seller': current_seller,
            'seller_orders': seller_orders,
        }

    return render(request, 'templates2/sellerdash/sellerorder.html', context)




from django.http import JsonResponse
from .models import Product

def live_search(request):
    if request.method == 'GET':
        search_query = request.GET.get('query', '')
        results = Product.objects.filter(product_name__icontains=search_query)
        product_data = []

        for product in results:
            # Perform any necessary calculations here
            product_info = {
                'name': product.product_name,
                'prod_id':product.product_id,
                'price': product.product_price, 
                'img': product.product_image.url, 
               
                 # Use the correct field for the image URL
            }
            product_data.append(product_info)

        return JsonResponse({'products': product_data})  

from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa  # Import for PDF generation
from .models import Order

def generate_pdf(request, order_id):
    order = get_object_or_404(Order, id=order_id)

    # Create a Django HTML template for the PDF content
    template = get_template('templates2/pdf_order.html')
    context = {'order': order}
    html = template.render(context)

    # Create a PDF file using the HTML content
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="Invoice{order_id}.pdf"'

    # Generate PDF from HTML using xhtml2pdf
    pisa_status = pisa.CreatePDF(html, dest=response)
    if pisa_status.err:
        return HttpResponse('Error generating PDF', status=500)

    return response

from .models import Review

def submit_review(request):
    if request.method == "POST":
        product_id = request.POST.get("product_id")
        rating = request.POST.get("rating")
        comment = request.POST.get("comment")
        user = request.user
        product = get_object_or_404(Product, id=product_id)

        # Check if the user has already reviewed the product
        existing_review = Review.objects.filter(product=product, user=user).first()

        if existing_review:
            # If the user has already reviewed, update the existing review
            existing_review.rating = rating
            existing_review.comment = comment
            existing_review.save()
        else:
            # If the user hasn't reviewed, create a new review
            review = Review(
                product=product,
                user=user,
                rating=rating,
                comment=comment
            )
            review.save()

    return redirect("orders")

def convert_to_star_rating(average_rating):
    if average_rating is not None:
            star_rating = '★' * int(average_rating)
            return star_rating
    else:
        return ""
