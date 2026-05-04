from django.db import models
from django.contrib.auth.models import User
from shop.models import Product
from decimal import Decimal

class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Ожидает оплаты'),
        ('paid', 'Оплачено'),
        ('shipped', 'Отправлено'),
        ('delivered', 'Доставлено'),
        ('cancelled', 'Отменено'),
    ]
    
    PAYMENT_CHOICES = [
        ('card', 'Банковская карта'),
        ('sbp', 'СБП (Система быстрых платежей)'),
        ('wallet', 'OnlineSale Wallet'),
    ]
    
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='orders',
        verbose_name='Пользователь'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')
    
    # Данные доставки
    first_name = models.CharField(max_length=50, verbose_name='Имя')
    last_name = models.CharField(max_length=50, verbose_name='Фамилия')
    email = models.EmailField(verbose_name='Email')
    phone = models.CharField(max_length=20, verbose_name='Телефон')
    address = models.TextField(verbose_name='Адрес доставки')
    city = models.CharField(max_length=100, verbose_name='Город')
    pickup_point = models.CharField(max_length=200, blank=True, verbose_name='Пункт выдачи')
    
    # Оплата
    payment_method = models.CharField(
        max_length=20, 
        choices=PAYMENT_CHOICES, 
        verbose_name='Способ оплаты'
    )
    total_amount = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        verbose_name='Сумма заказа'
    )
    discount = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0, 
        verbose_name='Скидка'
    )
    final_amount = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        verbose_name='Итоговая сумма'
    )
    
    # Статус
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='pending',
        verbose_name='Статус'
    )
    
    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'
        ordering = ['-created_at']
    
    def __str__(self):
        return f'Заказ #{self.id} - {self.user.username}'


class OrderItem(models.Model):
    order = models.ForeignKey(
        Order, 
        on_delete=models.CASCADE, 
        related_name='items',
        verbose_name='Заказ'
    )
    product = models.ForeignKey(
        Product, 
        on_delete=models.CASCADE, 
        verbose_name='Товар'
    )
    quantity = models.PositiveIntegerField(default=1, verbose_name='Количество')
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Цена')
    total = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Сумма')
    
    class Meta:
        verbose_name = 'Товар заказа'
        verbose_name_plural = 'Товары заказа'
    
    def __str__(self):
        return f'{self.product.name} x {self.quantity}'
    
    def save(self, *args, **kwargs):
        self.total = self.price * self.quantity
        super().save(*args, **kwargs)


class Wallet(models.Model):
    """OnlineSale Wallet - внутренний кошелёк пользователя"""
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE, 
        related_name='wallet',
        verbose_name='Пользователь'
    )
    balance = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0, 
        verbose_name='Баланс'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    
    class Meta:
        verbose_name = 'Кошелёк'
        verbose_name_plural = 'Кошельки'
    
    def __str__(self):
        return f'Кошелёк {self.user.username} - {self.balance} ₽'
    
    @classmethod
    def get_or_create_wallet(cls, user):
        wallet, created = cls.objects.get_or_create(user=user)
        return wallet
    
    def add_funds(self, amount):
        """Пополнить кошелёк"""
        self.balance += Decimal(str(amount))
        self.save()
    
    def spend_funds(self, amount):
        """Списать средства"""
        if self.balance >= Decimal(str(amount)):
            self.balance -= Decimal(str(amount))
            self.save()
            return True
        return False