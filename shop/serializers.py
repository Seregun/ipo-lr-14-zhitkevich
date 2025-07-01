from rest_framework import serializers
from .models import Product, Category, Manufacturer, Cart, CartItem

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'название', 'описание']

class ManufacturerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Manufacturer
        fields = ['id', 'название', 'страна', 'описание']

class ProductSerializer(serializers.ModelSerializer):
    категория = CategorySerializer(read_only=True)
    производитель = ManufacturerSerializer(read_only=True)
    
    class Meta:
        model = Product
        fields = '__all__'

class CartItemSerializer(serializers.ModelSerializer):
    товар = ProductSerializer(read_only=True)
    
    class Meta:
        model = CartItem
        fields = ['id', 'товар', 'количество', 'добавлен']

class CartSerializer(serializers.ModelSerializer):
    элементы = CartItemSerializer(many=True, read_only=True)
    
    class Meta:
        model = Cart
        fields = ['id', 'дата_создания', 'элементы']