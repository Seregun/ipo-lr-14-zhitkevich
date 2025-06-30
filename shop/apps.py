from django.apps import AppConfig
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model

class ShopConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'shop'
    
    def ready(self):
        from .models import Cart
        User = get_user_model()
        
        @receiver(post_save, sender=User)
        def create_user_cart(sender, instance, created, **kwargs):
            if created:
                Cart.objects.create(пользователь=instance)