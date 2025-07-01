from django.apps import AppConfig

class ShopConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'shop'
    
    def ready(self):
        from .models import create_user_cart
        from django.db.models.signals import post_save
        from django.contrib.auth import get_user_model
        
        post_save.connect(create_user_cart, sender=get_user_model())