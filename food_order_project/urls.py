from django.contrib import admin
from django.urls import path

from core.views import (
    home_view,
    restaurant_list_view,
    menu_detail_view,
    cart_view,
    checkout_view,
    order_tracking_view,
    login_view,
    register_view,
    logout_view,
    dashboard_view,
    dashboard_orders_view,
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home_view, name='home'),
    path('restaurants/', restaurant_list_view, name='restaurant_list'),
    path('restaurants/<int:pk>/menu/', menu_detail_view, name='menu_detail'),
    path('cart/', cart_view, name='cart'),
    path('checkout/', checkout_view, name='checkout'),
    path('orders/<int:pk>/tracking/', order_tracking_view, name='order_tracking'),
    path('login/', login_view, name='login'),
    path('register/', register_view, name='register'),
    path('logout/', logout_view, name='logout'),
    path('dashboard/', dashboard_view, name='dashboard'),
    path('dashboard/orders/', dashboard_orders_view, name='dashboard_orders'),
]
