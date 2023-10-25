import json
from decimal import Decimal
from datetime import datetime
from django.forms import DecimalField
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.core.paginator import Paginator
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, F, Count
from django.db.models.functions import TruncMonth, ExtractMonth
from django.template.loader import render_to_string
from django.utils.html import escape

from USERAPP.models import Orders, Product, StorageLocation, Supplier
from controllerapp.models import Sales, Stock
from django.db.models.functions import Now
from django.db.models.functions import ExtractMonth
from django.db.models import Sum, Count, Case, When, IntegerField
from datetime import datetime
from django.db import models
from django.db.models import Sum, Count, Case, When, DecimalField, F
from django.db.models.functions import TruncMonth
from .models import Sales, Orders  # Import your Sales and Orders models
from django.db.models import F, ExpressionWrapper, fields


@login_required
def controllerindex(request):
    user = request.user  # Get the current logged-in user

    # Get the current date and time
    current_datetime = datetime.now()

    # Calculate total sales amount for the current month
    monthly_sales = (
        Sales.objects
        .filter(date_field__year=current_datetime.year, date_field__month=current_datetime.month)
        .annotate(month=TruncMonth('date_field'))
        .values('month')
        .annotate(
            total_sales=Sum('total_sales_price'),
            total_profit=Sum('profit'),
            total_buying=Sum('total_buying_price'),
            total_sales_count=Count('id')
        )
    )

    unique_monthly_sales = (
            Sales.objects
            .annotate(month=TruncMonth('date_field'))
            .values('month')
            .annotate(
                total_sales=Sum('total_sales_price'),
                total_profit=Sum('profit'),
                total_buying=Sum('total_buying_price'),
                total_sales_count=Count('id')
            )
            .order_by('-month')
        )
    
    # Calculate the monthly data for the current year
   

# ...

    monthly_data = (
        Orders.objects
        .filter(order_datetime__year=current_datetime.year, order_datetime__month=current_datetime.month)
        .annotate(month=ExtractMonth('order_datetime'))
        .values('month')
        .annotate(
            total_delivered_orders=Sum(
                Case(
                    When(order_status='Delivered', then=1),
                    default=0,
                    output_field=IntegerField()
                )
            ),
            total_cancelled_orders=Sum(
                Case(
                    When(order_status='cancelled', then=1),
                    default=0,
                    output_field=IntegerField()
                )
            ),
            total_returned_orders=Sum(
                Case(
                    When(order_status='Return Completed', then=1),
                    default=0,
                    output_field=IntegerField()
                )
            ),
            total_purchase_price=Sum(
                Case(
                    When(order_status='Delivered', then=F('total_price')),
                    default=0,
                    output_field=DecimalField(max_digits=10, decimal_places=2, default=0.00)
                )
            )
        )
    )

    # Get a list of unique months in "YYYY-MM" format for the current year
    unique_months = [entry['month'].strftime('%Y-%m') for entry in unique_monthly_sales]

    # Get the current month and year in "YYYY-MM" format
    current_month = current_datetime.strftime('%Y-%m')

    top_selling_products = (
        Sales.objects
        .filter(date_field__year=current_datetime.year, date_field__month=current_datetime.month)
        .values('product__product_name')  # Group by product name
        .annotate(
            total_sales=Sum('quantity'),  # Calculate total quantity sold
            total_sales_price=Sum('total_sales_price'),  # Calculate total sales price
            remaining_quantity=Sum('stock__remaining_quantity')  # Calculate remaining quantity
        )
        .order_by('-total_sales')[:5]  # Get the top 5 products by total quantity sold
    )
    
    threshold_values = Product.objects.values('product_name', 'threshold_value')

    # Calculate the total remaining quantity for each product in the Stock model
    products_below_threshold = []

    for product in threshold_values:
        product_name = product['product_name']
        threshold_value = product['threshold_value']
        total_remaining_stock = Stock.objects.filter(order__product__product_name=product_name).aggregate(
            total_remaining_stock=models.Sum('remaining_quantity'))['total_remaining_stock'] or 0

        # Compare total remaining stock with the threshold value
        if total_remaining_stock <= threshold_value:
            products_below_threshold.append({
                'product_name': product_name,
                'threshold_value': threshold_value,
                'total_remaining_stock': total_remaining_stock,
            })


    context = {
        'user': user,
        'monthly_sales': monthly_sales,
        'current_month': current_month,
        'unique_months': unique_months,
        'monthly_data': monthly_data,
        'top_selling_products': top_selling_products,  # Include top-selling products in the context
        'products_below_threshold': products_below_threshold,
    }

    return render(request, 'Controller/controllerindex.html', context)

