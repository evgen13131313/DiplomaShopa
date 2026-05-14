from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from decimal import Decimal
from cart.cart import Cart
from .models import Order, OrderItem, Wallet
from .forms import OrderForm


# ===== ФУНКЦИИ ДЛЯ ПОКУПАТЕЛЕЙ =====

@login_required
def checkout(request):
    cart = Cart(request)
    
    if len(cart) == 0:
        messages.warning(request, 'Ваша корзина пуста')
        return redirect('cart:cart_detail')
    
    # Получаем или создаём кошелёк пользователя
    wallet = Wallet.get_or_create_wallet(request.user)
    
    # Считаем общую сумму
    total = cart.get_total_price()
    discount = Decimal('0')
    final_amount = total
    
    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            # 1. Получаем способ оплаты ИЗ ФОРМЫ
            payment_method = form.cleaned_data['payment_method']
            
            # 2. Рассчитываем скидку ТОЛЬКО если выбран кошелёк
            if payment_method == 'wallet':
                discount = total * Decimal('0.10') # 10%
                final_amount = total - discount
            else:
                discount = Decimal('0')
                final_amount = total
            
            # 3. Создаем объект заказа
            order = form.save(commit=False)
            order.user = request.user
            order.total_amount = total
            order.discount = discount
            order.final_amount = final_amount
            order.payment_method = payment_method # Важно: записываем метод оплаты
            
            # 4. Сохраняем заказ в БД
            order.save()
            
            # 5. Создаём товары заказа
            for item in cart:
                OrderItem.objects.create(
                    order=order,
                    product=item['product'],
                    quantity=item['quantity'],
                    price=Decimal(item['price']),
                    total=Decimal(item['price']) * item['quantity']
                )
            
            # 6. Обрабатываем оплату
            if payment_method == 'wallet':
                if wallet.spend_funds(final_amount):
                    messages.success(request, f'✔ Заказ #{order.id} оплачен! Списано {final_amount} ₽')
                    order.status = 'paid'
                    order.save()
                    cart.clear()
                    return redirect('orders:order_success', order_id=order.id)
                else:
                    messages.error(request, '✘ Недостаточно средств на кошельке')
                    order.delete()
                    # Возвращаем форму с ошибкой
                    form.add_error('payment_method', 'Недостаточно средств')
            else:
                # Карта или СБП - просто сохраняем как "ожидает оплаты"
                messages.success(request, f'✔ Заказ #{order.id} создан! Ожидает оплаты')
                cart.clear()
                return redirect('orders:order_success', order_id=order.id)
        else:
            messages.error(request, 'Проверьте правильность заполнения формы')
    else:
        form = OrderForm()
    
    context = {
        'cart': cart,
        'form': form,
        'total': total,
        'discount': discount,
        'final_amount': final_amount,
        'wallet': wallet,
    }
    return render(request, 'orders/checkout.html', context)


@login_required
def order_success(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'orders/success.html', {'order': order})


@login_required
def order_history(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'orders/history.html', {'orders': orders})


@login_required
def wallet_view(request):
    wallet = Wallet.get_or_create_wallet(request.user)
    orders = Order.objects.filter(user=request.user, payment_method='wallet')[:5]
    
    context = {
        'wallet': wallet,
        'orders': orders,
    }
    return render(request, 'orders/wallet.html', context)


@login_required
def add_funds(request):
    if request.method == 'POST':
        amount = request.POST.get('amount')
        if amount:
            wallet = Wallet.get_or_create_wallet(request.user)
            wallet.add_funds(Decimal(str(amount)))
            messages.success(request, f'✔ Кошелёк пополнен на {amount} ₽')
            return redirect('orders:wallet')
    return redirect('orders:wallet')


# ===== ФУНКЦИИ ДЛЯ МЕНЕДЖЕРОВ (ПАНЕЛЬ УПРАВЛЕНИЯ) =====

def is_manager(user):
    """Проверка: является ли пользователь администратором/менеджером"""
    return user.is_staff or user.is_superuser

@login_required(login_url='login')
@user_passes_test(is_manager, login_url='home')
def manager_orders(request):
    """Панель менеджера: список всех заказов"""
    # Получаем все заказы, сортируем по дате (новые сверху)
    orders = Order.objects.all().order_by('-created_at')
    
    # Фильтрация по статусу
    status_filter = request.GET.get('status')
    if status_filter:
        orders = orders.filter(status=status_filter)
    
    context = {
        'orders': orders,
        'status_filter': status_filter,
        'status_choices': Order.STATUS_CHOICES,
    }
    return render(request, 'orders/manager_orders.html', context)

@login_required(login_url='login')
@user_passes_test(is_manager, login_url='home')
def update_status(request, order_id):
    """Изменение статуса заказа"""
    if request.method == 'POST':
        order = get_object_or_404(Order, id=order_id)
        new_status = request.POST.get('status')
        
        if new_status:
            order.status = new_status
            order.save()
            messages.success(request, f'Статус заказа #{order.id} обновлён на "{dict(Order.STATUS_CHOICES).get(new_status)}"')
            
    return redirect('orders:manager_orders')