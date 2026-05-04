from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from shop.models import Product
from .cart import Cart
from .forms import CartAddProductForm

@require_POST
def cart_add(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    form = CartAddProductForm(request.POST)
    
    if form.is_valid():
        cd = form.cleaned_data
        cart.add(product=product, quantity=cd['quantity'])
    
    return redirect('cart:cart_detail')

@require_POST
def cart_remove(request, product_id):
    cart = Cart(request)
    cart.remove(product_id)
    return redirect('cart:cart_detail')

def cart_detail(request):
    cart = Cart(request)
    for item in cart:
        item['update_quantity_form'] = CartAddProductForm(
            initial={'quantity': item['quantity'], 'update': True}
        )
    
    # Применяем скидку для OnlineSale кошелька
    total_with_discount = cart.get_total_price()
    discount_percent = 0
    
    if request.GET.get('payment') == 'wallet':
        discount_percent = 10  # 10% скидка при оплате кошельком
        total_with_discount = total_with_discount * Decimal('0.9')
    
    context = {
        'cart': cart,
        'total_with_discount': total_with_discount,
        'discount_percent': discount_percent,
    }
    return render(request, 'cart/detail.html', context)