@login_required
def list_orders2(request):
    active_orders = Orders.objects.filter(is_active=True).order_by('order_id')
    orders_per_page = 12
    paginator = Paginator(active_orders, orders_per_page)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    products = Product.objects.filter(is_active=True)
    suppliers= Supplier.objects.filter(is_active=True)

    return render(request, 'Controller/orders2.html', {'page': page, 'products': products, 'suppliers':suppliers})


@login_required
def stock_list(request):
    stocks = Stock.objects.filter(is_active=True)  # Filter stocks where is_stored is True (active)
    storage_locations = StorageLocation.objects.all()  # Retrieve all storage locations
    context = {
        'stocks': stocks,
        'storage_locations': storage_locations,  # Include storage locations in the context
    }
    return render(request, 'Controller/stock.html', context)


@login_required
def update_stock(request, stock_id):
    if request.method == 'POST':
        try:
            # Retrieve the stock object based on the stock_id
            stock = Stock.objects.get(id=stock_id)
            
            # Update the stock details based on the form data
            stock.sector = request.POST.get('sector')
            stock.row_start = request.POST.get('rowStart')
            stock.column_start = request.POST.get('columnStart')
            stock.column_end = request.POST.get('columnEnd')
            
            stock.is_stored = True
            # Save the updated stock object
            stock.save()
            
            # You can return a success response as JSON if needed
            return JsonResponse({'message': 'Stock details updated successfully'})
        
        except Stock.DoesNotExist:
            # Handle the case where the stock with the provided ID does not exist
            return JsonResponse({'error': 'Stock not found'}, status=404)
    
    # Handle other HTTP methods or form submission errors
    return JsonResponse({'error': 'Invalid request'}, status=400)

@login_required
def get_stock_details(request, stock_id):
    try:
        stock = Stock.objects.get(pk=stock_id)
        # Create a dictionary containing the stock details you want to return
        stock_data = {
            'sector': stock.sector,
            'row_start': stock.row_start,
            'column_start': stock.column_start,
            'column_end': stock.column_end,
            # Add other fields as needed
        }
        return JsonResponse(stock_data)
    except Stock.DoesNotExist:
        return JsonResponse({'error': 'Stock not found'}, status=404)
    
    

@login_required
def get_stock_for_product(request, product_id):
    try:
        # Retrieve the stock data for the selected product with remaining quantity greater than 0
        stocks = Stock.objects.filter(order__product_id=product_id, remaining_quantity__gt=0).values(
            'id',
            'order__product__product_name',
            'order__delivered_at',
            'remaining_quantity'  # Use 'remaining_quantity' instead of 'quantity'
        )

        # Create a list to store the stock data as dictionaries
        stock_list = []

        # Iterate through the queryset and create dictionaries with the desired data
        for stock in stocks:
            # Convert remaining_quantity to float for subtraction
            remaining_quantity = float(stock['remaining_quantity'])
            
            stock_data = {
                'id': stock['id'],
                'stock_name': f"{stock['order__product__product_name']} - Delivered At: {stock['order__delivered_at']} - Remaining Quantity: {remaining_quantity}",
                'remaining_quantity': remaining_quantity
            }
            stock_list.append(stock_data)

        # Return the stock data as JSON with the key 'stocks'
        return JsonResponse({'stocks': stock_list})
    except Exception as e:
        # Handle any exceptions and return an error response if needed
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def sales(request):
    # Retrieve all Sales objects from the database
    sales = Sales.objects.all()

    # Retrieve other data for the template
    stocks = Stock.objects.filter(is_active=True)
    orders = Orders.objects.filter(is_active=True)
    products = Product.objects.all()
    active_products=Product.objects.filter(is_active=True)

    context = {
        'sales': sales,  # Pass the sales data to the template
        'stocks': stocks,  # Pass the stock data to the template
        'orders': orders,  # Pass the orders data to the template
        'products': products,  # Pass the product data to the template
        'active_products':active_products,
    }

    return render(request, 'Controller/sales.html', context)


