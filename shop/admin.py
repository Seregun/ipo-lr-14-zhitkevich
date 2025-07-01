from django.contrib import admin
from .models import Category, Manufacturer, Product, Cart, CartItem, Order, OrderItem

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('название', 'описание')
    search_fields = ('название',)

@admin.register(Manufacturer)
class ManufacturerAdmin(admin.ModelAdmin):
    list_display = ('название', 'страна', 'описание')
    search_fields = ('название', 'страна')
    list_filter = ('страна',)

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('название', 'категория', 'производитель', 'цена', 'количество_на_складе')
    search_fields = ('название', 'описание')
    list_filter = ('категория', 'производитель')
    list_editable = ('цена', 'количество_на_складе')

class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0
    readonly_fields = ('добавлен',)
    fields = ('товар', 'количество', 'добавлен')

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('пользователь', 'дата_создания')
    readonly_fields = ('дата_создания',)
    inlines = [CartItemInline]

@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('корзина', 'товар', 'количество', 'добавлен')
    list_filter = ('добавлен',)
    readonly_fields = ('добавлен',)

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'пользователь', 'дата_создания', 'total_price')
    readonly_fields = ('дата_создания', 'total_price')
    list_filter = ('дата_создания',)

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('заказ', 'товар', 'количество', 'цена')
    list_filter = ('заказ',)