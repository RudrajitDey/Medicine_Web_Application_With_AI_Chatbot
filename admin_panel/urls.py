from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    
    path("", views.admin_dashboard, name="admin_dashboard"),
    path("seller_list/", views.seller_list, name="seller_list"),
    path("admin_orders/", views.admin_orders, name="admin_orders"),
    path("admin_order_view/<int:order_id>/", views.admin_order_view, name="admin_order_view"),
    path("admin_order_delete/<int:order_id>/", views.admin_order_delete, name="admin_order_delete"),
    path("shop_orders/", views.shop_orders, name="shop_orders"),
    path("admin_accept_shop_order/<int:order_id>/", views.admin_accept_shop_order, name="admin_accept_shop_order"),
    path("admin_complete_shop_order/<int:order_id>/", views.admin_complete_shop_order, name="admin_complete_shop_order"),
    path("admin_reject_shop_order/<int:order_id>/", views.admin_reject_shop_order, name="admin_reject_shop_order"),
    path("admin_earnings/", views.admin_earnings, name="admin_earnings"),
    path("admin_customer/", views.admin_customer, name="admin_customer"),
    path('approve_vendor/<int:id>/', views.approve_vendor, name='approve_vendor'),
    path('reject_vendor/<int:id>/', views.reject_vendor, name='reject_vendor'),
    path('delete_vendor/<int:id>/', views.delete_vendor, name='delete_vendor'),
    path('seller_product_list/', views.seller_product_list, name="seller_product_list"),
    path('approve_product/<int:id>/', views.approve_product, name='approve_product'),
    path('reject_product/<int:id>/', views.reject_product, name='reject_product'),
    path('product_page/', views.product_page, name="product_page"),
    path('add_product/', views.add_product, name="add_product"),
    path('edit_product/<int:id>/', views.edit_product, name='edit_product'),
    path('delete_product/<int:id>/', views.delete_product, name='delete_product'),
    path('all_orders/', views.all_orders, name='all_orders'),
    path('order_detail/<int:order_id>/', views.order_detail, name='order_detail'),
    path('accept_order/<int:order_id>/', views.accept_order, name='accept_order'),
    path('complete_order/<int:order_id>/', views.complete_order, name='complete_order'),
    path('reject_order/<int:order_id>/', views.reject_order, name='reject_order'),
    path('all_customers/', views.all_customers, name='all_customers'),
    path('customer_detail/<int:customer_id>/', views.customer_detail, name='customer_detail'),
    path('earnings/', views.earnings, name='earnings'),

]   


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
