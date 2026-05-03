from .models import Cart, CartItem


def cart_count(request):
    """
    Context processor to provide cart count to all templates
    """
    cart_count = 0
    
    # For logged-in users, get their cart
    if request.user.is_authenticated:
        try:
            cart = Cart.objects.get(user=request.user)
            cart_count = cart.items.count()
        except Cart.DoesNotExist:
            cart_count = 0
    else:
        # For anonymous users, get cart from session
        cart_id = request.session.session_key
        
        if cart_id:
            try:
                cart = Cart.objects.get(cart_id=cart_id, user__isnull=True)
                cart_count = cart.items.count()
            except Cart.DoesNotExist:
                cart_count = 0
    
    return {
        'cart_count': cart_count
    }