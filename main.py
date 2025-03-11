import os
import sys
import subprocess

def run_django_server():
    print("Запуск Django сервера...")
    
    # Запускаем миграции
    subprocess.call([sys.executable, 'manage.py', 'migrate'])
    
    # Запускаем сервер на 0.0.0.0:8000
    subprocess.call([sys.executable, 'manage.py', 'runserver', '0.0.0.0:8000'])

if __name__ == "__main__":
    run_django_server()
