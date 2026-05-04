from cart.cart import Cart
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Product
from .forms import RegisterForm, LoginForm
from cart.cart import Cart

def index(request):
    products = Product.objects.all()
    cart = Cart(request)
    context = {
        'products': products,
        'title': 'Главная страница магазина',
        'cart_length': len(cart),
    }
    return render(request, 'shop/index.html', context)


def index(request):
    """Главная страница - каталог товаров"""
    products = Product.objects.all()
    context = {
        'products': products,
        'title': 'Главная страница магазина'
    }
    return render(request, 'shop/index.html', context)

def register(request):
    """Регистрация нового пользователя"""
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  
            messages.success(request, f'Регистрация успешна! Добро пожаловать, {user.username}!')
            return redirect('home')
        else:
            messages.error(request, 'Ошибка регистрации. Проверьте данные.')
    else:
        form = RegisterForm()
    

def user_login(request):
    """Вход пользователя"""
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            
            if user is not None:
                login(request, user)
                messages.success(request, f'С возвращением, {username}!')
                return redirect('home')
            else:
                messages.error(request, 'Неверный логин или пароль.')
        else:
            messages.error(request, 'Ошибка входа. Проверьте данные.')
    else:
        form = LoginForm()
    
    return render(request, 'shop/login.html', {'form': form, 'title': 'Вход'})

def user_logout(request):
    """Выход пользователя"""
    logout(request)
    messages.info(request, 'Вы вышли из системы.')
    return redirect('home')

@login_required(login_url='login')
def profile(request):
    """Личный кабинет пользователя"""
    return render(request, 'shop/profile.html', {'title': 'Личный кабинет'})