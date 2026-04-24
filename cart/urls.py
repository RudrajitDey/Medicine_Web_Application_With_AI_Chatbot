from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    
    path("", views.cart_view, name="cart"),
    path('add-to-cart/<int:product_id>/<str:product_type>/', views.add_to_cart, name='add_to_cart'),

    path('increase/<int:item_id>/', views.increase_quantity, name='increase_quantity'),
    path('decrease/<int:item_id>/', views.decrease_quantity, name='decrease_quantity'),
    path('remove/<int:item_id>/', views.remove_item, name='remove_item'),
]   

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)