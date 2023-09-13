from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login as auth_login, logout, get_user_model
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from .models import Category, Product, ProductLocation, StorageLocation,Subcategory,Supplier,Orders,UserProfile
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404
from django.core.serializers.json import DjangoJSONEncoder
from django.core.paginator import Paginator
from django.utils import timezone
from .forms import UserProfileForm
from django.views import View  
from django.db import transaction
from django import forms



def index(request):
    return render(request, 'index.html')

def login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            auth_login(request, user)
            request.session['user_id'] = user.id
            request.session['username'] = user.username
            request.session['name'] = user.first_name

            # Retrieve the user_profile
            user_profile = get_object_or_404(UserProfile, user=user)

            # Set the profile picture URL in the session
            request.session['profile_picture_url'] = user_profile.profile_picture.url
            
            return redirect('index')  # Replace with your desired URL
        else:
            messages.error(request, "Invalid credentials")
            return redirect('login')
    else:
        return render(request, 'login.html')


def register(request):
    if request.method == "POST":
        first_name = request.POST.get('name')
        username = request.POST.get('email')
        email = request.POST.get('email')
        password = request.POST.get('pass')

        if User.objects.filter(username=username).exists() or User.objects.filter(email=email).exists():
            messages.error(request, "Email Already Exists")
            return render(request, "register.html", {'email': username})
        else:
            user = User.objects.create_user(first_name=first_name,username=username,email=email,password=password)
            user.save()
            messages.success(request, "Registration successful! Please log in.")
            return redirect('login')
    else:
        return render(request, "register.html")


def loggout(request):
    print('Logged Out')
    logout(request)
    if 'username' in request.session:
        del request.session['username']
    return redirect('login')

def check_email(request):
    email = request.GET.get('email')
    exists = User.objects.filter(email=email).exists()
    return JsonResponse({'exists': exists})

def check_username(request):
    username = request.GET.get('username')
    exists = User.objects.filter(username=username).exists()
    return JsonResponse({'exists': exists})


def notifications(request):
    return render(request, 'notifications.html')

def error(request):
    return render(request, '404.html')

def account(request):
    return render(request, 'account.html')

def charts(request):
    return render(request, 'charts.html')

def docs(request):
    return render(request, 'docs.html')

def help(request):
    return render(request, 'help.html')

def inventory(request):
  categories = Category.objects.all()
  context = {'categories': categories}
  return render(request, 'inventory.html', context)

def settings(request):
    return render(request, 'settings.html')


def add_product(request):
    if request.method == 'POST':
        category_id = request.POST['category']
        subcategory_id = request.POST.get('subcategory')
        category = Category.objects.get(pk=category_id)
        subcategory = Subcategory.objects.get(pk=subcategory_id)
        product_image = request.FILES['productImage']
        product_name = request.POST['productName']
        #buying_price = request.POST['buyingPrice']
        quantity = request.POST['quantity']
        # unit = request.POST['unit']
        # expiry_date = request.POST['expiryDate']
        threshold_value = request.POST['thresholdValue']
        

        product = Product(category=category, 
                          subcategory=subcategory,
                          product_image=product_image, 
                          product_name=product_name, 
                          quantity=quantity,
                          threshold_value=threshold_value)
        product.save()

        # Redirect to a success page or wherever you want
        return redirect('list_products')  # Change 'success_page' to the actual URL


def list_products(request):

    active_products = Product.objects.filter(is_active=True).order_by('product_id')
    products_per_page = 12
    paginator = Paginator(active_products, products_per_page)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    categories = Category.objects.all()
    return render(request, 'inventory.html', {'page': page, 'categories': categories})

def get_subcategories(request):
    category_id = request.GET.get('category_id')
    subcategories = Subcategory.objects.filter(category=category_id)
    subcategory_options = [{'id': subcategory.subcategory_id, 'name': subcategory.subcategory_name} for subcategory in subcategories]
    return JsonResponse({'subcategories': subcategory_options})


