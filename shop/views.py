from django.core.mail import EmailMessage, send_mail
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .models import Category, Manufacturer, Product, Cart, CartItem
from .models import Product, Cart, CartItem, Qualification, Order, OrderItem
from django.core.exceptions import ObjectDoesNotExist
import json
import os
from django.conf import settings
from django.db.models import Q
from django.core.paginator import Paginator
from django.contrib import messages
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
import openpyxl
from io import BytesIO
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.http import HttpResponse
from django.contrib import messages
from django.conf import settings
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import Product, Category, Manufacturer, Cart, CartItem
from .serializers import (
    ProductSerializer, 
    CategorySerializer, 
    ManufacturerSerializer,
    CartSerializer,
    CartItemSerializer
)

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated]

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]

class ManufacturerViewSet(viewsets.ModelViewSet):
    queryset = Manufacturer.objects.all()
    serializer_class = ManufacturerSerializer
    permission_classes = [IsAuthenticated]

class CartViewSet(viewsets.ModelViewSet):
    serializer_class = CartSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Cart.objects.filter(пользователь=self.request.user)
    
    queryset = Cart.objects.none()

class CartItemViewSet(viewsets.ModelViewSet):
    serializer_class = CartItemSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return CartItem.objects.filter(корзина__пользователь=self.request.user)
    
    queryset = CartItem.objects.none()

def home(request):
    return render(request, 'shop/home.html')

def about(request):
    return render(request, 'shop/about.html')

def shop_info(request):
    return render(request, 'shop/shop_info.html')

def product_list(request):
    from .models import Product, Category, Manufacturer
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
    from .models import Product
    product = get_object_or_404(Product, id=product_id)
    return render(request, 'shop/product_detail.html', {'product': product})

def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    quantity = int(request.POST.get('quantity', 1))
    
    if not request.user.is_authenticated:
        cart = request.session.get('cart', {})
        cart[str(product_id)] = cart.get(str(product_id), 0) + quantity
        request.session['cart'] = cart
        messages.success(request, f'Товар "{product.название}" добавлен в корзину!')
        return redirect('product_detail', product_id=product_id)
    
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
    return redirect('product_detail', product_id=product_id)

@login_required
def cart_view(request):
    cart_items = []
    total_price = 0
    
    if not request.user.is_authenticated:
        cart = request.session.get('cart', {})
        for product_id, quantity in cart.items():
            try:
                product = Product.objects.get(id=product_id)
                item_total = product.цена * quantity
                total_price += item_total
                cart_items.append({
                    'id': product_id,
                    'product': product,
                    'quantity': quantity,
                    'total_price': item_total
                })
            except Product.DoesNotExist:
                if product_id in cart:
                    del cart[product_id]
                    request.session['cart'] = cart
    
    else:
        try:
            cart = Cart.objects.get(пользователь=request.user)
            for item in cart.элементы.all():
                item_total = item.стоимость_элемента()
                total_price += item_total
                cart_items.append({
                    'id': item.id,
                    'product': item.товар,
                    'quantity': item.количество,
                    'total_price': item_total
                })
        except Cart.DoesNotExist:
            pass
    
    return render(request, 'shop/cart.html', {
        'cart_items': cart_items,
        'total_price': total_price
    })

@login_required
def remove_from_cart(request, item_id):
    if not request.user.is_authenticated:
        cart = request.session.get('cart', {})
        if str(item_id) in cart:
            del cart[str(item_id)]
            request.session['cart'] = cart
        return redirect('cart')
    
    cart_item = get_object_or_404(CartItem, id=item_id, корзина__пользователь=request.user)
    product_name = cart_item.товар.название
    cart_item.delete()
    messages.success(request, f'Товар "{product_name}" удален из корзины')
    return redirect('cart')

@login_required
def update_cart_item(request, item_id):
    if not request.user.is_authenticated:
        cart = request.session.get('cart', {})
        quantity = int(request.POST.get('quantity', 1))
        
        if str(item_id) in cart:
            cart[str(item_id)] = quantity
            request.session['cart'] = cart
        
        return redirect('cart')
    
    cart_item = get_object_or_404(CartItem, id=item_id, корзина__пользователь=request.user)
    quantity = int(request.POST.get('quantity', 1))
    
    if 1 <= quantity <= cart_item.товар.количество_на_складе:
        cart_item.количество = quantity
        cart_item.save()
        messages.success(request, f'Количество товара "{cart_item.товар.название}" обновлено')
    else:
        messages.error(request, f'Недопустимое количество. Максимум: {cart_item.товар.количество_на_складе}')
    
    return redirect('cart')

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

@login_required
def checkout(request):
    from .models import Cart, CartItem, Order, OrderItem
    from django.core.mail import EmailMessage
    from django.conf import settings
    from io import BytesIO
    import openpyxl
    from django.contrib import messages

    try:
        cart = Cart.objects.get(пользователь=request.user)
        cart_items = cart.элементы.all()
        total_price = cart.общая_стоимость()
    except Cart.DoesNotExist:
        messages.error(request, "Ваша корзина пуста")
        return redirect('cart')
    
    if request.method == 'POST':
        delivery_address = request.POST.get('delivery_address', '')
        phone_number = request.POST.get('phone_number', '')
        email = request.POST.get('email', request.user.email)
        notes = request.POST.get('notes', '')
        
        order = Order.objects.create(
            пользователь=request.user,
            delivery_address=delivery_address,
            phone_number=phone_number,
            email=email,
            notes=notes,
            total_price=total_price
        )
        
        for item in cart_items:
            OrderItem.objects.create(
                заказ=order,
                товар=item.товар,
                количество=item.количество,
                цена=item.товар.цена
            )
            
            product = item.товар
            product.количество_на_складе -= item.количество
            product.save()
        
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Чек заказа"
        headers = ["Товар", "Количество", "Цена за единицу", "Сумма"]
        ws.append(headers)
        
        for item in order.элементы.all():
            ws.append([
                item.товар.название,
                item.количество,
                item.цена,
                item.количество * item.цена
            ])
        
        ws.append(["", "", "Итого:", order.total_price])
        
        buffer = BytesIO()
        wb.save(buffer)
        buffer.seek(0)
        excel_data = buffer.getvalue()
        
        subject = f'Чек заказа №{order.id}'
        message = f'''
        Спасибо за ваш заказ!
        Номер заказа: {order.id}
        Дата: {order.дата_создания.strftime("%d.%m.%Y %H:%M")}
        Адрес доставки: {delivery_address}
        Телефон: {phone_number}
        Общая сумма: {total_price}₽
        
        Состав заказа:
        '''
        for item in order.элементы.all():
            message += f"\n- {item.товар.название}: {item.количество} × {item.цена}₽"
        
        message += f"\n\nИтого: {total_price}₽"
        
        email_msg = EmailMessage(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [email],
        )
        email_msg.attach(
            f'checkout_{order.id}.xlsx', 
            excel_data, 
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        email_msg.send()
        
        cart_items.delete()
        cart.delete()
        
        order_items = []
        for item in order.элементы.all():
            order_items.append({
                'product': item.товар,
                'quantity': item.количество,
                'price': item.цена,
                'total': item.количество * item.цена
            })
        
        return render(request, 'shop/order_success.html', {
            'order': order,
            'order_items': order_items
        })
    
    return render(request, 'shop/checkout.html', {
        'cart_items': cart_items,
        'total_price': total_price,
        'user': request.user
    })