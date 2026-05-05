from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    
    path('place_order/', views.place_order, name='place_order'),
    path('payments/', views.payments, name="payments"),
    path('order_confirmation/<int:order_id>/', views.order_confirmation, name='order_confirmation'),
]   

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)