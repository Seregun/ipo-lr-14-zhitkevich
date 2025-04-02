from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('shop/', views.shop_info, name='shop_info'),
    path('spec/', views.spec_list, name='spec_list'),
    path('spec/<int:spec_id>/', views.spec_detail, name='spec_detail'),
]