@csrf_exempt
def delete_product(request, product_id):
    try:
        product = Product.objects.get(pk=product_id)
        product.soft_delete()
        return JsonResponse({'message': 'Product deleted successfully'})
    except Product.DoesNotExist:
        return JsonResponse({'error': 'Product not found'}, status=404)
    
    
def update_product(request, product_id):
    if request.method == 'POST':
        # Get the product instance based on the product ID
        product = get_object_or_404(Product, product_id=product_id)

        # Process the form data
        product.product_name = request.POST.get('productNameupdate')
        product.category_id = request.POST.get('categoryupdate')
        product.subcategory_id = request.POST.get('subcategoryupdate')
        #product.buying_price = request.POST.get('buyingPriceupdate')
        product.quantity = request.POST.get('quantityupdate')
        #product.unit = request.POST.get('unitupdate')
        #product.expiry_date = request.POST.get('expiryDateupdate')
        product.threshold_value = request.POST.get('thresholdValueupdate')
        
        
        # Check if a new product image is provided
        if request.FILES.get('productImageupdate'):
            product.product_image = request.FILES['productImageupdate']

        # Save the updated product
        product.save()

        # Return a JSON response indicating success
        return redirect('list_products')

    # Handle GET requests or other HTTP methods
    return JsonResponse({'message': 'Invalid request method'}, status=400)


def get_product_details(request, product_id):
    # Retrieve the product based on the product_id or return a 404 if not found
    product = get_object_or_404(Product, product_id=product_id)  # Use the correct field name for the primary key

    image_url = product.product_image.url if product.product_image else ''
    existing_image_name = product.product_image.name if product.product_image else ''
    # Convert the product data into a dictionary
    product_data = {
        'product_id': product.product_id,
        'category_id': product.category_id,
        'subcategory_id': product.subcategory_id,
        'product_name': product.product_name,
        #'buying_price': product.buying_price,
        'quantity': product.quantity,
        #'unit': product.unit,
       # 'expiry_date': product.expiry_date.strftime('%Y-%m-%d'),  # Format date as string
        'threshold_value': product.threshold_value,
        'product_image_url': image_url,  # Send the image URL
        'product_image_name': existing_image_name, 
        # Add other product fields as needed
    }

    # Return the product data as JSON response
    return JsonResponse(product_data)


def delete_multiple_products(request):
    if request.method == 'POST':
        # Get the list of product IDs to deactivate from the POST data
        product_ids = request.POST.getlist('product_ids[]')

        # Validate and sanitize the product_ids here if needed

        # Loop through the selected products and soft delete each one
        for product_id in product_ids:
            try:
                product = Product.objects.get(pk=product_id)
                product.soft_delete()
            except Product.DoesNotExist:
                pass  # Handle cases where the product doesn't exist

        # Redirect to the 'list_products' view after successful deactivation
        return redirect('list_products')



def add_suppliers(request):
    if request.method == 'POST':
        supplier_name = request.POST['supplierName']
        supplier_address = request.POST['supplierAddress']
        contact_number = request.POST['contactNumber']
        supplier_email = request.POST['supplieremail']
        supplier_type = request.POST['supplierType']
        supplier_image = request.FILES['supplierImage']
        

        supplier = Supplier(supplier_name=supplier_name, supplier_address=supplier_address,contact_number=contact_number, supplier_type=supplier_type,
                          supplier_image=supplier_image,supplier_email=supplier_email)
        supplier.save()

        # Redirect to a success page or wherever you want
        return redirect('list_suppliers')  # Change 'success_page' to the actual URL
    
    
def list_suppliers(request):
    active_suppliers = Supplier.objects.filter(is_active=True).order_by('supplier_id')
    suppliers_per_page = 12
    paginator = Paginator(active_suppliers, suppliers_per_page)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, 'suppliers.html', {'page': page})


