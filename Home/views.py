from django.shortcuts import render, get_object_or_404
from .models import Category, Product,SubCategory, faq

from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from admin_panel.models import vendor, seller_Product, OrderItem
from django.contrib import messages
from django.db.models import Q



# Create your views here.

def home(request):
    categories = Category.objects.prefetch_related('subcategories')
    faqs = faq.objects.all()

    return render(request, "home.html", {
        'categories': categories,
        'faqs': faqs,
    })
def subcategory_products(request, slug):
    subcategory = get_object_or_404(SubCategory, slug=slug)
    products = subcategory.products.all()

    return render(request, 'products/subcategory_products.html', {
        'subcategory': subcategory,
        'products': products
    })


def become_seller(request):
    if request.method == "POST":
        user = User.objects.create_user(
            username=request.POST['username'],
            email=request.POST['email'],
            password=request.POST['password']
        )

        vendor.objects.create(
            user=user,
            shop_name=request.POST['shop_name'],
            owner_name=request.POST['owner_name'],
            phone=request.POST['phone'],
            email=request.POST['email'],
            gst_number=request.POST['gst'],
            drug_license_number=request.POST['license'],
            gst_certificate=request.FILES.get('gst_file'),
            drug_license_file=request.FILES.get('license_file'),
            id_proof=request.FILES.get('id_proof'),
            city=request.POST['city'],
            status='pending',
            is_active=False
        )

        messages.success(request, "Request sent! Wait for admin approval.")
        return redirect('home')

    return render(request, 'footer/become_seller.html')

from django.contrib.auth import authenticate, login


def seller_login(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(username=username, password=password)

        if user:
            try:
                vendors = vendor.objects.get(user=user)

                if vendor.is_active:
                    login(request, user)
                    return redirect('vendor_dashboard')
                else:
                    return render(request, 'authentication/login.html', {
                        'error': 'Wait for admin approval'
                    })

            except vendor.DoesNotExist:
                return render(request, 'authentication/login.html', {
                    'error': 'Not a vendor account'
                })

        else:
            return render(request, 'authentication/login.html', {
                'error': 'Invalid credentials'
            })

    return render(request, 'authentication/login.html')

# def vendor_dashboard(request):

#     return render(request, 'vendor_dashboard/vendor_dashboard.html')


from django.contrib.auth.decorators import login_required
from django.db.models import Sum
 

@login_required
def vendor_dashboard(request):
    
    
    if not hasattr(request.user, 'vendor'):
        return redirect('login')

    vendor = request.user.vendor

    
    total_products = seller_Product.objects.filter(vendor=vendor).count()

   
    total_orders = OrderItem.objects.filter(vendor=vendor).count()

   
    pending_orders = OrderItem.objects.filter(
        vendor=vendor, status="Pending"
    ).count()

   
    earnings = OrderItem.objects.filter(
        vendor=vendor, status="Delivered"
    ).aggregate(total=Sum('price'))['total'] or 0

   
    total_customers = OrderItem.objects.filter(
        vendor=vendor
    ).values('order').distinct().count()

    
    best_products = OrderItem.objects.filter(
        vendor=vendor
    ).values('products__name').annotate(
        total_sold=Sum('quantity')
    ).order_by('-total_sold')[:5]

    context = {
        'vendor': vendor,
        'total_products': total_products,
        'total_orders': total_orders,
        'pending_orders': pending_orders,
        'earnings': earnings,
        'total_customers': total_customers,
        'best_products': best_products,
    }

    return render(request, 'vendor_dashboard/vendor_dashboard.html', context)

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