@login_required
def add_sales(request):
    if request.method == 'POST':
        # Get data from the form
        product_id = request.POST.get('product')
        stock_id = request.POST.get('stock')
        quantity = Decimal(request.POST.get('quantity'))  # Convert to Decimal
        delivery_address = request.POST.get('delivery_address')
        sales_price = Decimal(request.POST.get('sales_price'))  # Convert to Decimal
        buyer_name = request.POST.get('buyer_name')
        buyer_contact_info = request.POST.get('buyer_contact_info')

        try:
            # Set the status as "Order Placed"
            status = "Order Placed"

            # Create a Sales object
            sales = Sales.objects.create(
                product_id=product_id,
                stock_id=stock_id,
                quantity=quantity,
                delivery_address=delivery_address,
                sales_price=sales_price,
                status=status,
                buyer_name=buyer_name,
                buyer_contact_info=buyer_contact_info
            )

            # Update the Stock model's remaining_quantity
            stock = Stock.objects.get(id=stock_id)
            stock.remaining_quantity -= quantity
            stock.save()

            return redirect('sales')
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

    # Handle GET requests or other cases
    return redirect('sales')


@csrf_exempt
@login_required
def delete_multiple_sales(request):
    if request.method == "POST":
        sale_ids = request.POST.getlist("sale_ids[]")

        try:
            # Perform a soft delete by marking sales as deleted and updating the status to "Cancelled"
            Sales.objects.filter(id__in=sale_ids).update(deleted=True, status="Cancelled")

            # Return a success response
            return JsonResponse({"message": "Sales marked as cancelled and deleted successfully"}, status=200)
        except Exception as e:
            # Handle any exceptions and return an error response
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Bad request"}, status=400)


@login_required
def cancel_sale(request, sale_id):
    try:
        # Get the sale to cancel
        sale = get_object_or_404(Sales, pk=sale_id)
        
        # Update the status field to "Cancelled"
        sale.status = "Cancelled"
        sale.save()

        # You can perform other actions here if needed
        
        return JsonResponse({'message': 'Sale has been cancelled successfully'})
    except Sales.DoesNotExist:
        return JsonResponse({'error': 'Sale not found'}, status=404)
    
    
    
@login_required
def deliver_sale(request, sale_id):
    if request.method == 'POST':
        # Fetch the sale object
        sale = get_object_or_404(Sales, pk=sale_id)

        # Update the status to 'Delivered'
        sale.status = 'Delivered'
        sale.save()

        return JsonResponse({'message': 'Sale marked as Delivered successfully.'})

    # Handle other HTTP methods if needed
    return JsonResponse({'error': 'Invalid request method.'}, status=400)



@login_required
def get_buying_price_for_stock(request, stock_id):
    try:
        stock = Stock.objects.get(pk=stock_id)
        buying_price = stock.order.buying_price  # Assuming you have a ForeignKey relationship named 'orders'

        # Return the buying price in JSON format
        return JsonResponse({'buying_price': buying_price})
    except Stock.DoesNotExist:
        # Handle the case where the stock with the given ID does not exist
        return JsonResponse({'error': 'Stock not found'}, status=404)
    
    
    
    
@login_required
def controllercharts(request):
    user = request.user  # Get the current logged-in user
    return render(request, 'Controller/charts.html')



@login_required
def get_profit_data(request):
    # Query your Sales model and calculate profit data by month
    profit_data = (
        Sales.objects
        .annotate(month_name=ExtractMonth('date_field'))
        .values('month_name')
        .annotate(total_profit=Sum('profit'))
        .order_by('month_name')
    )

    # Map month numbers to month names
    month_names = {
        1: 'January',
        2: 'February',
        3: 'March',
        4: 'April',
        5: 'May',
        6: 'June',
        7: 'July',
        8: 'August',
        9: 'September',
        10: 'October',
        11: 'November',
        12: 'December',
    }

    # Format profit_data as a list of dictionaries with month names
    formatted_profit_data = [
        {
            'month': month_names[item['month_name']],
            'total_profit': float(item['total_profit']) if item['total_profit'] is not None else 0.0,  # Convert Decimal to float
        }
        for item in profit_data
    ]

    # Serialize the profit data to JSON
    profit_data_json = json.dumps(formatted_profit_data)

    return JsonResponse({'profit_data': profit_data_json})



