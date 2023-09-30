from django.shortcuts import render
from django.core.paginator import Paginator
from USERAPP.models import Orders, Product, Supplier

# Create your views here.
def controllerindex(request):
    user = request.user  # Get the current logged-in user
    return render(request, 'Controller/controllerindex.html')

def list_orders2(request):
    active_orders = Orders.objects.filter(is_active=True).order_by('order_id')
    orders_per_page = 12
    paginator = Paginator(active_orders, orders_per_page)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    products = Product.objects.all()
    suppliers=Supplier.objects.all()
    return render(request, 'Controller/orders2.html', {'page': page, 'products': products, 'suppliers':suppliers})


