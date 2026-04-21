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
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