@login_required
def get_stock_and_sales_data(request):
    # Query total stocks and total sales per month
    stock_data = (
        Stock.objects
        .annotate(month=F('order__delivered_at__month'))
        .values('month')
        .annotate(total_stocks=Sum('remaining_quantity'))
        .order_by('month')
        
    )

    sales_data = (
        Sales.objects
        .annotate(month=F('date_field__month'))
        .values('month')
        .annotate(total_sales=Sum('quantity'))
        .order_by('month')
    )

    # Organize the data into a suitable format
    stock_dict = {item['month']: item['total_stocks'] for item in stock_data}
    sales_dict = {item['month']: item['total_sales'] for item in sales_data}

    months = list(stock_dict.keys())  # Assuming months match between stock and sales data
    total_stocks = [stock_dict.get(month, 0) for month in months]
    total_sales = [sales_dict.get(month, 0) for month in months]

    # Prepare data for the chart
    data = {
        'months': months,
        'total_stocks': total_stocks,
        'total_sales': total_sales,
    }

    return JsonResponse(data)




@login_required
def get_order_status_data(request):
    # Get the current month and year
    today = datetime.now()
    current_month = today.month
    current_year = today.year

    # Query the database to get counts for each order status for the current month
    data = Orders.objects.filter(
        order_datetime__month=current_month,
        order_datetime__year=current_year
    ).values('order_status').annotate(count=Count('order_status'))

    # Prepare the data for the chart
    order_data = {}
    for entry in data:
        order_status = entry['order_status']
        count = entry['count']
        order_data[order_status] = count

    # Return the order status data as JSON
    return JsonResponse(order_data)



@csrf_exempt  # Only for development, remove in production or implement proper CSRF handling
@login_required
def get_top_selling_products(request):
    # Query the top 5 selling products based on quantity
    top_selling_products = (
        Sales.objects
        .values('product__product_name')
        .annotate(total_quantity=Sum('quantity'))
        .order_by('-total_quantity')[:5]
    )

    # Prepare the data as a dictionary
    product_names = [item['product__product_name'] for item in top_selling_products]
    quantities = [item['total_quantity'] for item in top_selling_products]

    data = {
        'product_names': product_names,
        'quantities': quantities,
    }

    return JsonResponse(data)


@login_required
def get_monthly_sales_data(request):
    selected_month = request.GET.get('selected_month')

    # Query the database to fetch data for the selected month
    monthly_sales = (
        Sales.objects
        .filter(date_field__month=selected_month.split('-')[1], date_field__year=selected_month.split('-')[0])
        .annotate(month=TruncMonth('date_field'))
        .values('month')
        .annotate(
            total_sales=Sum('total_sales_price'),
            total_profit=Sum('profit'),
            total_buying=Sum('total_buying_price'),
            total_sales_count=Count('id')
        )
        .order_by('-month')
    )

    data = {
        'monthly_sales': list(monthly_sales),
    }

    return JsonResponse(data)




@login_required
def fetch_data_view(request):
    # Ensure this view is only accessible via AJAX
    if not request.headers.get('x-requested-with') == 'XMLHttpRequest' or not request.method == 'GET':
        return JsonResponse({'error': 'Invalid request'}, status=400)

    # Get the selected month from the AJAX request parameters
    selected_month = request.GET.get('month')

    # Query the database to fetch total sales for the selected month
    total_sales_for_month = (
        Sales.objects
        .filter(date_field__startswith=selected_month)
        .aggregate(total_sales=Sum('total_sales_price'))
    )['total_sales']

    # If there are no sales for the selected month, 'total_sales' will be None, so provide a default value of 0
    total_sales_for_month = total_sales_for_month or 0

    # You can also calculate other metrics (total_profit, total_buying_price, etc.) similarly if needed.

    # Render the data as HTML using a template
    html_data = render_to_string('Controller/controllerindex.html', {'total_sales_for_month': total_sales_for_month})

    # Escape the HTML to prevent any security vulnerabilities
    escaped_html_data = escape(html_data)

    return JsonResponse({'html_data': escaped_html_data})



