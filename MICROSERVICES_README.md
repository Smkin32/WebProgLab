
# 🎭 Анекдоты - Микросервисная архитектура

Проект разбит на следующие микросервисы:

## 🏗️ Архитектура

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   API Gateway   │────│  Jokes Service  │    │  Rating Service │
│   Port: 5000    │    │   Port: 5002    │    │   Port: 5001    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │                       │
    ┌────▼────┐             ┌────▼────┐             ┌────▼────┐
    │ Клиенты │             │ База    │             │ WebSocket│
    │  Web UI │             │ анекдотов│             │ для рейтингов│
    └─────────┘             └─────────┘             └─────────┘
```

## 🛠️ Микросервисы

### 1. **Rating Service** (порт 5001)
- ⭐ Управление рейтингами анекдотов
- 🔄 WebSocket для real-time обновлений
- 📊 API для получения и обновления рейтингов

**Endpoints:**
- `GET /rating/{joke_id}` - получить рейтинг
- `POST /rating/{joke_id}` - обновить рейтинг  
- `WS /ws` - WebSocket соединение

### 2. **Jokes Service** (порт 5002)
- 📝 Управление анекдотами
- 🔍 Поиск и фильтрация
- 📈 Счетчики просмотров
- 🔗 Интеграция с Rating Service

**Endpoints:**
- `GET /jokes` - список анекдотов
- `GET /jokes/{joke_id}` - конкретный анекдот
- `GET /jokes/random` - случайный анекдот
- `GET /categories` - категории

### 3. **API Gateway** (порт 5000)
- 🌐 Единая точка входа
- 🔀 Маршрутизация запросов
- 🎨 Web интерфейс
- 🔌 WebSocket прокси

## 🚀 Запуск

### Автоматический запуск всех сервисов:
```bash
python start_microservices.py
```

### Ручной запуск каждого сервиса:

1. **Rating Service:**
```bash
cd rating_service
pip install -r requirements.txt  
python main.py
```

2. **Jokes Service:**
```bash
cd jokes_service
pip install -r requirements.txt
python main.py
```

3. **API Gateway:**
```bash
cd api_gateway  
pip install -r requirements.txt
python main.py
```

## 📱 Использование

- **Главная страница:** http://localhost:5000
- **API документация Jokes:** http://localhost:5002/docs
- **API документация Rating:** http://localhost:5001/docs

## 🔄 Взаимодействие сервисов

1. **Клиент** отправляет запрос в **API Gateway**
2. **API Gateway** перенаправляет в соответствующий сервис
3. **Jokes Service** при необходимости обращается к **Rating Service**
4. **Rating Service** отправляет WebSocket уведомления через **API Gateway**

## 📊 Преимущества микросервисной архитектуры

- ✅ **Независимое развертывание** каждого сервиса
- ✅ **Масштабирование** по потребностям  
- ✅ **Технологическое разнообразие** (можно использовать разные языки/БД)
- ✅ **Отказоустойчивость** (падение одного сервиса не влияет на другие)
- ✅ **Команды** могут работать независимо над разными сервисами

## 🔮 Будущие улучшения

- 🔐 **User Service** для аутентификации
- 📧 **Notification Service** для Telegram/Email
- 🗄️ **Отдельные базы данных** для каждого сервиса
- 🔍 **Service Discovery** (Consul, etcd)
- 📊 **Мониторинг** (Prometheus, Grafana)
- 🐳 **Контейнеризация** (Docker)
