from django.shortcuts import render, get_object_or_404
from django.contrib import messages
from django.db import models
from .models import vendor, seller_Product, ProductContent, ProductPoint
from django.contrib.auth.decorators import login_required
from django.utils.text import slugify
from orders.models import OrderProduct, Order
from accounts.models import Account


# Create your views here.

def admin_dashboard(request):
    from django.db.models import Count, Sum, Avg
    from datetime import datetime, timedelta
    from accounts.models import Account
    from orders.models import Order, OrderProduct
    
    # Get total counts
    total_users = Account.objects.count()
    total_vendors = vendor.objects.count()
    total_orders = Order.objects.count()
    
    # Get recent orders with items
    recent_orders = Order.objects.select_related('user').prefetch_related('order_items').order_by('-created_at')[:10]
    
    # Get best selling products (simplified query)
    best_selling_products = seller_Product.objects.filter(
        orderproduct__isnull=False
    ).distinct().order_by('-created_at')[:10]
    
    # Calculate total earnings
    total_earnings = OrderProduct.objects.aggregate(
        total=Sum('product_price')
    )['total'] or 0
    
    # Calculate growth percentages (simplified - you may want to implement actual period comparison)
    user_growth_percentage = 12.5  # Example percentage
    order_growth_percentage = 8.2   # Example percentage  
    vendor_growth_percentage = 15.3 # Example percentage
    earnings_growth_percentage = 22.1 # Example percentage
    
    context = {
        'total_users': total_users,
        'total_vendors': total_vendors,
        'total_orders': total_orders,
        'total_earnings': f"{total_earnings:.2f}",
        'user_growth_percentage': user_growth_percentage,
        'order_growth_percentage': order_growth_percentage,
        'vendor_growth_percentage': vendor_growth_percentage,
        'earnings_growth_percentage': earnings_growth_percentage,
        'recent_orders': recent_orders,
        'best_selling_products': best_selling_products,
    }
    
    return render(request, 'admin/admin_dashboard.html', context)

def seller_list(request):

    vendors = vendor.objects.all().order_by('-created_at')

    return render(request, 'admin/seller/seller_list.html', {'vendors': vendors})

def admin_orders(request):
    orders = Order.objects.select_related('user').prefetch_related('order_items').order_by('-created_at')
    
    # Apply filters
    status_filter = request.GET.get('status', '')
    date_filter = request.GET.get('date', '')
    customer_filter = request.GET.get('customer', '')
    min_amount_filter = request.GET.get('min_amount', '')
    
    if status_filter:
        orders = orders.filter(status__iexact=status_filter)
    
    if date_filter:
        orders = orders.filter(created_at__date=date_filter)
    
    if customer_filter:
        orders = orders.filter(
            models.Q(user__username__icontains=customer_filter) |
            models.Q(first_name__icontains=customer_filter) |
            models.Q(last_name__icontains=customer_filter)
        )
    
    if min_amount_filter:
        try:
            min_amount = float(min_amount_filter)
            orders = orders.filter(order_total__gte=min_amount)
        except ValueError:
            pass
    
    return render(request, 'admin/orders/admin_orders.html', {'orders': orders})

def admin_customer(request):
    customers = Account.objects.all().order_by('-date_joined')
    
    # Apply filters
    status_filter = request.GET.get('status', '')
    date_filter = request.GET.get('date', '')
    search_filter = request.GET.get('search', '')
    domain_filter = request.GET.get('domain', '')
    
    if status_filter:
        if status_filter == 'active':
            customers = customers.filter(is_active=True)
        elif status_filter == 'inactive':
            customers = customers.filter(is_active=False)
    
    if date_filter:
        customers = customers.filter(date_joined__date=date_filter)
    
    if search_filter:
        customers = customers.filter(
            models.Q(username__icontains=search_filter) |
            models.Q(first_name__icontains=search_filter) |
            models.Q(last_name__icontains=search_filter) |
            models.Q(email__icontains=search_filter)
        )
    
    if domain_filter:
        customers = customers.filter(email__endswith=f'@{domain_filter}')
    
    # Calculate statistics
    total_customers = customers.count()
    active_customers = customers.filter(is_active=True).count()
    
    context = {
        'customers': customers,
        'total_customers': total_customers,
        'active_customers': active_customers,
    }
    
    return render(request, 'admin/custommers/admin_customer.html', context)

