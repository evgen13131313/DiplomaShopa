from django import forms
from .models import Order

class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['first_name', 'last_name', 'email', 'phone', 'address', 'city', 'pickup_point', 'payment_method']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Имя'}),
            'last_name': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Фамилия'}),
            'email': forms.EmailInput(attrs={'class': 'form-input', 'placeholder': 'Email'}),
            'phone': forms.TextInput(attrs={'class': 'form-input', 'placeholder': '+7 (___) ___-__-__'}),
            'address': forms.Textarea(attrs={'class': 'form-input', 'placeholder': 'Адрес доставки', 'rows': 3}),
            'city': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Город'}),
            'pickup_point': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Пункт выдачи (необязательно)'}),
            'payment_method': forms.Select(attrs={'class': 'form-input'}),
        }