@csrf_exempt
def delete_suppliers(request, supplier_id):
    try:
        supplier = Supplier.objects.get(pk=supplier_id)
        supplier.soft_delete()
        return JsonResponse({'message': 'Supplier deleted successfully'})
    except Product.DoesNotExist:
        return JsonResponse({'error': 'Supplier not found'}, status=404)
    
    
def update_supplier(request, supplier_id):
    if request.method == 'POST':
        # Get the product instance based on the product ID
        supplier = get_object_or_404(Supplier, supplier_id=supplier_id)

        # Process the form data
        supplier.supplier_name = request.POST['supplierNameupdate']
        supplier.supplier_address = request.POST['supplierAddressupdate']
        supplier.contact_number = request.POST['contactNumberupdate']
        supplier.supplier_email= request.POST['supplieremailupdate']
        supplier.supplier_type = request.POST['supplierTypeupdate']
        supplier.supplier_image = request.FILES['supplierImageupdate']
        # Check if a new supplier image is provided
        if request.FILES.get('supplierImageupdate'):
            supplier.supplier_image = request.FILES['supplierImageupdate']

        # Save the updated supplier
        supplier.save()

        # Return a JSON response indicating success
        return redirect('list_suppliers')

    # Handle GET requests or other HTTP methods
    return JsonResponse({'message': 'Invalid request method'}, status=400)


def get_supplier_details(request, supplier_id):
    # Retrieve the supplier based on the supplier_id or return a 404 if not found
    supplier = get_object_or_404(Supplier, supplier_id=supplier_id)  # Use the correct field name for the primary key

    image_url = supplier.supplier_image.url if supplier.supplier_image else ''
    existing_image_name = supplier.supplier_image.name if supplier.supplier_image else ''


    # Convert the supplier data into a dictionary
    supplier_data = {    
        'supplier_id': supplier.supplier_id,
        'supplier_name': supplier.supplier_name,
        'supplier_address': supplier.supplier_address,
        'contact_number': supplier.contact_number,
        'supplier_email':supplier.supplier_email,
        'supplier_type': supplier.supplier_type,
        'supplier_image_url': image_url,  # Send the image URL
        'supplier_image_name': existing_image_name, 
    }

    # Return the supplier data as JSON response
    return JsonResponse(supplier_data)


def delete_multiple_suppliers(request):
    if request.method == 'POST':
        # Get the list of supplier IDs to deactivate from the POST data
        supplier_ids = request.POST.getlist('supplier_ids[]')

        # Validate and sanitize the supplier_ids here if needed

        # Loop through the selected suppliers and soft delete each one
        for supplier_id in supplier_ids:
            try:
                supplier = Supplier.objects.get(pk=supplier_id)
                supplier.soft_delete()
            except supplier.DoesNotExist:
                pass  # Handle cases where the supplier doesn't exist

        # Redirect to the 'list_suppliers' view after successful deactivation
        return redirect('list_suppliers')


def check_supplieremail(request):
    email = request.GET.get('email')
    exists = Supplier.objects.filter(supplier_email=email).exists()
    return JsonResponse({'exists': exists})

def check_suppliercontact(request):
    username = request.GET.get('username')
    exists = Supplier.objects.filter(contact_number=username).exists()
    return JsonResponse({'exists': exists})


def add_orders(request):
    if request.method == 'POST':
        product_id = request.POST['product']
        supplier_id = request.POST.get('supplier')
        product = Product.objects.get(pk=product_id)
        supplier = Supplier.objects.get(pk=supplier_id)
        order_status = request.POST['orderstatus']
        warehouse = request.POST.get('warehouse')
        quantity = request.POST.get('quantity')
        

        order = Orders(
            product=product,
            supplier=supplier,
            order_datetime=timezone.now(),  # Set the current date and time
            order_status=order_status,
            warehouse=warehouse,
            quantity=quantity,
            is_active=True  # Assuming new orders are active by default
        )
        order.save()

        # Redirect to a success page or wherever you want
        return redirect('list_orders')  # Change 'success_page' to the actual URL
    
    
