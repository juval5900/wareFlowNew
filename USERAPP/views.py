# Standard Library Imports
from datetime import date, timedelta
from io import BytesIO

# Django Imports
from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login, logout, get_user_model
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.core.paginator import Paginator
from django.core.serializers.json import DjangoJSONEncoder
from django.db import transaction
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render, redirect
from django.utils import timezone
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.urls import reverse
from django import forms
from django.conf import settings

# Third-Party Library Imports
import pyotp
import tablib
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph

from controllerapp.models import Stock

# Project-Specific Imports
from .forms import UserProfileForm
from .models import Category, Product, ProductLocation, StorageLocation, Subcategory, Supplier, Orders, UserProfile, UserRole
from .models import Product  # Duplicate import, remove it





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


            try:
                user_role = UserRole.objects.get(user=user)
                user_role_name = user_role.role
            except UserRole.DoesNotExist:
                user_role_name = None
                
            # Set the profile picture URL in the session
            request.session['profile_picture_url'] = user_profile.profile_picture.url

            # Redirect users based on their roles
            if user_role_name == 'admin':
                return redirect('adminindex')  # Replace with the admin app index URL
            elif user_role_name == 'warehouse manager':
                return redirect('index')  # Replace with the user app index URL
            elif user_role_name == 'inventory controller':
                return redirect('controllerindex')  # Replace with the user app index URL       
            else:
                messages.error(request, "Invalid role")  # Handle invalid roles
                return redirect('login')
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

def settingshtml(request):
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
        product.product_name = request.POST.get('productName')
        product.category_id = request.POST.get('category')
        product.subcategory_id = request.POST.get('subcategory')
        #product.buying_price = request.POST.get('buyingPriceupdate')
        product.quantity = request.POST.get('quantity')
        #product.unit = request.POST.get('unitupdate')
        #product.expiry_date = request.POST.get('expiryDateupdate')
        product.threshold_value = request.POST.get('thresholdValue')
        
        
        # Check if a new product image is provided
        if request.FILES.get('productImage'):
            product.product_image = request.FILES['productImage']

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
        supplier.supplier_name = request.POST['supplierName']
        supplier.supplier_address = request.POST['supplierAddress']
        supplier.contact_number = request.POST['contactNumber']
        supplier.supplier_email= request.POST['supplieremail']
        supplier.supplier_type = request.POST['supplierType']
        supplier.supplier_image = request.FILES['supplierImage']
        # Check if a new supplier image is provided
        if request.FILES.get('supplierImage'):
            supplier.supplier_image = request.FILES['supplierImage']

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


from django.shortcuts import render, redirect
from django.utils import timezone
from .models import Orders, Product, Supplier

def add_orders(request):
    if request.method == 'POST':
        product_id = request.POST['product']
        supplier_id = request.POST.get('supplier')
        buying_price_str = request.POST.get('buying_price')
        # Convert buying_price to a float (or integer, if it's always a whole number)
        buying_price = float(buying_price_str) if buying_price_str else 0.0  # Default to 0.0 if empty
        product = Product.objects.get(pk=product_id)
        supplier = Supplier.objects.get(pk=supplier_id)
        order_status = request.POST['orderstatus']
        warehouse = request.POST.get('warehouse')
        quantity_str = request.POST.get('quantity')
        # Convert quantity to an integer
        quantity = int(quantity_str) if quantity_str else 0  # Default to 0 if empty

        order = Orders(
            product=product,
            supplier=supplier,
            buying_price=buying_price,
            order_datetime=timezone.now(),
            order_status=order_status,
            warehouse=warehouse,
            quantity=quantity,
            is_active=True
        )
        # Calculate the total price
        order.total_price = buying_price * quantity
        order.save()

        # Redirect to a success page or wherever you want
        return redirect('list_orders')
    
    
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
        #order.soft_delete()

        return JsonResponse({'message': 'Order has been cancelled successfully'})
    except Orders.DoesNotExist:
        return JsonResponse({'error': 'Order not found'}, status=404)
    

def deliver_order(request, order_id):
    try:
        order = Orders.objects.get(pk=order_id)
        order.order_status = 'Delivered'  # Set the order_status to "Delivered"
        order.delivered_at = timezone.now()  # Update the delivered_at field with the current time
        order.save()  # Save the changes to the order

        # Create an entry in the Stock table with the remaining_quantity set to the order's quantity
        Stock.objects.create(
            order=order,
            is_stored=False,
            remaining_quantity=order.quantity
        )

        return JsonResponse({'message': 'Order has been delivered successfully'})
    except Orders.DoesNotExist:
        return JsonResponse({'error': 'Order not found'}, status=404)
    
