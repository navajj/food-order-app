from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.shortcuts import render, redirect, get_object_or_404

from .models import Customer, Restaurant, MenuItem, Order


def home_view(request):
    return redirect('restaurant_list')


def restaurant_list_view(request):
    restaurants = Restaurant.objects.filter(is_active=True)
    return render(request, 'menu/restaurant_list.html', {'restaurants': restaurants})


def menu_detail_view(request, pk):
    restaurant = get_object_or_404(Restaurant, pk=pk)
    menu_items = restaurant.menu_items.filter(is_available=True)
    return render(request, 'menu/menu_detail.html', {
        'restaurant': restaurant,
        'menu_items': menu_items,
    })


@login_required
def cart_view(request):
    return render(request, 'orders/cart.html')


@login_required
def checkout_view(request):
    return render(request, 'orders/checkout.html')


@login_required
def order_tracking_view(request, pk):
    order = get_object_or_404(Order, pk=pk)
    return render(request, 'orders/tracking.html', {'order': order})


@staff_member_required
def dashboard_view(request):
    recent_orders = Order.objects.select_related('customer', 'restaurant').order_by('-created_at')[:10]
    return render(request, 'dashboard/index.html', {'recent_orders': recent_orders})


@staff_member_required
def dashboard_orders_view(request):
    orders = Order.objects.select_related('customer', 'restaurant').all()
    return render(request, 'dashboard/order_management.html', {'orders': orders})


def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('restaurant_list')
    else:
        form = AuthenticationForm()
    return render(request, 'auth/login.html', {'form': form})


def register_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            Customer.objects.create(user=user)
            login(request, user)
            return redirect('restaurant_list')
    else:
        form = UserCreationForm()
    return render(request, 'auth/register.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('login')
