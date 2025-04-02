from django.shortcuts import render
from django.http import Http404
import json
import os

def load_specs():
    json_path = os.path.join(os.path.dirname(__file__), 'dump.json')
    try:
        with open(json_path, 'r', encoding='utf-8') as file:
            return json.load(file)
    except FileNotFoundError:
        return []

def home(request):
    """Представление для главной страницы"""
    return render(request, 'shop/home.html')

def about(request):
    """Представление для страницы об авторе"""
    return render(request, 'shop/about.html')

def shop_info(request):
    """Представление для страницы о магазине"""
    return render(request, 'shop/shop_info.html')

def spec_list(request):
    """Представление для списка квалификаций"""
    specs = load_specs()
    return render(request, 'shop/spec_list.html', {'specs': specs})

def spec_detail(request, spec_id):
    """Представление для детальной информации о квалификации"""
    specs = load_specs()
    spec = next((s for s in specs if s.get('id') == spec_id), None)

    if spec is None:
        raise Http404("Квалификация не найдена")

    return render(request, 'shop/spec_detail.html', {'spec': spec})