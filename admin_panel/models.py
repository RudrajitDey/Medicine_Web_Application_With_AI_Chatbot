from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class vendor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    shop_name = models.CharField(max_length=255)
    owner_name = models.CharField(max_length=255)

    phone = models.CharField(max_length=15)
    email = models.EmailField()

    gst_number = models.CharField(max_length=20, unique=True)
    drug_license_number = models.CharField(max_length=50, unique=True)

    gst_certificate = models.FileField(upload_to='vendor_docs/gst/')
    drug_license_file = models.FileField(upload_to='vendor_docs/license/')
    id_proof = models.FileField(upload_to='vendor_docs/id/')

    address = models.TextField()
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    pincode = models.CharField(max_length=100)

    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    )
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.shop_name


class seller_Product(models.Model):
    vendor = models.ForeignKey(vendor, on_delete = models.CASCADE)
    name = models.CharField(max_length=100,blank=True, null=True)
    price = models.FloatField(blank=True, null=True)
    discount_price = models.FloatField(blank=True, null=True)
    stock = models.IntegerField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    category = models.CharField(max_length=100,  null=True, blank=True)
    brand = models.CharField(max_length=100,  null=True, blank=True)
    image = models.ImageField(upload_to='seller_products/',blank=True, null=True)
    expiry_date = models.DateField(blank=True, null=True)
    is_available = models.BooleanField(default=True)
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    )
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.name
    
class Order(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    products = models.ForeignKey(seller_Product, on_delete=models.CASCADE)
    vendor = models.ForeignKey(vendor, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    price = models.FloatField()
    status = models.CharField(max_length=20, default="Pending")