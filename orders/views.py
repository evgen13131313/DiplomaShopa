from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from decimal import Decimal
from cart.cart import Cart
from .models import Order, OrderItem, Wallet
from .forms import OrderForm

@login_required
def checkout(request):
    cart = Cart(request)
    
    if len(cart) == 0:  # ← ИСПРАВЛЕНО: len(cart) вместо cart|length
        messages.warning(request, 'Ваша корзина пуста')
        return redirect('cart:cart_detail')
    
    # Получаем или создаём кошелёк пользователя
    wallet = Wallet.get_or_create_wallet(request.user)
    
    # Считаем сумму
    total = cart.get_total_price()
    discount = Decimal('0')
    discount_percent = 0
    
    # Проверяем, выбран ли OnlineSale Wallet
    if request.method == 'POST':
        payment_method = request.POST.get('payment_method')
        if payment_method == 'wallet':
            discount_percent = 10
            discount = total * Decimal('0.1')
    
    final_amount = total - discount
    
    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            order.user = request.user
            order.total_amount = total
            order.discount = discount
            order.final_amount = final_amount
            
            # Сохраняем заказ
            order.save()
            
            # Создаём товары заказа
            for item in cart:
                OrderItem.objects.create(
                    order=order,
                    product=item['product'],
                    quantity=item['quantity'],
                    price=Decimal(item['price']),
                    total=Decimal(item['price']) * item['quantity']
                )
            
            # Обрабатываем оплату
            payment_method = form.cleaned_data['payment_method']
            
            if payment_method == 'wallet':
                # Списываем с кошелька
                if wallet.spend_funds(final_amount):
                    messages.success(request, f'✅ Заказ #{order.id} оплачен! Списано {final_amount} ₽ с OnlineSale Wallet')
                    order.status = 'paid'
                    order.save()
                    cart.clear()
                    return redirect('orders:order_success', order_id=order.id)
                else:
                    messages.error(request, '❌ Недостаточно средств на кошельке')
                    order.delete()
                    return redirect('orders:checkout')
            else:
                # Карта или СБП - помечаем как ожидает оплаты
                messages.success(request, f'✅ Заказ #{order.id} создан! Ожидает оплаты')
                order.save()
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
        'discount_percent': discount_percent,
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
            messages.success(request, f'✅ Кошелёк пополнен на {amount} ₽')
            return redirect('orders:wallet')
    return redirect('orders:wallet')