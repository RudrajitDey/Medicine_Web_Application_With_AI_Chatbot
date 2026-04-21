from django.contrib import admin
from .models import Category, Product, faq

# Register models.

admin.site.register(Category)
admin.site.register(Product)
admin.site.register(faq)
