from .models import Cart, CartItem

def cart_context(request):
    cart_count = 0
    
    if request.user.is_authenticated:
        carts = Cart.objects.filter(user=request.user)
        if carts.exists():
            # Sum items from all user carts
            cart_count = sum(cart.items.filter(is_active=True).count() for cart in carts)
    else:
        if request.session.session_key:
            carts = Cart.objects.filter(cart_id=request.session.session_key)
            if carts.exists():
                # Sum items from all session carts
                cart_count = sum(cart.items.filter(is_active=True).count() for cart in carts)
    
    return {
        'cart_count': cart_count
    }
