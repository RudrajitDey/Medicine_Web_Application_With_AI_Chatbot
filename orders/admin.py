from django.contrib import admin
from .models import Payment, Order, OrderProduct

# Register your models here.

class OrderProductInline(admin.TabularInline):
    model = OrderProduct
    extra = 0

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    inlines = [OrderProductInline]

admin.site.register(Payment)
# admin.site.register(Order)
admin.site.register(OrderProduct)

