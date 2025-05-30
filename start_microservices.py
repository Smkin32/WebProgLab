
#!/usr/bin/env python3
"""
Скрипт для запуска всех микросервисов
"""

import subprocess
import time
import sys
import os

def install_dependencies(service_dir):
    """Установка зависимостей для сервиса"""
    print(f"Installing dependencies for {service_dir}...")
    subprocess.run([
        sys.executable, "-m", "pip", "install", "-r", 
        os.path.join(service_dir, "requirements.txt")
    ], check=True)

def start_service(service_dir, port):
    """Запуск сервиса"""
    print(f"Starting {service_dir} on port {port}...")
    return subprocess.Popen([
        sys.executable, os.path.join(service_dir, "main.py")
    ], cwd=service_dir)

def main():
    """Главная функция"""
    services = [
        ("rating_service", 5001),
        ("jokes_service", 5002),
        ("api_gateway", 5000),
    ]
    
    processes = []
    
    try:
        # Установка зависимостей
        for service_dir, _ in services:
            if os.path.exists(service_dir):
                install_dependencies(service_dir)
        
        # Запуск сервисов
        for service_dir, port in services:
            if os.path.exists(service_dir):
                process = start_service(service_dir, port)
                processes.append(process)
                time.sleep(2)  # Пауза между запусками
        
        print("\n" + "="*50)
        print("🚀 Все микросервисы запущены!")
        print("📱 Главная страница: http://localhost:5000")
        print("🎭 Jokes Service: http://localhost:5002/docs")
        print("⭐ Rating Service: http://localhost:5001/docs") 
        print("="*50)
        
        # Ожидание завершения
        for process in processes:
            process.wait()
            
    except KeyboardInterrupt:
        print("\n🛑 Останавливаем сервисы...")
        for process in processes:
            process.terminate()
        print("✅ Все сервисы остановлены")

if __name__ == "__main__":
    main()
