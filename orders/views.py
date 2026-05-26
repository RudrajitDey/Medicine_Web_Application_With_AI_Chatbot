from django.shortcuts import render, redirect
from django.http import JsonResponse
from cart.models import CartItem
from .forms import OrderForm
from .models import Order, OrderProduct, Payment
from cart.views import _get_cart
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.urls import reverse

from Medicine_Store.network_utils import is_network_error

import json

# Create your views here.

def validate_cart_stock(cart_items):
    """Validate stock availability for all items in cart"""
    from Home.models import Product as StoreProduct
    from admin_panel.models import seller_Product as SellerProduct
    
    for item in cart_items:
        product = item.get_product()
        if product and hasattr(product, 'stock'):
            if product.stock < item.quantity:
                product_name = product.product_name if hasattr(product, 'product_name') else product.name
                return False, f'Insufficient stock for {product_name}. Available: {product.stock}, Requested: {item.quantity}'
    return True, None

def send_order_confirmation_email(order, order_items):
    """Send order confirmation email to customer"""
    try:
        mail_subject = 'Order Confirmation - Medicine Web Store'
        message = render_to_string('orders/order_confirmation_email.html', {
            'order': order,
            'order_items': order_items
        })
        to_email = order.email
        send_email = EmailMessage(mail_subject, message, to=[to_email])
        send_email.content_subtype = 'html'
        send_email.send()
        return True
    except Exception as e:
        print(f"Error sending order confirmation email: {e}")
        return False

@login_required(login_url='login')
def place_order(request):
    if request.method == 'POST':
        cart = _get_cart(request)
        items = cart.items.all()
        
        if not items.exists():
            messages.error(request, 'Your cart is empty!')
            return redirect('cart')
        
        # Validate stock availability before processing
        stock_valid, stock_error = validate_cart_stock(items)
        if not stock_valid:
            messages.error(request, stock_error)
            return redirect('cart')
        
        # Get form data
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        address_line_1 = request.POST.get('address_line_1')
        address_line_2 = request.POST.get('address_line_2', '')
        city = request.POST.get('city')
        state = request.POST.get('state')
        pincode = request.POST.get('pincode')
        country = request.POST.get('country', 'India')
        payment_method = request.POST.get('payment_method', 'cod')
        
        # Create order
        import uuid
        order_number = str(uuid.uuid4())[:8].upper()
        
        total = sum(item.total_price() for item in items)
        tax = (5 * total) / 100
        
        # Get user IP address
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        
        order = Order.objects.create(
            user=request.user,
            order_number=order_number,
            first_name=first_name,
            last_name=last_name,
            email=email,
            phone=phone,
            address_line_1=address_line_1,
            address_line_2=address_line_2,
            city=city,
            state=state,
            pin_code=pincode,
            country=country,
            order_total=total,
            tax=tax,
            status='New',
            is_ordered=True,
            ip=ip
        )
        
        # Create order items and reduce stock
        for item in items:
            product = item.get_product()
            
            # Check product type and assign to correct field
            from Home.models import Product as StoreProduct
            from admin_panel.models import seller_Product as SellerProduct
            
            # Validate stock availability
            if product and hasattr(product, 'stock'):
                if product.stock < item.quantity:
                    messages.error(request, f'Insufficient stock for {product.product_name if hasattr(product, "product_name") else product.name}. Available: {product.stock}, Requested: {item.quantity}')
                    return redirect('cart')
            
            if isinstance(product, SellerProduct):  # It's a seller_Product
                OrderProduct.objects.create(
                    order=order,
                    user=request.user,
                    product=None,
                    seller_product=product,
                    quantity=item.quantity,
                    product_price=product.price if product else 0,
                    ordered=True
                )
                # Reduce stock for seller product
                if product and hasattr(product, 'stock'):
                    product.stock -= item.quantity
                    product.save()
            elif isinstance(product, StoreProduct):  # It's a store Product
                OrderProduct.objects.create(
                    order=order,
                    user=request.user,
                    product=product,
                    seller_product=None,
                    quantity=item.quantity,
                    product_price=product.price if product else 0,
                    ordered=True
                )
                # Reduce stock for store product
                if product and hasattr(product, 'stock'):
                    product.stock -= item.quantity
                    product.save()
            else:  # Fallback - try to determine by attributes
                if hasattr(product, 'product_name'):  # Likely seller_Product
                    OrderProduct.objects.create(
                        order=order,
                        user=request.user,
                        product=None,
                        seller_product=product,
                        quantity=item.quantity,
                        product_price=product.price if product else 0,
                        ordered=True
                    )
                    # Reduce stock for seller product
                    if product and hasattr(product, 'stock'):
                        product.stock -= item.quantity
                        product.save()
                else:  # Likely store Product
                    OrderProduct.objects.create(
                        order=order,
                        user=request.user,
                        product=product,
                        seller_product=None,
                        quantity=item.quantity,
                        product_price=product.price if product else 0,
                        ordered=True
                    )
                    # Reduce stock for store product
                    if product and hasattr(product, 'stock'):
                        product.stock -= item.quantity
                        product.save()
        
        # Send order confirmation email after order creation
        order_items = OrderProduct.objects.filter(order=order)
        email_sent = send_order_confirmation_email(order, order_items)
        if email_sent:
            messages.success(request, 'Order placed successfully! Confirmation email sent.')
        else:
            messages.success(request, 'Order placed successfully! Please complete payment.')
        
        # Clear cart
        items.delete()
        cart.delete()
        
        return redirect('payments')
    
    return redirect('checkout')