def update_order(request, order_id):
    if request.method == 'POST':
        # Get the product instance based on the product ID
        order = get_object_or_404(Orders, order_id=order_id)

        # Process the form data
        order.product_id = request.POST['product']
        order.supplier_id = request.POST['supplier']
        order.warehouse = request.POST['warehouse']
        order.quantity= request.POST['quantity']

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
    
    
def return_order(request, order_id):
    try:
        order = Orders.objects.get(pk=order_id)
        order.order_status = 'Return Initiated'  # Set the order_status to "Return Initiated"
        order.save()  # Save the changes to the order

        # Get the corresponding stock entry and perform a soft delete
        try:
            stock = Stock.objects.get(order=order)
            stock.is_active = False
            
            stock.save()
        except Stock.DoesNotExist:
            pass  # Stock entry not found, nothing to delete

        return JsonResponse({'message': 'Return has been initiated successfully'})
    except Orders.DoesNotExist:
        return JsonResponse({'error': 'Order not found'}, status=404)
    
    
def returned_order(request, order_id):
    try:
        order = Orders.objects.get(pk=order_id)
        order.order_status = 'Return Completed'  # Set the order_status to "Return Completed"
        order.save()  # Save the changes to the order

        # Get the corresponding stock entry and delete it
        try:
            stock = Stock.objects.get(order=order)
            stock.delete()  # Delete the stock entry
        except Stock.DoesNotExist:
            pass  # Stock entry not found, nothing to delete

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

        if ' ' in full_name:
            # Split the full name into first name and last name
            first_name, last_name = full_name.split(' ', 1)
            user.first_name = first_name
            user.last_name = last_name
        else:
            # If there is no space, consider the whole name as the first name
            user.first_name = full_name
            user.last_name = ''

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
    sixteen_years_ago = date.today() - timedelta(days=16*365)
    sixtyfive_years_ago = date.today() - timedelta(days=65*365)
    context = {
        'user': user,
        'user_profile': user_profile,
        'sixteen_years_ago': sixteen_years_ago.strftime('%Y-%m-%d'),  # Format the date as YYYY-MM-DD
        'sixtyfive_years_ago': sixtyfive_years_ago.strftime('%Y-%m-%d'),
        'profile_picture_form': ProfilePictureForm(instance=user_profile),  # Pass the form to the template
    }
    return render(request, 'account.html', context)



def list_storage(request):
    delivered_orders = Orders.objects.filter(order_status="Delivered", is_stored=False).order_by('order_id')
    orders_per_page = 12
    paginator = Paginator(delivered_orders, orders_per_page)
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


