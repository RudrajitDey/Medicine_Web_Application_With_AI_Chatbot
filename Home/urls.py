from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    
    path('', views.home, name="home"),
    path('become_seller/', views.become_seller, name="become_seller"),
    path('seller_login/', views.seller_login, name="seller_login"),
    path('vendor_dashboard/', views.vendor_dashboard, name="vendor_dashboard"),
    path('all_medicines/', views.all_medicines, name="all_medicines"),
    path('all_medicines/<slug:slug>/', views.product_detail, name='product_detail'),
    path('subcategory/<slug:slug>/', views.subcategory_products, name='subcategory_products'),
    path('product/<slug:slug>/', views.store_product_detail, name='store_product_detail'),
    path('search/', views.search, name='search'),

    path('how_to_buy/', views.how_to_buy, name='how_to_buy'),
    path('terms-and-conditions/', views.terms_conditions, name='terms_conditions'),
    path('privacy-policy/', views.privacy_policy, name='privacy_policy'),
    path('contact-us/', views.contact_us, name='contact_us'),
    path('faqss/', views.faq_page, name='faq_page'),
    path('all-blogs/', views.all_blogs, name='all_blogs'),
    path('all-salts/', views.all_salts, name='all_salts'),
    path('all-diseases/', views.all_diseases, name='all_diseases'),
    path('all-brands/', views.all_brands, name='all_brands'),
    path('all-medicines/', views.all_medicines, name='all_medicines'),
    path('all-health-products/', views.all_health_products, name='all_health_products'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
