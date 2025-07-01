from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from .views import (
    ProductViewSet,
    CategoryViewSet,
    ManufacturerViewSet,
    CartViewSet,
    CartItemViewSet
)

router = DefaultRouter()
router.register(r'products', ProductViewSet, basename='product')
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'manufacturers', ManufacturerViewSet, basename='manufacturer')
router.register(r'carts', CartViewSet, basename='cart')
router.register(r'cartitems', CartItemViewSet, basename='cartitem')

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('shop/', views.shop_info, name='shop_info'),
    path('specializations/', views.spec_list, name='spec_list'),
    path('specializations/<int:qualification_id>/', views.spec_detail, name='spec_detail'),
    
    path('products/', views.product_list, name='product_list'), 
    path('products/<int:product_id>/', views.product_detail, name='product_detail'),
    path('cart/', views.cart_view, name='cart'), 
    path('add-to-cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/remove/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('cart/update/<int:item_id>/', views.update_cart_item, name='update_cart_item'),
    path('checkout/', views.checkout, name='checkout'),
    
    path('api/', include(router.urls)),
]