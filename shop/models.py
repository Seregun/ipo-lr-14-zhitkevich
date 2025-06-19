from django.db import models
from django.core.validators import MinValueValidator
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from decimal import Decimal


class Category(models.Model):
    """Модель категории товара"""
    название = models.CharField(max_length=100)
    описание = models.TextField(blank=True)
    
    def __str__(self):
        return str(self.название)


class Manufacturer(models.Model):
    """Модель производителя"""  
    название = models.CharField(max_length=100)
    страна = models.CharField(max_length=100)
    описание = models.TextField(blank=True)
    
    def __str__(self):
        return str(self.название)


class Product(models.Model):
    """Модель товара"""
    название = models.CharField(max_length=200)
    описание = models.TextField()
    фото_товара = models.ImageField(upload_to='products/', blank=True, null=True)
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
    
    def save(self, *args, **kwargs):
        self.full_clean() 
        super().save(*args, **kwargs)
    
    def __str__(self):
        return str(self.название)


class Cart(models.Model):
    """Модель корзины"""
    пользователь = models.OneToOneField(User, on_delete=models.CASCADE)
    дата_создания = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Корзина пользователя {self.пользователь.username}"
    
    def общая_стоимость(self):
        """Вычисляет общую стоимость всех элементов в корзине"""
        total = sum(item.стоимость_элемента() for item in self.cartitem_set.all())
        return total


class CartItem(models.Model):
    """Модель элемента корзины"""
    корзина = models.ForeignKey(Cart, on_delete=models.CASCADE)
    товар = models.ForeignKey(Product, on_delete=models.CASCADE)
    количество = models.PositiveIntegerField()
    
    def __str__(self):
        return f"{self.товар.название} ({self.количество} шт.)"
    
    def стоимость_элемента(self):
        """Возвращает стоимость данного элемента корзины"""
        return self.товар.цена * self.количество
    
    def clean(self):
        """Валидация: количество не должно превышать количество на складе"""
        if self.количество > self.товар.количество_на_складе:
            raise ValidationError(
                f'Количество {self.количество} превышает доступное на складе ({self.товар.количество_на_складе})'
            )
    
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


class Qualification(models.Model):
    qualification_id = models.IntegerField()
    name = models.CharField(max_length=200, default='')
    description = models.TextField(default='')
    
    def __str__(self):
        return str(self.name)