def list_orders(request):
    active_orders = Orders.objects.filter(is_active=True).order_by('order_id')
    orders_per_page = 12
    paginator = Paginator(active_orders, orders_per_page)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    products = Product.objects.all()
    suppliers=Supplier.objects.all()
    return render(request, 'orders.html', {'page': page, 'products': products, 'suppliers':suppliers})


@csrf_exempt
def cancel_order(request, order_id):
    try:
        order = Orders.objects.get(pk=order_id)
        order.order_status = 'cancelled'  # Set the order_status to "cancelled"
        order.save()  # Save the changes to the order
        order.soft_delete()

        return JsonResponse({'message': 'Order has been cancelled successfully'})
    except Orders.DoesNotExist:
        return JsonResponse({'error': 'Order not found'}, status=404)
    
@csrf_exempt
def deliver_order(request, order_id):
    try:
        order = Orders.objects.get(pk=order_id)
        order.order_status = 'Delivered'  # Set the order_status to "cancelled"
        order.save()  # Save the changes to the order

        return JsonResponse({'message': 'Order has been delivered successfully'})
    except Orders.DoesNotExist:
        return JsonResponse({'error': 'Order not found'}, status=404)
    
def update_order(request, order_id):
    if request.method == 'POST':
        # Get the product instance based on the product ID
        order = get_object_or_404(Orders, order_id=order_id)

        # Process the form data
        order.product_id = request.POST['productupdate']
        order.supplier_id = request.POST['supplierupdate']
        order.warehouse = request.POST['warehouseupdate']
        order.quantity= request.POST['quantityupdate']

        # Save the updated order
        order.save()

        # Return a JSON response indicating success
        return redirect('list_orders')

    # Handle GET requests or other HTTP methods
    return JsonResponse({'message': 'Invalid request method'}, status=400)


def get_order_details(request, order_id):
    # Retrieve the order based on the order_id or return a 404 if not found
    order = get_object_or_404(Orders, order_id=order_id)  # Use the correct field name for the primary key
    # Convert the order data into a dictionary
    order_data = {    
        'product_id': order.product_id,
        'supplier_id': order.supplier_id,
        'warehouse': order.warehouse,
        'quantity': order.quantity,
    }

    # Return the order data as JSON response
    return JsonResponse(order_data)


def cancel_multiple_orders(request):
    if request.method == 'POST':
        # Get the list of order IDs to deactivate from the POST data
        order_ids = request.POST.getlist('order_ids[]')

        # Validate and sanitize the order_ids here if needed

        # Loop through the selected orders and soft delete each one
        for order_id in order_ids:
            try:
                order = Orders.objects.get(pk=order_id)
                order.order_status = 'cancelled'  # Set the order_status to "cancelled"
                order.save()
            except order.DoesNotExist:
                pass  # Handle cases where the order doesn't exist

        # Redirect to the 'list_orders' view after successful deactivation
        return redirect('list_orders')
    
    
@csrf_exempt
def return_order(request, order_id):
    try:
        order = Orders.objects.get(pk=order_id)
        order.order_status = 'Return Initiated'  # Set the order_status to "cancelled"
        order.save()  # Save the changes to the order

        return JsonResponse({'message': 'Return has been initiated successfully'})
    except Orders.DoesNotExist:
        return JsonResponse({'error': 'Order not found'}, status=404)
    
    
@csrf_exempt
def returned_order(request, order_id):
    try:
        order = Orders.objects.get(pk=order_id)
        order.order_status = 'Return Completed'  # Set the order_status to "cancelled"
        order.save()  # Save the changes to the order

        return JsonResponse({'message': 'Return has been completed successfully'})
    except Orders.DoesNotExist:
        return JsonResponse({'error': 'Order not found'}, status=404)

def isactiveinv(request):
    value='chat'
    return render(request, 'base.html', {'value': value})


class ProfilePictureForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['profile_picture']

