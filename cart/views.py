from django.shortcuts import render, redirect, get_object_or_404

from .models import Cart, CartItem
from Home.models import Product
from admin_panel.models import seller_Product

# Create your views here.

def _get_cart(request):
    cart_id = request.session.session_key

    if not cart_id:
        request.session.create()
        cart_id = request.session.session_key

    if not cart_id:
        import uuid
        cart_id = str(uuid.uuid4())

    cart, created = Cart.objects.get_or_create(cart_id=cart_id)
    return cart


def add_to_cart(request, product_id, product_type):
    cart = _get_cart(request)

    if product_type == "store":
        product = get_object_or_404(Product, id=product_id)

        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            store_product=product,
            seller_product=None
        )

    elif product_type == "seller":
        product = get_object_or_404(seller_Product, id=product_id)

        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            seller_product=product,
            store_product=None
        )

    else:
        return redirect('cart')

    if not created:
        cart_item.quantity += 1

    cart_item.save()
    return redirect('cart')

def cart_view(request):
    cart = _get_cart(request)
    items = cart.items.all()
    total = sum(item.total_price() for item in items)
    tax = (5 * total)/100
    grand_total = total + tax
    return render(request, 'cart/cart.html', {
        'cart': cart,
        'items': items,
        'total': total,
        'tax': tax,
        'grand_total': grand_total
    })

def increase_quantity(request, item_id):
    item = get_object_or_404(CartItem, id=item_id)

    item.quantity += 1
    item.save()

    return redirect('cart')

def decrease_quantity(request, item_id):
    item = get_object_or_404(CartItem, id=item_id)

    if item.quantity > 1:
        item.quantity -= 1
        item.save()
    else:
        item.delete()

    return redirect('cart')

def remove_item(request, item_id):
    item = get_object_or_404(CartItem, id=item_id)
    item.delete()
    return redirect('cart')


