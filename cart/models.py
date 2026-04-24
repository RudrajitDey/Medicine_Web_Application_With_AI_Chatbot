from django.db import models
from Home.models import Product
from admin_panel.models import seller_Product

# Create your models here.

class Cart(models.Model):
    cart_id = models.CharField(max_length=250, blank=True)
    date_added = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.cart_id
    
class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    store_product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True, blank=True)
    seller_product = models.ForeignKey(seller_Product, on_delete=models.CASCADE, null=True, blank=True)
    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True) 

    def clean(self):
        if not self.store_product and not self.seller_product:
            raise ValueError("CartItem must have one product")

        if self.store_product and self.seller_product:
            raise ValueError("Only one product allowed")
    
    # Get actual product 
    def get_product(self):
        return self.store_product if self.store_product else self.seller_product

    def total_price(self):
        product = self.get_product()
        return product.price * self.quantity if product else 0

    def __str__(self):
        product = self.get_product()
        return f"{product.name} ({self.quantity})" if product else "Empty CartItem"
    
    def get_product_name(self):
        product = self.get_product()

        if hasattr(product, 'name'):
            return product.name
        elif hasattr(product, 'product_name'):
            return product.product_name

        return "No Name"
    
    def get_image(self):
        product = self.get_product()

        if hasattr(product, 'image'):
            return product.image 
        elif hasattr(product, 'product_image'):
            return product.product_image

        return "No Image"