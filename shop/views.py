from django.shortcuts import render, get_object_or_404
from django.http import Http404
from .models import Qualification
import json
import os
from django.conf import settings

def load_qualifications_from_json():
    """Загружает квалификации из JSON файла"""
    json_path = os.path.join(settings.BASE_DIR, 'attached_assets', 'dump.json')
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