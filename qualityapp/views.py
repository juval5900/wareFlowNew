from calendar import monthrange
import json
from decimal import Decimal
from datetime import date, datetime, timedelta
from django.forms import DecimalField
from django.http import HttpResponseNotFound, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.core.paginator import Paginator
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, F, Count
from django.db.models.functions import TruncMonth, ExtractMonth
from django.template.loader import render_to_string
from django.utils.html import escape
from django.db import transaction
from USERAPP.models import Orders, Product, StorageLocation, Supplier, UserProfile
from USERAPP.views import ProfilePictureForm
from controllerapp.models import Sales, Stock
from django.db.models.functions import Now
from django.db.models.functions import ExtractMonth
from django.db.models import Sum, Count, Case, When, IntegerField
from datetime import datetime
from django.db import models
from django.db.models import Sum, Count, Case, When, DecimalField, F
from django.db.models.functions import TruncMonth
from django.db.models import F, ExpressionWrapper, fields
from ecohiveapp.models import Order, OrderItem
from qualityapp.models import Inspection

# Create your views here.
@login_required
def qualityindex(request):
    user = request.user  # Get the current logged-in user

    # Get the current date and time
    current_datetime = datetime.now()

    # Calculate total sales amount for the current month
    active_orders = Orders.objects.filter(
        is_active=True,
        order_status='Delivered',
        is_inspected=False
    ).count()  # Count the number of active orders

    # Find the count of passed and failed inspections
    passed_inspections_count = Inspection.objects.filter(quality_check_status='passed').count()
    failed_inspections_count = Inspection.objects.filter(quality_check_status='failed').count()

    context = {
        'active_orders': active_orders,  # Pass the count of active orders to the template
        'passed_inspections_count': passed_inspections_count,  # Pass the count of passed inspections
        'failed_inspections_count': failed_inspections_count,  # Pass the count of failed inspections
    }
    
    return render(request, 'qualitycontrol/qualityindex.html', context)



@login_required
def quality_profile(request):
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
    return render(request, 'qualitycontrol/qualityaccount.html', context)

@login_required
def order_list(request):
    active_orders = Orders.objects.filter(
        is_active=True,
        order_status='Delivered',
        is_inspected=False
    ).order_by('order_id')

    orders_per_page = 12
    paginator = Paginator(active_orders, orders_per_page)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    products = Product.objects.filter(is_active=True)
    suppliers = Supplier.objects.filter(is_active=True)

    return render(request, 'qualitycontrol/pendingorders.html', {'page': page, 'products': products, 'suppliers': suppliers})


from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages

def save_inspection(request, order_id):
    if request.method == 'POST':
        try:
            order = get_object_or_404(Orders, order_id=order_id)
        except Orders.DoesNotExist:
            return HttpResponseNotFound("Order not found")

        packing_quality = int(request.POST.get('packing_quality', 0))
        box_tampered = request.POST.get('box_tampered') == 'yes'
        product_packing_safe = request.POST.get('product_packing_safe') == 'yes'
        seal_tampered = request.POST.get('seal_tampered') == 'yes'
        shipping_quality = int(request.POST.get('shipping_quality', 0))
        print(shipping_quality)
        # Create an instance of Inspection and save it
        inspection = Inspection.objects.create(
            order=order,
            packing_quality=packing_quality,
            box_tampered=box_tampered,
            product_packing_safe=product_packing_safe,
            seal_tampered=seal_tampered,
            shipping_quality=shipping_quality
        )

        print(packing_quality)
        print(product_packing_safe)
        print(box_tampered)
        print(seal_tampered)
        print(shipping_quality)
        # Check quality criteria and set quality_check_status accordingly
        if packing_quality < 3 or not product_packing_safe or box_tampered or seal_tampered or shipping_quality < 3:
            print("uc")
            order.quality_check_status = 'Rejected'
            inspection.quality_check_status = 'Failed'
            order.order_status='Return Completed'
            order.save()
            inspection.save()
            try:
                stock = Stock.objects.get(order=order)
                stock.is_active = False
            
                stock.save()
            except Stock.DoesNotExist:
                pass  # Stock entry not found, nothing to delete
        else:
            inspection.quality_check_status = 'Passed'
            order.quality_check_status = 'Passed'

        # Set is_inspected field of the order to True
        order.is_inspected = True
        order.save()

        # Optionally, you can add a success message
        messages.success(request, 'Inspection details saved successfully.')

        return redirect('order_list')
    
    
def get_inspection_data(request):
    selected_month = request.GET.get('selected_month')

    # Parse selected month and year
    year, month = map(int, selected_month.split('-'))

    # Get the first and last day of the selected month
    _, last_day = monthrange(year, month)

    # Define start and end datetime for the selected month
    start_datetime = datetime(year, month, 1)
    end_datetime = datetime(year, month, last_day, 23, 59, 59)

    # Query inspections made during the selected month
    inspections = Inspection.objects.filter(
        created_at__gte=start_datetime,
        created_at__lte=end_datetime
    )

    # Get counts of inspections with different quality check statuses
    inspection_counts = inspections.values('quality_check_status').annotate(count=Count('quality_check_status'))

    # Create a dictionary to hold the counts
    counts = {
        'failed': 0,
        'passed': 0,
        'not_inspected': 0
    }

    # Update counts dictionary with actual counts from the queryset
    for inspection_count in inspection_counts:
        counts[inspection_count['quality_check_status']] = inspection_count['count']

    # Return counts as JSON response
    return JsonResponse(counts) 


@login_required
def inspection_list(request):
    inspections = Inspection.objects.order_by('-id')

    orders_per_page = 12
    paginator = Paginator(inspections, orders_per_page)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)

    return render(request, 'qualitycontrol/inspections_done.html', {'page': page})

def print_inspection_report(request, order_id):
    # Fetch the inspection report for the given order ID
    inspection = get_object_or_404(Inspection, id=order_id)
    
    # Prepare the data to pass to the template
    report_data = {
        'inspection': inspection,
        # Add more data if needed
    }
    print(report_data)
    
    # Return the template with the data
    return render(request, 'qualitycontrol/inspectreport.html', report_data)    