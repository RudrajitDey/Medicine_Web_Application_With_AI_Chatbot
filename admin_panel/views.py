from django.shortcuts import render
from django.contrib import messages
from .models import vendor, seller_Product
from django.contrib.auth.decorators import login_required

# Create your views here.

def admin_dashboard(request):
    return render(request, 'admin/admin_dashboard.html')

def seller_list(request):

    vendors = vendor.objects.all().order_by('-created_at')

    return render(request, 'admin/seller/seller_list.html', {'vendors': vendors})

from django.core.mail import send_mail
from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404


def approve_vendor(request, id):
    v = get_object_or_404(vendor, id=id)

    v.status = 'approved'
    v.is_active = True
    v.save()

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
    seller_products = seller_Product.objects.all()
    return render(request, 'admin/seller/seller_product_list.html', {'seller_products': seller_products})

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

        seller_Product.objects.create(
            vendor=vendor_obj,
            name=name,
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