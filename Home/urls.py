from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    
    path('', views.home, name="home"),
    path('become_seller/', views.become_seller, name="become_seller"),
    path('login/', views.seller_login, name="login"),
    path('vendor_dashboard/', views.vendor_dashboard, name="vendor_dashboard"),
    path('all_medicines/', views.all_medicines, name="all_medicines"),
    path('all_medicines/<slug:slug>/', views.product_detail, name='product_detail'),
    path('subcategory/<slug:slug>/', views.subcategory_products, name='subcategory_products'),
    path('product/<slug:slug>/', views.store_product_detail, name='store_product_detail'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
