from .models import Cart, CartItem

def cart_context(request):
    cart_count = 0
    
    if request.session.session_key:
        try:
            cart = Cart.objects.get(cart_id=request.session.session_key)
            cart_count = cart.items.filter(is_active=True).count()
        except Cart.DoesNotExist:
            pass
    
    return {
        'cart_count': cart_count
    }
