from django.shortcuts import render, get_object_or_404, redirect
from django.http import Http404, JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from .models import Qualification, Product, Category, Manufacturer, Cart, CartItem
from django.contrib.auth.models import User
import json
import os
from django.conf import settings

def load_qualifications_from_json():
    """Загружает квалификации из JSON файла"""
    json_path = os.path.join(settings.BASE_DIR, '', 'dump.json')
    print(f"Ищем файл по пути: {json_path}")
    print(f"Файл существует: {os.path.exists(json_path)}")  
    try:
        with open(json_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
            print(f"JSON загружен, количество записей: {len(data)}") 
            specialties = []
            for item in data:
                if item.get('model') == 'data.specialty':
                    specialty = {
                        'qualification_id': item['pk'],
                        'name': item['fields']['title'],
                        'description': item['fields'].get('desc') or item['fields']['title'],
                        'code': item['fields'].get('code', ''),
                        'type': item['fields'].get('c_type', '')
                    }
                    specialties.append(specialty)
            print(f"Найдено специальностей: {len(specialties)}")
            return specialties
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Ошибка: {e}")
        return []
def spec_list(request):
    """Представление для списка квалификаций с поиском по ID"""
    all_qualifications = load_qualifications_from_json()
    search_id = request.GET.get('id', '')
    if search_id:
        try:
            search_id_int = int(search_id)
            qualifications = [q for q in all_qualifications if q['qualification_id'] == search_id_int]

        except ValueError:
            qualifications = []
    else:
        qualifications = all_qualifications[:50] 
    context = {
        'qualifications': qualifications,
        'search_id': search_id,
        'total_count': len(all_qualifications)
    }
    return render(request, 'shop/spec_list.html', context)
def spec_detail(request, qualification_id):
    """Представление для детальной информации о квалификации"""
    qualifications = load_qualifications_from_json()
    qualification = None
    for q in qualifications:
        if q['qualification_id'] == qualification_id:
            qualification = q
            break
   
    if qualification is None:
        return render(request, 'shop/spec_not_found.html', {
            'error_message': f'Квалификация с ID {qualification_id} не найдена.'
        }) 
    return render(request, 'shop/spec_detail.html', {
        'spec': qualification
    })
def home(request):
    """Представление для главной страницы"""
    return render(request, 'shop/home.html')

def about(request):
    """Представление для страницы об авторе"""
    return render(request, 'shop/about.html')

def shop_info(request):
    """Представление для страницы о магазине"""
    return render(request, 'shop/shop_info.html')


def products_list(request):
    """Представление для списка товаров с фильтрацией и поиском"""
    products = Product.objects.all()
    categories = Category.objects.all()
    manufacturers = Manufacturer.objects.all()
    
    category_id = request.GET.get('category')
    if category_id:
        products = products.filter(категория_id=category_id)
    
    manufacturer_id = request.GET.get('manufacturer')
    if manufacturer_id:
        products = products.filter(производитель_id=manufacturer_id)
    
    search = request.GET.get('search')
    if search:
        products = products.filter(название__icontains=search)
    
    sort_by = request.GET.get('sort', 'название')
    if sort_by == 'price_asc':
        products = products.order_by('цена')
    elif sort_by == 'price_desc':
        products = products.order_by('-цена')
    elif sort_by == 'name':
        products = products.order_by('название')
    else:
        products = products.order_by('название')
    
    paginator = Paginator(products, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'categories': categories,
        'manufacturers': manufacturers,
        'current_category': int(category_id) if category_id else None,
        'current_manufacturer': int(manufacturer_id) if manufacturer_id else None,
        'search_query': search or '',
        'current_sort': sort_by,
        'total_products': products.count()
    }
    
    return render(request, 'shop/products_list.html', context)


def product_detail(request, product_id):
    """Представление для детальной информации о товаре"""
    product = get_object_or_404(Product, id=product_id)
    
    context = {
        'product': product,
    }
    
    return render(request, 'shop/product_detail.html', context)


@login_required
def add_to_cart(request, product_id):
    """Добавление товара в корзину"""
    if request.method == 'POST':
        product = get_object_or_404(Product, id=product_id)
        quantity = int(request.POST.get('quantity', 1))
        
        if quantity > product.количество_на_складе:
            messages.error(request, f'Недостаточно товара на складе. Доступно: {product.количество_на_складе} шт.')
            return redirect('product_detail', product_id=product_id)
        
        cart, created = Cart.objects.get_or_create(пользователь=request.user)
        
        cart_item, created = CartItem.objects.get_or_create(
            корзина=cart,
            товар=product,
            defaults={'количество': quantity}
        )
        
        if not created:
            new_quantity = cart_item.количество + quantity
            if new_quantity > product.количество_на_складе:
                messages.error(request, f'Нельзя добавить больше {product.количество_на_складе} шт.')
                return redirect('product_detail', product_id=product_id)
            cart_item.количество = new_quantity
            cart_item.save()
            messages.success(request, f'Количество товара "{product.название}" увеличено до {new_quantity} шт.')
        else:
            messages.success(request, f'Товар "{product.название}" добавлен в корзину ({quantity} шт.)')
        
        return redirect('cart_view')
    
    return redirect('product_detail', product_id=product_id)


@login_required
def cart_view(request):
    """Просмотр корзины"""
    try:
        cart = Cart.objects.get(пользователь=request.user)
        cart_items = cart.cartitem_set.all()
    except Cart.DoesNotExist:
        cart = None
        cart_items = []
    
    context = {
        'cart': cart,
        'cart_items': cart_items,
    }
    
    return render(request, 'shop/cart.html', context)


@login_required
def remove_from_cart(request, item_id):
    """Удаление товара из корзины"""
    cart_item = get_object_or_404(CartItem, id=item_id, корзина__пользователь=request.user)
    product_name = cart_item.товар.название
    cart_item.delete()
    messages.success(request, f'Товар "{product_name}" удален из корзины')
    return redirect('cart_view')


@login_required
def update_cart_item(request, item_id):
    """Обновление количества товара в корзине"""
    if request.method == 'POST':
        cart_item = get_object_or_404(CartItem, id=item_id, корзина__пользователь=request.user)
        quantity = int(request.POST.get('quantity', 1))
        
        if quantity <= 0:
            cart_item.delete()
            messages.success(request, f'Товар "{cart_item.товар.название}" удален из корзины')
        elif quantity > cart_item.товар.количество_на_складе:
            messages.error(request, f'Недостаточно товара на складе. Доступно: {cart_item.товар.количество_на_складе} шт.')
        else:
            cart_item.количество = quantity
            cart_item.save()
            messages.success(request, f'Количество товара "{cart_item.товар.название}" обновлено')
    
    return redirect('cart_view')
