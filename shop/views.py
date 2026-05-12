from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.core.paginator import Paginator
from .models import Product, Category
from .forms import RegisterForm, LoginForm
from cart.cart import Cart

def index(request):
    """Главная страница - каталог товаров с фильтрацией и поиском"""
    
    # Базовый запрос с оптимизацией
    products = Product.objects.select_related('category').all()
    
    # === ФИЛЬТРАЦИЯ И ПОИСК ===
    
    # Поиск по названию и описанию
    search_query = request.GET.get('search', '')
    if search_query:
        products = products.filter(
            Q(name__icontains=search_query) | 
            Q(description__icontains=search_query)
        )
    
    # Фильтр по категории
    category_id = request.GET.get('category', '')
    if category_id:
        products = products.filter(category_id=category_id)
    
    # Фильтр по цене (мин)
    min_price = request.GET.get('min_price', '')
    if min_price:
        products = products.filter(price__gte=min_price)
    
    # Фильтр по цене (макс)
    max_price = request.GET.get('max_price', '')
    if max_price:
        products = products.filter(price__lte=max_price)
    
    # === ПАГИНАЦИЯ ===
    paginator = Paginator(products, 12)  # 12 товаров на страницу
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # === КОНТЕКСТ ===
    cart = Cart(request)
    categories = Category.objects.all()
    
    context = {
        'products': page_obj,
        'categories': categories,
        'title': 'Каталог товаров',
        'cart_length': len(cart),
        # Сохраняем параметры для пагинации
        'search_query': search_query,
        'category_id': category_id,
        'min_price': min_price,
        'max_price': max_price,
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
    
    return render(request, 'shop/register.html', {'form': form, 'title': 'Регистрация'})


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


def checkout(request):
    """Заглушка для оформления заказа"""
    return render(request, 'shop/checkout.html', {'title': 'Оформление заказа'})