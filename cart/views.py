from django.shortcuts import render, redirect, get_object_or_404
from .models import Cart, CartItem
from Home.models import Product
from admin_panel.models import seller_Product
from django.contrib.auth.decorators import login_required



# Create your views here.
def _get_cart(request):
    if request.user.is_authenticated:
        # Handle case where user might have multiple carts
        carts = Cart.objects.filter(user=request.user)
        if carts.exists():
            if carts.count() > 1:
                # Merge all user carts into the first one
                main_cart = carts.first()
                for cart in carts[1:]:
                    # Move items from duplicate cart to main cart
                    for item in cart.items.all():
                        existing_item = CartItem.objects.filter(
                            cart=main_cart,
                            store_product=item.store_product,
                            seller_product=item.seller_product
                        ).first()
                        
                        if existing_item:
                            existing_item.quantity += item.quantity
                            existing_item.save()
                            item.delete()
                        else:
                            item.cart = main_cart
                            item.save()
                    
                    cart.delete()
                cart = main_cart
            else:
                cart = carts.first()
        else:
            cart = Cart.objects.create(user=request.user)
    else:
        cart_id = request.session.session_key

        if not cart_id:
            cart_id = request.session.create()

        # Use filter to handle multiple carts with same cart_id
        carts = Cart.objects.filter(cart_id=cart_id)
        if carts.exists():
            if carts.count() > 1:
                # Merge duplicate session carts
                cart = carts.first()
                for duplicate_cart in carts[1:]:
                    for item in duplicate_cart.items.all():
                        existing_item = CartItem.objects.filter(
                            cart=cart,
                            store_product=item.store_product,
                            seller_product=item.seller_product
                        ).first()
                        
                        if existing_item:
                            existing_item.quantity += item.quantity
                            existing_item.save()
                            item.delete()
                        else:
                            item.cart = cart
                            item.save()
                    duplicate_cart.delete()
            else:
                cart = carts.first()
        else:
            cart = Cart.objects.create(cart_id=cart_id)

    return cart

def merge_cart(request, user):
    session_cart_id = request.session.session_key

    if session_cart_id:
        try:
            session_carts = Cart.objects.filter(cart_id=session_cart_id)
            if session_carts.exists():
                if session_carts.count() > 1:
                    # Merge session carts
                    session_cart = session_carts.first()
                    for cart in session_carts[1:]:
                        for item in cart.items.all():
                            existing_item = CartItem.objects.filter(
                                cart=session_cart,
                                store_product=item.store_product,
                                seller_product=item.seller_product
                            ).first()
                            
                            if existing_item:
                                existing_item.quantity += item.quantity
                                existing_item.save()
                                item.delete()
                            else:
                                item.cart = session_cart
                                item.save()
                        cart.delete()
                else:
                    session_cart = session_carts.first()
            else:
                return
            
            user_cart, created = Cart.objects.get_or_create(user=user)

            items = CartItem.objects.filter(cart=session_cart)

            for item in items:
                # Check for existing item with same product
                if item.store_product:
                    existing_item = CartItem.objects.filter(
                        cart=user_cart,
                        store_product=item.store_product
                    ).first()
                else:
                    existing_item = CartItem.objects.filter(
                        cart=user_cart,
                        seller_product=item.seller_product
                    ).first()

                if existing_item:
                    existing_item.quantity += item.quantity
                    existing_item.save()
                    item.delete()
                else:
                    item.cart = user_cart
                    item.save()

            session_cart.delete()

        except Cart.DoesNotExist:
            pass

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

@login_required(login_url='login')
def checkout(request):
    cart = _get_cart(request)
    items = cart.items.all()
    total = sum(item.total_price() for item in items)
    tax = (5 * total)/100
    grand_total = total + tax
    
    return render(request, 'cart/checkout.html', {
        'cart': cart,
        'items': items,
        'total': total,
        'tax': tax,
        'grand_total': grand_total
    })
