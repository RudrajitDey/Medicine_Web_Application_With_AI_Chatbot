from django.shortcuts import render, get_object_or_404
from .models import Category, Product,SubCategory, faq, AdBanner

from accounts.models import Account
from django.shortcuts import render, redirect
from admin_panel.models import vendor, seller_Product
from django.contrib import messages
from django.db.models import Q
from orders.models import OrderProduct
from django.contrib import auth



# Create your views here.

def home(request):
    categories = Category.objects.prefetch_related('subcategories')
    faqs = faq.objects.all()
    banners = AdBanner.objects.all()

    return render(request, "home.html", {
        'categories': categories,
        'faqs': faqs,
        'banners': banners,
    })
def subcategory_products(request, slug):
    subcategory = get_object_or_404(SubCategory, slug=slug)
    products = subcategory.products.all()

    return render(request, 'products/subcategory_products.html', {
        'subcategory': subcategory,
        'products': products,
    })


def become_seller(request):
    if request.method == "POST":
        try:
            # Validate required fields
            username = request.POST.get('username', '').strip()
            email = request.POST.get('email', '').strip()
            password = request.POST.get('password', '').strip()
            shop_name = request.POST.get('shop_name', '').strip()
            owner_name = request.POST.get('owner_name', '').strip()
            phone = request.POST.get('phone', '').strip()
            
            # Basic validation
            if not username or not email or not password or not shop_name:
                messages.error(request, "Please fill in all required fields (Username, Email, Password, Shop Name)")
                return render(request, 'footer/become_seller.html')
            
            # Check if username already exists
            if Account.objects.filter(username=username).exists():
                messages.error(request, "Username already exists!")
                return render(request, 'footer/become_seller.html')
            
            # Check if email already exists
            if Account.objects.filter(email=email).exists():
                messages.error(request, "Email already exists!")
                return render(request, 'footer/become_seller.html')
            
            # Create user
            user = Account.objects.create_user(
                first_name=owner_name,
                last_name='',
                username=username,
                email=email,
                password=password
            )

            # Create vendor record
            vendor.objects.create(
                user=user,
                shop_name=shop_name,
                owner_name=owner_name,
                phone=phone,
                email=email,
                gst_number=request.POST.get('gst', ''),
                drug_license_number=request.POST.get('license', ''),
                gst_certificate=request.FILES.get('gst_file'),
                drug_license_file=request.FILES.get('license_file'),
                id_proof=request.FILES.get('id_proof'),
                city=request.POST.get('city', ''),
                status='pending',
                is_active=False
            )

            messages.success(request, "Seller registration successful! Wait for admin approval.")
            return redirect('home')
            
        except Exception as e:
            messages.error(request, f"Registration failed: {str(e)}")
            return render(request, 'footer/become_seller.html')

    return render(request, 'footer/become_seller.html')

from django.contrib.auth import authenticate, login
from accounts.models import Account


def seller_login(request):

    if request.method == "POST":

        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '').strip()

        if not username or not password:
            return render(
                request,
                'authentication/login.html',
                {
                    'error': 'Please enter both username and password'
                }
            )

        try:
            # Find account using username
            account = Account.objects.get(username=username)

            # IMPORTANT: authenticate using EMAIL
            user = auth.authenticate(
                request,
                email=account.email,
                password=password
            )

            if user is not None:

                try:
                    vendor_obj = vendor.objects.get(user=user)

                    if vendor_obj.is_active:

                        # Proper Django login
                        auth.login(request, user)

                        messages.success(
                            request,
                            f"Welcome back, {vendor_obj.shop_name}!"
                        )

                        return redirect('vendor_dashboard')

                    else:
                        messages.error(
                            request,
                            'Your seller account is pending approval.'
                        )

                except vendor.DoesNotExist:
                    messages.error(
                        request,
                        'No vendor account found.'
                    )

            else:
                messages.error(
                    request,
                    'Invalid username or password'
                )

        except Account.DoesNotExist:
            messages.error(
                request,
                'Invalid username or password'
            )

    return render(request, 'authentication/login.html')



from django.contrib.auth.decorators import login_required
from django.db.models import Sum
 

@login_required(login_url='seller_login')
def vendor_dashboard(request):

    if not hasattr(request.user, 'vendor'):
        return redirect('seller_login')

    vendor_obj = request.user.vendor

    total_products = seller_Product.objects.filter(vendor=vendor_obj).count()
    total_orders = OrderProduct.objects.filter(seller_product__vendor=vendor_obj).count()
    pending_orders = OrderProduct.objects.filter(seller_product__vendor=vendor_obj, order__status='New').count()
    earnings = OrderProduct.objects.filter(seller_product__vendor=vendor_obj).aggregate(Sum('product_price'))['product_price__sum'] or 0
    total_customers = OrderProduct.objects.filter(seller_product__vendor=vendor_obj).values('user').distinct().count()
    
    # Best selling products
    best_products = seller_Product.objects.filter(vendor=vendor_obj, status='approved').order_by('-price')[:5]
    
    # Recent orders
    recent_orders = OrderProduct.objects.filter(seller_product__vendor=vendor_obj).select_related('user', 'seller_product').order_by('-created_at')[:10]

    context = {
        'vendor': vendor_obj,
        'total_products': total_products,
        'total_orders': total_orders,
        'pending_orders': pending_orders,
        'earnings': earnings,
        'total_customers': total_customers,
        'best_products': best_products,
        'recent_orders': recent_orders,
    }

    return render(
        request,
        'vendor_dashboard/vendor_dashboard.html',
        context
    )
def all_medicines(request):
    seller_products = seller_Product.objects.filter(status='approved')
    return render(request, 'products/all_medicines.html',{'seller_products':seller_products})

def product_detail(request, slug):
    product = get_object_or_404(seller_Product, slug=slug)
    related_products = seller_Product.objects.exclude(id=product.id)[:10]
    return render(request, 'products/product_detail.html', {
        'product': product,
        'related_products': related_products
     })

def store_product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug)

    related_products = Product.objects.filter(
        subcategory=product.subcategory
    ).exclude(id=product.id)[:8]

    return render(request, 'products/store_product_detail.html', {
        'product': product,
        'related_products': related_products
    })



def search(request):
    query = request.GET.get('q')
    results = []

    if query:
        store_products = Product.objects.filter(
            Q(product_name__icontains=query)
        )

        seller_products = seller_Product.objects.filter(
            Q(name__icontains=query)
        )

        # Combine both
        results = list(store_products) + list(seller_products)

        total_results = len(results) 

    return render(request, 'products/search_results.html', {
        'query': query,
        'results': results,
        'total_results':  total_results,
    })