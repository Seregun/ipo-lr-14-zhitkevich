from django.shortcuts import render, get_object_or_404, redirect
from .models import Product, Cart, CartItem, Qualification
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
import json
import os
from django.conf import settings

def home(request):
    return render(request, 'shop/home.html')

def about(request):
    return render(request, 'shop/about.html')

def shop_info(request):
    return render(request, 'shop/shop_info.html')

def product_list(request):
    products = Product.objects.all()
    return render(request, 'shop/products_list.html', {'products': products})

def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    return render(request, 'shop/product_detail.html', {'product': product})

@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart, created = Cart.objects.get_or_create(пользователь=request.user)
    
    cart_item, created = CartItem.objects.get_or_create(
        корзина=cart,
        товар=product,
        defaults={'количество': 1}
    )
    
    if not created:
        cart_item.количество += 1
        cart_item.save()
    
    return redirect('cart_view')

@login_required
def cart_view(request):
    try:
        cart = Cart.objects.get(пользователь=request.user)
        cart_items = cart.элементы.all()
    except ObjectDoesNotExist:
        cart = None
        cart_items = []
    
    return render(request, 'shop/cart.html', {
        'cart': cart,
        'cart_items': cart_items
    })

@login_required
def remove_from_cart(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id, корзина__пользователь=request.user)
    cart_item.delete()
    return redirect('cart_view')

@login_required
def update_cart_item(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id, корзина__пользователь=request.user)
    quantity = int(request.POST.get('quantity', 1))
    
    if 1 <= quantity <= cart_item.товар.количество_на_складе:
        cart_item.количество = quantity
        cart_item.save()
    
    return redirect('cart_view')

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