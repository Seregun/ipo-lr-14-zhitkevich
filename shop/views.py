from .models import Category, Manufacturer, Product, Cart, CartItem
from django.shortcuts import render, get_object_or_404, redirect
from .models import Product, Cart, CartItem, Qualification
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
import json
import os
from django.conf import settings
from django.db.models import Q
from django.core.paginator import Paginator
from django.contrib import messages
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect


def home(request):
    return render(request, 'shop/home.html')

def about(request):
    return render(request, 'shop/about.html')

def shop_info(request):
    return render(request, 'shop/shop_info.html')

def product_list(request):
    products = Product.objects.all()
    
    search_query = request.GET.get('search', '')
    category_id = request.GET.get('category')
    manufacturer_id = request.GET.get('manufacturer')
    sort = request.GET.get('sort', 'name')
    
    if search_query:
        products = products.filter(
            Q(название__icontains=search_query) | 
            Q(описание__icontains=search_query)
        )
    
    if category_id:
        products = products.filter(категория_id=category_id)
    
    if manufacturer_id:
        products = products.filter(производитель_id=manufacturer_id)
    
    if sort == 'price_asc':
        products = products.order_by('цена')
    elif sort == 'price_desc':
        products = products.order_by('-цена')
    else:
        products = products.order_by('название')
    
    paginator = Paginator(products, 9)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'categories': Category.objects.all(),
        'manufacturers': Manufacturer.objects.all(),
        'current_category': int(category_id) if category_id else None,
        'current_manufacturer': int(manufacturer_id) if manufacturer_id else None,
        'current_sort': sort,
        'search_query': search_query,
        'total_products': products.count()
    }
    
    return render(request, 'shop/product_list.html', context)

def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    return render(request, 'shop/product_detail.html', {'product': product})

def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    quantity = int(request.POST.get('quantity', 1))
    
    cart, created = Cart.objects.get_or_create(пользователь=request.user)
    
    cart_item, item_created = CartItem.objects.get_or_create(
        корзина=cart,
        товар=product,
        defaults={'количество': quantity}
    )
    
    if not item_created:
        cart_item.количество += quantity
        cart_item.save()
    
    messages.success(request, f'Товар "{product.название}" добавлен в корзину!')
    return redirect('shop:cart')  

@login_required
def cart_view(request):
    try:
        cart = Cart.objects.get(пользователь=request.user)
        cart_items = cart.элементы.all()
        total_price = cart.общая_стоимость()
    except ObjectDoesNotExist:
        cart = None
        cart_items = []
        total_price = 0
    
    return render(request, 'shop/cart.html', {
        'cart': cart,
        'cart_items': cart_items,
        'total_price': total_price
    })

@login_required
def remove_from_cart(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id, корзина__пользователь=request.user)
    product_name = cart_item.товар.название
    cart_item.delete()
    messages.success(request, f'Товар "{product_name}" удален из корзины')
    return redirect('cart_view')

@login_required
def update_cart_item(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id, корзина__пользователь=request.user)
    quantity = int(request.POST.get('quantity', 1))
    
    if 1 <= quantity <= cart_item.товар.количество_на_складе:
        cart_item.количество = quantity
        cart_item.save()
        messages.success(request, f'Количество товара "{cart_item.товар.название}" обновлено')
    else:
        messages.error(request, f'Недопустимое количество. Максимум: {cart_item.товар.количество_на_складе}')
    
    return redirect('cart_view')

@login_required
def profile_view(request):
    return render(request, 'shop/profile.html')

def load_qualifications_from_json():
    json_path = os.path.join(settings.BASE_DIR, 'dump.json')
    try:
        with open(json_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
            return [
                {
                    'qualification_id': item['pk'],
                    'name': item['fields']['title'],
                    'description': item['fields'].get('desc', ''),
                    'code': item['fields'].get('code', ''),
                    'type': item['fields'].get('c_type', '')
                }
                for item in data if item.get('model') == 'data.specialty'
            ]
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def spec_list(request):
    qualifications = load_qualifications_from_json()
    search_id = request.GET.get('id', '')
    
    if search_id:
        try:
            search_id = int(search_id)
            qualifications = [q for q in qualifications if q['qualification_id'] == search_id]
        except ValueError:
            qualifications = []
    
    return render(request, 'shop/spec_list.html', {
        'qualifications': qualifications[:50],
        'search_id': search_id,
        'total_count': len(qualifications)
    })

def spec_detail(request, qualification_id):
    qualifications = load_qualifications_from_json()
    qualification = next((q for q in qualifications if q['qualification_id'] == qualification_id), None)
    
    if not qualification:
        return render(request, 'shop/spec_not_found.html')
    
    return render(request, 'shop/spec_detail.html', {'spec': qualification})

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            Cart.objects.get_or_create(пользователь=user)
            return redirect('home')
    else:
        form = UserCreationForm()
    return render(request, 'shop/register.html', {'form': form})