def profile_view(request):
    user = request.user

    # Try to get the UserProfile or create it if it doesn't exist
    user_profile = get_object_or_404(UserProfile, user=user)

    if request.method == 'POST':
        # Handle profile picture update separately using the form
        profile_picture_form = ProfilePictureForm(request.POST, request.FILES, instance=user_profile)
        if profile_picture_form.is_valid():
            profile_picture_form.save()

        # Extract first name and last name from the full name
        full_name = request.POST.get('nameupdate', '')
        if 'nameupdate' in request.POST:
            first_name, last_name = full_name.split(' ', 1)
            user.first_name = first_name
            user.last_name = last_name
            user.save()

        # Update user profile fields
        if request.POST.get('dobupdate'):
            user_profile.date_of_birth = request.POST.get('dobupdate')
        if request.POST.get('countryupdate'):
            user_profile.country = request.POST.get('countryupdate')
        if request.POST.get('stateupdate'):
            user_profile.state = request.POST.get('stateupdate')
        if request.POST.get('cityupdate'):
            user_profile.city = request.POST.get('cityupdate')
        if request.POST.get('distupdate'):
            user_profile.district = request.POST.get('distupdate')
        if request.POST.get('numupdate'):
            user_profile.phone_no = request.POST.get('numupdate')
        if request.POST.get('adrupdate'):
            user_profile.addressline1 = request.POST.get('adrupdate')
        if request.POST.get('adrlupdate'):
            user_profile.addressline2 = request.POST.get('adrlupdate')
        if request.POST.get('pinupdate'):
            user_profile.pin_code = request.POST.get('pinupdate')

        with transaction.atomic():
            user.save()
            user_profile.save()
        return redirect('profile_view')

    user_profile.date_of_birth = user_profile.date_of_birth.strftime('%Y-%m-%d') if user_profile.date_of_birth else ''
    context = {
        'user': user,
        'user_profile': user_profile,
        'profile_picture_form': ProfilePictureForm(instance=user_profile),  # Pass the form to the template
    }
    return render(request, 'account.html', context)



def list_storage(request):
    active_orders = Orders.objects.filter(is_active=True).order_by('order_id')
    orders_per_page = 12
    paginator = Paginator(active_orders, orders_per_page)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    storagelocations=StorageLocation.objects.all()
    return render(request, 'help.html', {'page': page, 'storagelocations': storagelocations})


def add_storage(request):
    if request.method == 'POST':
        # Get data from the POST request
        location_name = request.POST['location_name']
        row_capacity = int(request.POST['row_capacity'])  # Convert to integer
        column_capacity = int(request.POST['column_capacity'])  # Convert to integer
        description = request.POST.get('description', '')  # Optional field

        # Calculate the shelf capacity
        shelf_capacity = row_capacity * column_capacity

        # Create a new storage location object and save it to the database
        storage_location = StorageLocation(
            location_name=location_name,
            row_capacity=row_capacity,
            column_capacity=column_capacity,
            shelf_capacity=shelf_capacity,  # Assign the calculated shelf capacity
            description=description
        )
        storage_location.save()

        return redirect('list_storage')  # Redirect to a page showing all storage locations
    else:
        return render(request, 'help.html')
    
def allocate_storages(request, order_id):
    if request.method == 'POST':
        storage_location_id = request.POST.get('storagelocation')
        shelf_number = request.POST.get('shelfnumber')
        row_number = request.POST.get('rownumber')
        column_number = request.POST.get('columnnumber')

        # Retrieve the corresponding Order instance
        order = get_object_or_404(Orders, order_id=order_id)

        # Set the is_stored field of the Order to True
        order.is_stored = True
        order.save()

        # Create a new ProductLocation instance with the form data
        ProductLocation.objects.create(
            order=order,  # Associate the ProductLocation with the Order
            storage_location_id=storage_location_id,
            shelf_number=shelf_number,
            row_number=row_number,
            column_number=column_number
        )

        # Redirect to a success page or another view
        return redirect('list_storage')  # Replace 'success_page' with your desired URL

    return HttpResponse("This view only accepts POST requests.")