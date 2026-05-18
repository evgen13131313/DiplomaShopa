from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import get_user_model
from .serializers import ProductSerializer, OrderSerializer
from shop.models import Product
from orders.models import Order, OrderItem

# User = get_user_model()

# 1. Получение списка товаров (GET)
class ProductListAPI(generics.ListAPIView):
    queryset = Product.objects.all().order_by('-id')
    serializer_class = ProductSerializer
    permission_classes = [permissions.AllowAny]

# 2. Создание заказа через API (POST)
# Принимает JSON: {"products": [{"id": 1, "quantity": 2}]}
class OrderCreateAPI(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        user = request.user
        products_data = request.data.get('products')

        if not products_data:
            return Response({'error': 'Список товаров пуст'}, status=400)

        # Создаем заказ (заглушка с фиктивной суммой для примера, 
        # в реальности нужно считать сумму на сервере)
        order = Order.objects.create(
            user=user,
            total_amount=0, # Упрощение для API
            final_amount=0,
            first_name=user.first_name or "API",
            last_name=user.last_name or "User",
            email=user.email,
            phone="000000000",
            address="API Delivery",
            city="Moscow",
            payment_method='card'
        )

        total = 0
        for item in products_data:
            try:
                product = Product.objects.get(id=item['id'])
                quantity = item.get('quantity', 1)
                
                OrderItem.objects.create(
                    order=order,
                    product=product,
                    quantity=quantity,
                    price=product.price,
                    total=product.price * quantity
                )
                total += product.price * quantity
            except Product.DoesNotExist:
                continue

        order.total_amount = total
        order.final_amount = total
        order.save()

        serializer = OrderSerializer(order)
        return Response(serializer.data, status=201)