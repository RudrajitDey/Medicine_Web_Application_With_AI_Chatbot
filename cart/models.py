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
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    store_product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True, blank=True)
    seller_product = models.ForeignKey(seller_Product, on_delete=models.CASCADE, null=True, blank=True)
    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True) 

    def __str__(self):
        product = self.get_product()
        return f"{product.name} ({self.quantity})"
    
    # Get actual product 
    def get_product(self):
        return self.store_product if self.store_product else self.seller_product

    # # 🔥 Price calculation
    # def total_price(self):
    #     product = self.get_product()
    #     return product.price * self.quantity