@login_required
def get_sales_data(request):
    selected_month = request.GET.get('selected_month')

    # Query the data for the selected month
    monthly_sales = (
        Sales.objects
        .filter(date_field__year=selected_month.split('-')[0], date_field__month=selected_month.split('-')[1])
        .annotate(month=TruncMonth('date_field'))
        .values('month')
        .annotate(
            total_sales=Sum('total_sales_price'),
            total_profit=Sum('profit'),
            total_buying=Sum('total_buying_price'),
            total_sales_count=Count('id')
        )
    )

    monthly_data = (
        Orders.objects
        .filter(order_datetime__year=selected_month.split('-')[0], order_datetime__month=selected_month.split('-')[1])
        .annotate(month=TruncMonth('order_datetime'))
        .values('month')
        .annotate(
            total_delivered_orders=Sum(
                Case(
                    When(order_status='Delivered', then=1),
                    default=0,
                    output_field=IntegerField()
                )
            ),
            total_cancelled_orders=Sum(
                Case(
                    When(order_status='cancelled', then=1),
                    default=0,
                    output_field=IntegerField()
                )
            ),
            total_returned_orders=Sum(
                Case(
                    When(order_status='Return Completed', then=1),
                    default=0,
                    output_field=IntegerField()
                )
            ),
            total_purchase_price=Sum(
                Case(
                    When(order_status='Delivered', then=F('total_price')),
                    default=0,
                    output_field=DecimalField(max_digits=10, decimal_places=2, default=0.00)
                )
            )
        )
    )
    
    # Convert monthly_sales and monthly_data to lists of dictionaries
    monthly_sales_values = list(monthly_sales)
    monthly_data_values = list(monthly_data)

    # Check if monthly_sales is empty and replace with 0s
    if not monthly_sales_values:
        monthly_sales_values = [{'total_sales': 0, 'total_profit': 0, 'total_buying': 0, 'total_sales_count': 0}]
    
    # Check if monthly_data is empty and replace with 0s
    if not monthly_data_values:
        monthly_data_values = [{'total_delivered_orders': 0, 'total_cancelled_orders': 0, 'total_returned_orders': 0, 'total_purchase_price': 0.00}]

    selected_datetime = datetime.strptime(selected_month, '%Y-%m')
    
    top_selling_products = (
        Sales.objects
        .filter(date_field__year=selected_datetime.year, date_field__month=selected_datetime.month)
        .values('product__product_name')  # Group by product name
        .annotate(
            total_sales=Sum('quantity'),  # Calculate total quantity sold
            total_sales_price=Sum('total_sales_price'),  # Calculate total sales price
            remaining_quantity=Sum('stock__remaining_quantity')  # Calculate remaining quantity
        )
        .order_by('-total_sales')[:5]  # Get the top 5 products by total quantity sold
    )

    # Create a list of dictionaries from the top-selling products queryset
    top_selling_data = list(top_selling_products)

    # Return both sets of data in the JSON response
    return JsonResponse({'monthly_sales': monthly_sales_values, 'monthly_data': monthly_data_values, 'top_selling_products':top_selling_data })



@login_required
def view_invoice(request, sale_id):
    # Retrieve the sale object or data as per your application
    # Replace this with your actual logic to retrieve sale data
    sale = Sales.objects.get(id=sale_id)
    
    if sale:
        # Calculate GST (5%)
        gst = Decimal('0.05') * sale.sales_price

        # Calculate Service Charges (3%)
        service_charges = Decimal('0.03') * sale.sales_price

        # Calculate Packing Fee (10%)
        packing_fee = Decimal('0.2') * sale.sales_price

        context = {
            'sale': sale,
            'gst': gst,
            'service_charges': service_charges,
            'packing_fee': packing_fee,
        }

        return render(request, 'Controller/invoice.html', context)
    else:
        return render(request, 'Controller/invoice.html', {'sale': None})
    
    
    
@login_required
def view_order_pdf(request):
    active_orders = Orders.objects.filter(is_active=True).order_by('order_id')
    orders_per_page = 12
    paginator = Paginator(active_orders, orders_per_page)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    products = Product.objects.filter(is_active=True)
    suppliers= Supplier.objects.filter(is_active=True)

    return render(request, 'Controller/pdforder.html', {'page': page, 'products': products, 'suppliers':suppliers})