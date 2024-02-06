# cart_context.py

from ecohiveapp.models import Cart  # Import your Cart model
# from django.contrib.auth.decorators import login_required
from django.shortcuts import render



# @login_required
def cart(request):
    if request.user.is_authenticated:
        cart_items = Cart.objects.filter(user=request.user)
        cart_item_count = cart_items.count()
    else:
        # If the user is not logged in, set cart_item_count to 0
        cart_item_count = 0

    return {'cart_item_count': cart_item_count}
