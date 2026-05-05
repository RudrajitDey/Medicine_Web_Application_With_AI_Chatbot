from django.db import models
from django.conf import settings
from Home.models import Product
from admin_panel.models import seller_Product

# Create your models here.

class Payment(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    payment_id = models.CharField(max_length=100)
    payment_method = models.CharField(max_length=100)
    amount_paid = models.CharField(max_length=100)
    status = models.CharField(max_length=100)
    craeted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.payment_id
    

    
class Order(models.Model):
    STATUS = (
        ('New', 'New'),
        ('Accepted', 'Accepted'),
        ('Completed', 'Completed'),
        ('Cancelled', 'Cancelled'),
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    payment = models.ForeignKey(Payment, on_delete=models.SET_NULL, blank=True, null=True)

    order_number = models.CharField(max_length=20)

    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    phone = models.CharField(max_length=15)
    email = models.EmailField(max_length=50)

    address_line_1 = models.CharField(max_length=50)
    address_line_2 = models.CharField(max_length=50, blank=True)

    country = models.CharField(max_length=50)
    state = models.CharField(max_length=50)
    city = models.CharField(max_length=50)
    pin_code = models.CharField(max_length=50)


    order_total = models.FloatField()
    tax = models.FloatField()

    status = models.CharField(
        max_length=10,
        choices=STATUS,
        default='New'
    )

    ip = models.CharField(blank=True, max_length=20)
    is_ordered = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.first_name
    

    
class OrderProduct(models.Model):

    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='order_items'
    )

    user = models.ForeignKey(
       settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True
    )

    # ✅ SUPPORT BOTH TYPES
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    seller_product = models.ForeignKey(
        seller_Product,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    quantity = models.PositiveIntegerField(default=1)
    product_price = models.DecimalField(max_digits=10, decimal_places=2)
    ordered = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    # =====================
    # 🔥 HELPER METHODS
    # =====================

    def get_product(self):
        return self.product if self.product else self.seller_product

    def get_product_name(self):
        p = self.get_product()
        if p:
            if hasattr(p, 'product_name'):  # seller_Product
                return p.product_name
            elif hasattr(p, 'name'):  # Product (if it had name)
                return p.name
            else:
                return str(p)  # fallback to string representation
        return "Product"

    def get_image(self):
        p = self.get_product()
        if p:
            if hasattr(p, 'product_image'):  # Product
                return p.product_image
            elif hasattr(p, 'product_image'):  # seller_Product
                return p.product_image
            elif hasattr(p, 'image'):  # fallback
                return p.image
        return None

    def sub_total(self):
        return self.quantity * self.product_price

    def __str__(self):
        return self.get_product_name()