class ExportPDF(View):
    def get(self, request):
        # Get the data you want to export
        products = Product.objects.all()

        # Create a PDF buffer using BytesIO
        buffer = BytesIO()

        # Create the PDF object, using the buffer as its "file."
        doc = SimpleDocTemplate(buffer, pagesize=letter)

        # Create a list to store the data for the table
        data = []

        # Define the table's column headers
        table_headers = ['Product Name', 'Category', 'Subcategory', 'Quantity', 'Threshold Value']

        data.append(table_headers)

        # Populate the table data with product information
        for product in products:
            data.append([product.product_name, product.category.category_name, product.subcategory.subcategory_name,
                         product.quantity, product.threshold_value])

        # Create the table
        table = Table(data)

        # Add style to the table
        style = TableStyle([('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                            ('GRID', (0, 0), (-1, -1), 1, colors.black)])

        table.setStyle(style)

        # Build the PDF
        pdf = []

        # Add a title to the PDF
        styles = getSampleStyleSheet()
        title = Paragraph("Product List", styles['Title'])
        pdf.append(title)

        # Add the table to the PDF
        pdf.append(table)

        # Build the PDF
        doc.build(pdf)

        # Set the buffer's position to the beginning
        buffer.seek(0)

        # Create an HTTP response with the PDF file
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="product_list.pdf"'
        response.write(buffer.read())

        # Close the buffer
        buffer.close()

        return response


class ExportSupplierPDF(View):
    def get(self, request):
        # Get the data you want to export (in this case, Suppliers)
        suppliers = Supplier.objects.all()

        # Create a PDF buffer using BytesIO
        buffer = BytesIO()

        # Create the PDF object, using the buffer as its "file."
        doc = SimpleDocTemplate(buffer, pagesize=letter)

        # Create a list to store the data for the table
        data = []

        # Define the table's column headers
        table_headers = ['Supplier Name', 'Address', 'Contact Number', 'Email', 'Type']

        data.append(table_headers)

        # Populate the table data with supplier information
        for supplier in suppliers:
            data.append([supplier.supplier_name, supplier.supplier_address, supplier.contact_number,
                         supplier.supplier_email, supplier.supplier_type])

        # Create the table
        table = Table(data)

        # Add style to the table
        style = TableStyle([('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                            ('GRID', (0, 0), (-1, -1), 1, colors.black)])

        table.setStyle(style)

        # Build the PDF
        pdf = []

        # Add a title to the PDF
        styles = getSampleStyleSheet()
        title = Paragraph("Supplier List", styles['Title'])
        pdf.append(title)

        # Add the table to the PDF
        pdf.append(table)

        # Build the PDF
        doc.build(pdf)

        # Set the buffer's position to the beginning
        buffer.seek(0)

        # Create an HTTP response with the PDF file
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="supplier_list.pdf"'
        response.write(buffer.read())

        # Close the buffer
        buffer.close()

        return response
    
    
class ExportOrdersPDF(View):
    def get(self, request):
        # Get the data you want to export (in this case, Orders)
        orders = Orders.objects.all()

        # Create a PDF buffer using BytesIO
        buffer = BytesIO()

        # Create the PDF object, using the buffer as its "file."
        doc = SimpleDocTemplate(buffer, pagesize=letter)

        # Create a list to store the data for the table
        data = []

        # Define the table's column headers
        table_headers = ['Order ID', 'Product', 'Supplier', 'Order Date & Time', 'Order Status', 'Warehouse', 'Quantity', 'Is Active', 'Cancelled At', 'Is Stored']

        data.append(table_headers)

        # Populate the table data with order information
        for order in orders:
            data.append([order.order_id, order.product.product_name, order.supplier.supplier_name,
                         order.order_datetime, order.order_status, order.warehouse,
                         order.quantity, order.is_active, order.cancelled_at, order.is_stored])

        # Create the table
        table = Table(data)

        # Add style to the table
        style = TableStyle([('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                            ('GRID', (0, 0), (-1, -1), 1, colors.black)])

        table.setStyle(style)

        # Build the PDF
        pdf = []

        # Add a title to the PDF
        styles = getSampleStyleSheet()
        title = Paragraph("Orders List", styles['Title'])
        pdf.append(title)

        # Add the table to the PDF
        pdf.append(table)

        # Build the PDF
        doc.build(pdf)

        # Set the buffer's position to the beginning
        buffer.seek(0)

        # Create an HTTP response with the PDF file
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="orders_list.pdf"'
        response.write(buffer.read())

        # Close the buffer
        buffer.close()

        return response
    
    
def forgot(request):
    return render(request, 'forgot.html')
    
User = get_user_model()



def generate_otp(request):
    if request.method == 'POST':
        user_email = request.POST.get('username')  # Get user's email from the request (change 'user_email' to match your form field name)
        print(user_email)
        # Generate a random OTP using pyotp
        otp = pyotp.random_base32()
       

        # Store the OTP in the session or database for later verification
        # For example, you can save it in the session like this:
        request.session['generated_otp'] = otp

        # Send the OTP in an email to the user
        subject = 'Your OTP for account activation'
        message = f'Your OTP for account activation is: {otp}'
        from_email = settings.EMAIL_HOST_USER  # Your sender email address
        recipient_list = [user_email]

        send_mail(subject, message, from_email, recipient_list)

        # Return the OTP as a JSON response
        return JsonResponse({'otp': otp, 'success': True})

    # Handle GET requests or other methods appropriately
    return JsonResponse({'error': 'Invalid request method'}, status=400)



def reset_password(request):
    if request.method == 'POST':
        user_email = request.POST.get('user_email')  # Get user's email from the request
        new_password = request.POST.get('new_password')  # Get the new password from the request

        try:
            user = User.objects.get(email=user_email)
        except User.DoesNotExist:
            return JsonResponse({'error': 'User not found'}, status=404)

        # Set the new password for the user
        user.set_password(new_password)
        user.save()

        # Optionally, you can clear the session or database where you stored the OTP
        if 'generated_otp' in request.session:
            del request.session['generated_otp']

        # Redirect to the login page upon successful password reset
        return HttpResponseRedirect(reverse('login'))  # Replace 'login' with your login URL name

    # Handle GET requests or other methods appropriately
    return JsonResponse({'error': 'Invalid request method'}, status=400)