def admin_order_view(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    order_items = OrderProduct.objects.filter(order=order).select_related('product', 'seller_product')
    
    # Calculate item totals
    items_with_totals = []
    for item in order_items:
        item_total = item.quantity * item.product_price
        items_with_totals.append({
            'item': item,
            'total': item_total
        })
    
    # Get customer information
    customer = order.user
    customer_info = {
        'first_name': order.first_name or customer.first_name,
        'last_name': order.last_name or customer.last_name,
        'email': order.email or customer.email,
        'phone': order.phone or customer.phone_number,
        'address_line_1': order.address_line_1,
        'address_line_2': order.address_line_2,
        'city': order.city,
        'state': order.state,
        'pincode': order.pin_code,  # Fixed: use pin_code instead of pincode
        'country': order.country,
    }
    
    context = {
        'order': order,
        'order_items': order_items,
        'items_with_totals': items_with_totals,
        'customer': customer,
        'customer_info': customer_info,
    }
    
    return render(request, 'admin/orders/admin_order_detail.html', context)

def admin_order_delete(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    
    if request.method == 'POST':
        order.delete()
        messages.success(request, 'Order deleted successfully.')
        return redirect('admin_orders')
    
    # If GET request, show confirmation page
    return render(request, 'admin/orders/admin_order_delete.html', {'order': order})

def shop_orders(request):
    # Filter orders that contain ONLY shop products (no seller products)
    # This excludes orders that have both shop and seller products
    orders = Order.objects.filter(
        order_items__product__isnull=False
    ).exclude(
        order_items__seller_product__isnull=False
    ).select_related('user').prefetch_related('order_items').order_by('-created_at').distinct()
    
    # Apply filters
    status_filter = request.GET.get('status', '')
    date_filter = request.GET.get('date', '')
    customer_filter = request.GET.get('customer', '')
    min_amount_filter = request.GET.get('min_amount', '')
    
    if status_filter:
        orders = orders.filter(status__iexact=status_filter)
    
    if date_filter:
        orders = orders.filter(created_at__date=date_filter)
    
    if customer_filter:
        orders = orders.filter(
            models.Q(user__username__icontains=customer_filter) |
            models.Q(first_name__icontains=customer_filter) |
            models.Q(last_name__icontains=customer_filter)
        )
    
    if min_amount_filter:
        try:
            min_amount = float(min_amount_filter)
            orders = orders.filter(order_total__gte=min_amount)
        except ValueError:
            pass
    
    # Calculate statistics
    total_orders = orders.count()
    pending_orders = orders.filter(status='New').count()
    completed_orders = orders.filter(status='Completed').count()
    
    context = {
        'orders': orders,
        'total_orders': total_orders,
        'pending_orders': pending_orders,
        'completed_orders': completed_orders,
    }
    
    return render(request, 'admin/orders/shop_orders.html', context)

def admin_earnings(request):
    # Calculate earnings from all orders
    all_orders = Order.objects.all()
    
    # Calculate total earnings
    total_earnings = all_orders.aggregate(
        total=models.Sum('order_total')
    )['total'] or 0
    
    # Calculate earnings by status
    completed_orders = all_orders.filter(status='Completed')
    completed_earnings = completed_orders.aggregate(
        total=models.Sum('order_total')
    )['total'] or 0
    
    pending_orders = all_orders.filter(status='New')
    pending_earnings = pending_orders.aggregate(
        total=models.Sum('order_total')
    )['total'] or 0
    
    # Calculate monthly earnings
    from django.db.models import Count
    from django.utils import timezone
    from datetime import timedelta
    
    current_month = timezone.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    monthly_earnings = all_orders.filter(
        created_at__gte=current_month
    ).aggregate(
        total=models.Sum('order_total')
    )['total'] or 0
    
    # Calculate earnings by product type
    shop_orders = Order.objects.filter(
        order_items__product__isnull=False
    ).exclude(
        order_items__seller_product__isnull=False
    ).distinct()
    
    shop_earnings = shop_orders.aggregate(
        total=models.Sum('order_total')
    )['total'] or 0
    
    # Calculate vendor earnings (orders with seller products)
    vendor_orders = Order.objects.filter(
        order_items__seller_product__isnull=False
    ).distinct()
    
    vendor_earnings = vendor_orders.aggregate(
        total=models.Sum('order_total')
    )['total'] or 0
    
    context = {
        'total_earnings': total_earnings,
        'completed_earnings': completed_earnings,
        'pending_earnings': pending_earnings,
        'monthly_earnings': monthly_earnings,
        'shop_earnings': shop_earnings,
        'vendor_earnings': vendor_earnings,
        'total_orders_count': all_orders.count(),
        'completed_orders_count': completed_orders.count(),
        'pending_orders_count': pending_orders.count(),
    }
    
    return render(request, 'admin/earnings/admin_earnings.html', context)

def admin_accept_shop_order(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    order.status = 'Accepted'
    order.save()
    messages.success(request, f"Shop Order #{order.id} accepted! 📦")
    return redirect('shop_orders')

def admin_complete_shop_order(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    order.status = 'Completed'
    order.save()
    messages.success(request, f"Shop Order #{order.id} completed! 📦")
    return redirect('shop_orders')

def admin_reject_shop_order(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    order.status = 'Rejected'
    order.save()
    messages.success(request, f"Shop Order #{order.id} rejected! 🗑️")
    return redirect('shop_orders')

from django.core.mail import send_mail
from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404


def approve_vendor(request, id):
    v = get_object_or_404(vendor, id=id)

    v.status = 'approved'
    v.is_active = True
    v.save()
    
    # Also activate the associated Account
    if v.user:
        v.user.is_active = True
        v.user.save()

    # 📧 Send Email
    send_mail(
        subject="Seller Approved ✅",
        message=f"""
Hello {v.owner_name},

Your seller account has been approved 🎉

You can now login and start selling.

Thank you!
""",
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=[v.email],
        fail_silently=False
    )

    return redirect('seller_list')

def reject_vendor(request, id):
    v = get_object_or_404(vendor, id=id)

    v.status = 'rejected'
    v.is_active = False
    v.save()

    send_mail(
        subject="Seller Rejected ❌",
        message="Your seller request was rejected. Contact support.",
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=[v.email],
        fail_silently=True
    )

    return redirect('seller_list')

def delete_vendor(request, id):
    v = get_object_or_404(vendor, id=id)
    user = v.user
    v.delete()
    user.delete()
    return redirect('seller_list')


def seller_product_list(request):
    seller_products = seller_Product.objects.all().select_related('vendor').order_by('-created_at')
    
    # Statistics
    total_products = seller_products.count()
    approved_products = seller_products.filter(status='approved').count()
    pending_products = seller_products.filter(status='pending').count()
    rejected_products = seller_products.filter(status='rejected').count()
    total_vendors = seller_Product.objects.values('vendor').distinct().count()
    
    # Stock analysis
    low_stock_products = seller_products.filter(stock__lte=10).count()
    out_of_stock_products = seller_products.filter(stock=0).count()
    
    # Recent activity
    recent_products = seller_products.order_by('-created_at')[:5]
    
    # Vendor statistics
    vendor_stats = {}
    for product in seller_products:
        vendor_name = product.vendor.shop_name
        if vendor_name not in vendor_stats:
            vendor_stats[vendor_name] = {
                'total_products': 0,
                'approved_products': 0,
                'pending_products': 0,
                'rejected_products': 0,
                'vendor': product.vendor
            }
        vendor_stats[vendor_name]['total_products'] += 1
        if product.status == 'approved':
            vendor_stats[vendor_name]['approved_products'] += 1
        elif product.status == 'pending':
            vendor_stats[vendor_name]['pending_products'] += 1
        elif product.status == 'rejected':
            vendor_stats[vendor_name]['rejected_products'] += 1
    
    context = {
        'seller_products': seller_products,
        'total_products': total_products,
        'approved_products': approved_products,
        'pending_products': pending_products,
        'rejected_products': rejected_products,
        'total_vendors': total_vendors,
        'low_stock_products': low_stock_products,
        'out_of_stock_products': out_of_stock_products,
        'recent_products': recent_products,
        'vendor_stats': vendor_stats,
    }
    
    return render(request, 'admin/seller/seller_product_list.html', context)

def approve_product(request, id):
    product = get_object_or_404(seller_Product, id=id)
    product.status = 'approved'
    product.save()
    return redirect('seller_product_list')


def reject_product(request, id):
    product = get_object_or_404(seller_Product, id=id)
    product.status = 'rejected'
    product.save()
    return redirect('seller_product_list')

def product_page(request):
    vendor = request.user.vendor
    seller_product = seller_Product.objects.filter(vendor=vendor)
    return render(request, 'vendor_dashboard/seller_pages/product_page.html', {'seller_product':seller_product})

@login_required
def add_product(request):
    try:
        vendor_obj = vendor.objects.get(user=request.user)
    except vendor.DoesNotExist:
        return render(request, 'vendor_dashboard/seller_pages/add_product.html', {
            'error': 'You are not registered as a vendor'
        })

    # ❗ Prevent unapproved sellers
    if vendor_obj.status != 'approved':
        return render(request, 'vendor_dashboard/seller_pages/add_product.html', {
            'error': 'Wait for admin approval before adding products'
        })

    if request.method == "POST":
        name = request.POST.get('name')
        description = request.POST.get('description')
        category = request.POST.get('category')
        brand = request.POST.get('brand')
        price = request.POST.get('price')
        stock = request.POST.get('stock')
        expiry_date = request.POST.get('expiry_date')
        image = request.FILES.get('image')
        discount_price = request.POST.get('discount_price')
        is_available=True if request.POST.get('is_available') == "True" else False

        product = seller_Product.objects.create(
            vendor=vendor_obj,
            name=name,
            slug=slugify(name),
            description=description,
            category=category,
            brand=brand,
            price=price,
            stock=stock,
            expiry_date=expiry_date,
            image=image,
            discount_price=discount_price,
            is_available=is_available
        )



        # 👉 Handle dynamic sections
        section_types = request.POST.getlist('section_type[]')
        titles = request.POST.getlist('section_title[]')
        contents = request.POST.getlist('section_content[]')

        for i in range(len(section_types)):
            if contents[i]:  # avoid empty
                content_obj = ProductContent.objects.create(
                    product_s=product,
                    section_type=section_types[i],
                    title=titles[i],
                    content=contents[i]
                )

                # 👉 Convert lines to bullet points
                lines = contents[i].split("\n")
                for line in lines:
                    if line.strip():
                        ProductPoint.objects.create(
                            content=content_obj,
                            text=line.strip()
                        )

        messages.success(request, "Product added successfully ✅")
        return redirect('add_product')  # reload page

    return render(request, 'vendor_dashboard/seller_pages/add_product.html')

# Edit Product

@login_required
def edit_product(request, id):
    vendor_obj = get_object_or_404(vendor, user=request.user)
    product = get_object_or_404(seller_Product, id=id, vendor=vendor_obj)

    if request.method == "POST":
        product.name = request.POST.get('name')
        product.description = request.POST.get('description')
        product.category = request.POST.get('category')
        product.brand = request.POST.get('brand')
        product.price = request.POST.get('price')
        product.discount_price = request.POST.get('discount_price')
        product.stock = request.POST.get('stock')
        product.expiry_date = request.POST.get('expiry_date')

        # Boolean fix
        product.is_available = True if request.POST.get('is_available') == "True" else False

        # Image update (optional)
        if request.FILES.get('image'):
            product.image = request.FILES.get('image')

        product.save()
        messages.success(request, "Product updated successfully ✅")
        return redirect('product_page')

    return render(request, 'vendor_dashboard/seller_pages/edit_product.html', {
        'product': product
    })

# Delete Product

@login_required
def delete_product(request, id):
    vendor_obj = get_object_or_404(vendor, user=request.user)
    product = get_object_or_404(seller_Product, id=id, vendor=vendor_obj)

    product.delete()
    messages.success(request, "Product deleted successfully ❌")
    return redirect('product_page')


def all_orders(request):
    vendor = request.user.vendor
    # Fetch orders for this vendor's products
    orders = OrderProduct.objects.filter(seller_product__vendor=vendor).select_related('user', 'seller_product', 'order').order_by('-created_at')
    return render(request, 'vendor_dashboard/seller_pages/all_orders.html', {'orders': orders})


def order_detail(request, order_id):
    vendor = request.user.vendor
    # Get specific order for this vendor with related objects
    order = get_object_or_404(
        OrderProduct.objects.select_related('user', 'seller_product', 'order', 'order__payment'),
        id=order_id, 
        seller_product__vendor=vendor
    )
    
    return render(request, 'vendor_dashboard/seller_pages/order_detail.html', {'order': order})


@login_required
def accept_order(request, order_id):
    vendor = request.user.vendor
    # Get specific order for this vendor
    order_product = get_object_or_404(
        OrderProduct.objects.select_related('user', 'seller_product', 'order'),
        id=order_id, 
        seller_product__vendor=vendor
    )
    
    # Update Order model status to Accepted
    order = order_product.order
    order.status = 'Accepted'
    order.save()
    
    messages.success(request, f"Order #{order.id} accepted! 📦")
    return redirect('all_orders')

@login_required
def complete_order(request, order_id):
    vendor = request.user.vendor
    # Get specific order for this vendor
    order_product = get_object_or_404(
        OrderProduct.objects.select_related('user', 'seller_product', 'order'),
        id=order_id, 
        seller_product__vendor=vendor
    )
    
    # Update Order model status to Completed
    order = order_product.order
    order.status = 'Completed'
    order.save()
    
    # Also update OrderProduct status
    order_product.ordered = True
    order_product.save()
    
    messages.success(request, f"Order #{order.id} marked as completed! 📦")
    return redirect('all_orders')

@login_required
def reject_order(request, order_id):
    try:
        vendor = request.user.vendor
        
        # Get specific order for this vendor
        order_product = get_object_or_404(
            OrderProduct.objects.select_related('user', 'seller_product', 'order'),
            id=order_id, 
            seller_product__vendor=vendor
        )
        
        # Update Order model status to Rejected
        order = order_product.order
        order.status = 'Rejected'
        order.save()
        
        messages.success(request, f"Order #{order.id} rejected! 🗑️")
        
    except Exception as e:
        messages.error(request, f"Error rejecting order: {str(e)} ❌")
    
    return redirect('all_orders')


@login_required
def all_customers(request):
    """Display all customers for the vendor"""
    vendor = request.user.vendor
    
    # Get all orders for this vendor to extract customers
    orders = OrderProduct.objects.filter(seller_product__vendor=vendor).select_related('user', 'seller_product', 'order')
    
    # Extract unique customers from orders
    customers = {}
    for order in orders:
        if order.user not in customers:
            customers[order.user] = {
                'user': order.user,
                'total_orders': 0,
                'total_spent': 0,
                'last_order': None
            }
        customers[order.user]['total_orders'] += 1
        customers[order.user]['total_spent'] += order.product_price * order.quantity
        if not customers[order.user]['last_order'] or order.created_at > customers[order.user]['last_order']:
            customers[order.user]['last_order'] = order.created_at
    
    return render(request, 'vendor_dashboard/seller_pages/all_customers.html', {'customers': customers.values()})


@login_required
def customer_detail(request, customer_id):
    """Display customer details and order history"""
    vendor = request.user.vendor
    
    # Get customer and their orders
    customer = get_object_or_404(
        Account,
        id=customer_id
    )
    
    orders = OrderProduct.objects.filter(
        user=customer,
        seller_product__vendor=vendor
    ).select_related('seller_product', 'order', 'order__payment').order_by('-created_at')
    
    # Calculate total spent by this customer and add total_price to each order
    total_spent = 0
    for order in orders:
        order.total_price = order.product_price * order.quantity
        total_spent += order.total_price
    
    # Get address information from the most recent order
    customer_address = None
    if orders.exists():
        latest_order = orders.first()
        if hasattr(latest_order, 'order') and latest_order.order:
            # Try to get address from the Order model
            customer_address = {
                'first_name': getattr(latest_order.order, 'first_name', ''),
                'last_name': getattr(latest_order.order, 'last_name', ''),
                'phone': getattr(latest_order.order, 'phone', ''),
                'address_line_1': getattr(latest_order.order, 'address_line_1', ''),
                'address_line_2': getattr(latest_order.order, 'address_line_2', ''),
                'city': getattr(latest_order.order, 'city', ''),
                'state': getattr(latest_order.order, 'state', ''),
                'postal_code': getattr(latest_order.order, 'postal_code', ''),
                'country': getattr(latest_order.order, 'country', 'India')
            }
    
    return render(request, 'vendor_dashboard/seller_pages/customer_detail.html', {
        'customer': customer, 
        'orders': orders, 
        'total_spent': total_spent,
        'customer_address': customer_address
    })


@login_required
def earnings(request):
    """Display earnings and sales analytics for the vendor"""
    vendor = request.user.vendor
    
    # Get all orders for this vendor
    orders = OrderProduct.objects.filter(seller_product__vendor=vendor).select_related('seller_product', 'order')
    
    # Calculate dates
    from datetime import datetime, timedelta
    today = datetime.now()
    
    # Weekly (last 7 days)
    week_ago = today - timedelta(days=7)
    weekly_orders = orders.filter(created_at__gte=week_ago)
    weekly_revenue = sum(order.product_price * order.quantity for order in weekly_orders)
    weekly_sales = len(weekly_orders)
    
    # Monthly (last 30 days)
    month_ago = today - timedelta(days=30)
    monthly_orders = orders.filter(created_at__gte=month_ago)
    monthly_revenue = sum(order.product_price * order.quantity for order in monthly_orders)
    monthly_sales = len(monthly_orders)
    
    # Yearly (last 365 days)
    year_ago = today - timedelta(days=365)
    yearly_orders = orders.filter(created_at__gte=year_ago)
    yearly_revenue = sum(order.product_price * order.quantity for order in yearly_orders)
    yearly_sales = len(yearly_orders)
    
    # Total revenue (all time)
    total_revenue = sum(order.product_price * order.quantity for order in orders)
    total_sales = len(orders)
    
    # Recent transactions for display
    recent_orders = orders.order_by('-created_at')[:10]
    
    # Calculate average order value
    avg_order_value = total_revenue / total_sales if total_sales > 0 else 0
    
    # Monthly breakdown for chart
    monthly_breakdown = []
    for i in range(12):
        month_start = today - timedelta(days=30 * (i + 1))
        month_end = today - timedelta(days=30 * i)
        month_orders = orders.filter(created_at__gte=month_start, created_at__lt=month_end)
        month_revenue = sum(order.product_price * order.quantity for order in month_orders)
        monthly_breakdown.append({
            'month': month_start.strftime('%b'),
            'revenue': month_revenue,
            'orders': len(month_orders)
        })
    
    context = {
        'weekly_revenue': weekly_revenue,
        'weekly_sales': weekly_sales,
        'monthly_revenue': monthly_revenue,
        'monthly_sales': monthly_sales,
        'yearly_revenue': yearly_revenue,
        'yearly_sales': yearly_sales,
        'total_revenue': total_revenue,
        'total_sales': total_sales,
        'avg_order_value': avg_order_value,
        'recent_orders': recent_orders,
        'monthly_breakdown': monthly_breakdown[::-1],  # Reverse to show oldest to newest
    }
    
    return render(request, 'vendor_dashboard/seller_pages/earnings.html', context)