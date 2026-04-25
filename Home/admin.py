from django.contrib import admin
from .models import Category, SubCategory, Product, faq, AdBanner

# Register models.

admin.site.register(Category)
admin.site.register(Product)
admin.site.register(faq)
admin.site.register(SubCategory)
admin.site.register(AdBanner)

