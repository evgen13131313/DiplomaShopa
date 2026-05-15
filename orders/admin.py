import csv
from django.contrib import admin
from django.http import HttpResponse
from .models import Order, OrderItem, Wallet, ActionLog

# ===== Функция экспорта в CSV =====
def export_orders_to_csv(modeladmin, request, queryset):
    # Создаем HTTP-ответ с типом CSV
    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = 'attachment; filename="orders_export.csv"'
    
    # Добавляем BOM для корректного отображения кириллицы в Excel
    response.write('\ufeff')
    
    writer = csv.writer(response)
    
    # Заголовки таблицы
    writer.writerow([
        'ID заказа', 'Пользователь', 'Имя', 'Фамилия', 'Email', 'Телефон',
        'Город', 'Адрес', 'Способ оплаты', 'Сумма', 'Скидка', 'Итого', 'Статус', 'Дата создания'
    ])
    
    # Записываем данные по каждому выбранному заказу
    for order in queryset:
        writer.writerow([
            order.id,
            order.user.username if order.user else 'Гость',
            order.first_name,
            order.last_name,
            order.email,
            order.phone,
            order.city,
            order.address,
            order.get_payment_method_display(),
            order.total_amount,
            order.discount,
            order.final_amount,
            order.get_status_display(),
            order.created_at.strftime('%d.%m.%Y %H:%M')
        ])
        
    return response

# Название кнопки в админке
export_orders_to_csv.short_description = "📥 Скачать выбранные заказы в CSV"


# ===== Регистрация моделей =====

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'first_name', 'last_name', 'total_amount', 'status', 'created_at']
    list_filter = ['status', 'created_at', 'payment_method']
    search_fields = ['user__username', 'email', 'first_name', 'last_name']
    list_editable = ['status']
    readonly_fields = ['created_at', 'updated_at']
    actions = [export_orders_to_csv]  # Подключаем кнопку экспорта

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['id', 'order', 'product', 'quantity', 'price', 'total']
    search_fields = ['order__id', 'product__name']

@admin.register(Wallet)
class WalletAdmin(admin.ModelAdmin):
    list_display = ['user', 'balance', 'created_at']
    search_fields = ['user__username']

@admin.register(ActionLog)
class ActionLogAdmin(admin.ModelAdmin):
    list_display = ['timestamp', 'user', 'action', 'object_type', 'object_id']
    list_filter = ['action', 'timestamp']
    search_fields = ['user__username', 'description']
    readonly_fields = ['timestamp']