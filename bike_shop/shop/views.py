from django.shortcuts import render

def home(request):
    """Представление для главной страницы"""
    return render(request, 'shop/home.html')

def about(request):
    """Представление для страницы об авторе"""
    return render(request, 'shop/about.html')

def shop_info(request):
    """Представление для страницы о магазине"""
    return render(request, 'shop/shop_info.html')
