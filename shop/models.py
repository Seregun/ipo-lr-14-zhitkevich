from django.db import models
from django.core.validators import MinValueValidator
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from decimal import Decimal
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model

User = get_user_model()

@receiver(post_save, sender=User)
def create_user_cart(sender, instance, created, **kwargs):
    if created:
        Cart.objects.create(пользователь=instance)
        
class Category(models.Model):
    название = models.CharField(max_length=100)
    описание = models.TextField(blank=True)
    
    class Meta:
        verbose_name = "Категория товара"
        verbose_name_plural = "Категории товаров"
    
    def __str__(self):
        return self.название

class Manufacturer(models.Model):
    название = models.CharField(max_length=100)
    страна = models.CharField(max_length=100)
    описание = models.TextField(blank=True)
    
    class Meta:
        verbose_name = "Производитель"
        verbose_name_plural = "Производители"
    
    def __str__(self):
        return self.название

class Product(models.Model):
    название = models.CharField(max_length=200)
    описание = models.TextField()
    фото_товара = models.ImageField(upload_to='product/', blank=True, null=True)
    цена = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    количество_на_складе = models.IntegerField(
        validators=[MinValueValidator(0)]
    )
    категория = models.ForeignKey(Category, on_delete=models.CASCADE)
    производитель = models.ForeignKey(Manufacturer, on_delete=models.CASCADE)
    
    class Meta:
        verbose_name = "Товар"
        verbose_name_plural = "Товары"
    
    def save(self, *args, **kwargs):
        self.full_clean() 
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.название

class Cart(models.Model):
    пользователь = models.OneToOneField(
        User, 
        on_delete=models.CASCADE,
        verbose_name="Пользователь",
        related_name="корзина"
    )
    дата_создания = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата создания"
    )
    
    class Meta:
        verbose_name = "Корзина"
        verbose_name_plural = "Корзины"
        db_table = "shop_cart"
    
    def __str__(self):
        return f"Корзина пользователя {self.пользователь.username}"
    
    def общая_стоимость(self):
        return sum(item.стоимость_элемента() for item in self.элементы.all())
    
    def количество_товаров(self):
        return sum(item.количество for item in self.элементы.all())

class CartItem(models.Model):
    корзина = models.ForeignKey(
        Cart,
        on_delete=models.CASCADE,
        verbose_name="Корзина",
        related_name="элементы"
    )
    товар = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        verbose_name="Товар"
    )
    количество = models.PositiveIntegerField(
        verbose_name="Количество"
    )
    добавлен = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата добавления"
    )
    
    class Meta:
        verbose_name = "Элемент корзины"
        verbose_name_plural = "Элементы корзины"
        unique_together = ('корзина', 'товар')
    
    def __str__(self):
        return f"{self.товар.название} ({self.количество} шт.)"
    
    def стоимость_элемента(self):
        return self.товар.цена * self.количество
    
    def clean(self):
        if self.товар and self.количество > self.товар.количество_на_складе:
            raise ValidationError(
                f"Количество не должно превышать остаток на складе ({self.товар.количество_на_складе})"
            )
    
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

class Qualification(models.Model):
    qualification_id = models.IntegerField(unique=True)
    name = models.CharField(max_length=200, default='')
    description = models.TextField(default='')
    
    class Meta:
        verbose_name = "Квалификация"
        verbose_name_plural = "Квалификации"
    
    def __str__(self):
        return str(self.name)

class Order(models.Model):
    пользователь = models.ForeignKey(
        User, 
        on_delete=models.CASCADE,
        verbose_name="Пользователь"
    )
    дата_создания = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата создания"
    )
    delivery_address = models.TextField(
        verbose_name="Адрес доставки"
    )
    phone_number = models.CharField(
        max_length=20,
        verbose_name="Телефон"
    )
    email = models.EmailField(
        verbose_name="Email"
    )
    notes = models.TextField(
        blank=True,
        null=True,
        verbose_name="Примечания"
    )
    total_price = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        verbose_name="Общая стоимость"
    )
    
    class Meta:
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"
        ordering = ['-дата_создания']
    
    def __str__(self):
        return f"Заказ №{self.id} от {self.дата_создания.strftime('%d.%m.%Y')}"

class OrderItem(models.Model):
    заказ = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        verbose_name="Заказ",
        related_name="элементы"
    )
    товар = models.ForeignKey(
        Product,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name="Товар"
    )
    количество = models.PositiveIntegerField(
        verbose_name="Количество"
    )
    цена = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        verbose_name="Цена за единицу"
    )
    
    class Meta:
        verbose_name = "Элемент заказа"
        verbose_name_plural = "Элементы заказа"
    
    def __str__(self):
        return f"{self.товар.название} (x{self.количество})"
    
from django.apps import apps
apps.all_models['shop'] = {
    'category': Category,
    'manufacturer': Manufacturer,
    'product': Product,
    'cart': Cart,
    'cartitem': CartItem,
    'qualification': Qualification,
    'order': Order,
    'orderitem': OrderItem,
}