@login_required(login_url='login')
def order_confirmation(request, order_id):
    try:
        order = Order.objects.get(id=order_id, user=request.user)
        order_items = OrderProduct.objects.filter(order=order)
        
        context = {
            'order': order,
            'order_items': order_items,
            'total': order.order_total + order.tax
        }
        return render(request, 'orders/order_confirmation.html', context)
    except Order.DoesNotExist:
        messages.error(request, 'Order not found!')
        return redirect('home')
    

@login_required(login_url='login')
def payments(request):
    
    if request.method == 'POST':
        try:
            body = json.loads(request.body)
            payment = Payment()
            payment_method = body.get('payment_method')
        except json.JSONDecodeError:
            payment_method = request.POST.get('payment_method')
        
        # Get the most recent order for this user
        try:
            order = Order.objects.filter(user=request.user).order_by('-created_at').first()
            if not order:
                messages.error(request, 'No order found!')
                return redirect('home')
            
            # Create payment record
            import uuid
            payment_id = str(uuid.uuid4())[:12].upper()
            
            payment = Payment.objects.create(
                user=request.user,
                payment_id=payment_id,
                payment_method=payment_method,
                amount_paid=str(order.order_total + order.tax),
                status='Completed'  # In real app, this would be 'Pending' initially
            )
            
            # Update order with payment reference
            order.payment = payment
            order.status = 'Accepted'
            order.is_ordered = True
            order.save()
            
            # Handle different payment methods
            if payment_method == 'cod':
                messages.success(request, 'Order placed successfully! Pay on delivery.')
            elif payment_method == 'card':
                # In real app, integrate with payment gateway
                messages.success(request, 'Payment successful! Order confirmed.')
            elif payment_method == 'upi':
                # In real app, redirect to UPI app
                messages.success(request, 'UPI payment initiated! Order confirmed.')
            elif payment_method == 'netbanking':
                # In real app, redirect to bank portal
                messages.success(request, 'Net banking payment initiated! Order confirmed.')
            
            # Return JSON response for PayPal redirect
            return JsonResponse({
                'success': True,
                'redirect_url': f'/orders/order_confirmation/{order.id}/'
            })
            
        except Exception as e:
            if is_network_error(e):
                is_json_request = (
                    request.content_type == 'application/json'
                    or request.headers.get('Content-Type', '').startswith('application/json')
                )
                if is_json_request:
                    return JsonResponse({
                        'success': False,
                        'network_error': True,
                        'redirect_url': reverse('connection_error'),
                    }, status=503)
                return redirect('connection_error')
            messages.error(request, 'Payment processing failed. Please try again.')
            return redirect('payments')
    
    # GET request - show payment page with order details
    try:
        # Get the most recent order for this user (regardless of status)
        order = Order.objects.filter(user=request.user).order_by('-created_at').first()
        if order:
            order_items = OrderProduct.objects.filter(order=order)
            total = order.order_total + order.tax
        else:
            order = None
            order_items = []
            total = 0
    except:
        order = None
        order_items = []
        total = 0
    
    context = {
        'order': order,
        'order_items': order_items,
        'total': total
    }
    return render(request, 'orders/payments.html', context)





