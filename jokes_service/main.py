
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import httpx
import uvicorn
from datetime import datetime

app = FastAPI(title="Jokes Service", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# URL Rating Service (в продакшене будет через service discovery)
RATING_SERVICE_URL = "http://localhost:5001"

# Временное хранилище анекдотов
jokes_storage = [
    {
        "id": 1,
        "title": "Анекдот про программиста",
        "content": "Идет программист в душ, жена кричит: - Возьми шампунь! Программист взял шампунь, лег спать.",
        "category": "programming",
        "created_at": datetime.now(),
        "views": 125
    },
    {
        "id": 2,
        "title": "Медицинский анекдот",
        "content": "Доктор говорит пациенту: - У вас очень редкая болезнь. - А что это значит? - Это значит, что вы будете названы в честь неё.",
        "category": "medical",
        "created_at": datetime.now(),
        "views": 89
    },
    {
        "id": 3,
        "title": "Семейный анекдот",
        "content": "Жена мужу: - Дорогой, ты меня любишь? - Конечно! - А почему тогда в телефоне я записана как 'Дом'? - А ты хочешь быть 'Работой'?",
        "category": "family",
        "created_at": datetime.now(),
        "views": 67
    }
]

CATEGORIES = [
    ("general", "Общие"),
    ("political", "Политические"),
    ("family", "Семейные"),
    ("work", "Рабочие"),
    ("student", "Студенческие"),
    ("medical", "Медицинские"),
    ("programming", "Про программистов"),
]

class Joke(BaseModel):
    id: int
    title: str
    content: str
    category: str
    created_at: datetime
    views: int

class JokeWithRating(BaseModel):
    id: int
    title: str
    content: str
    category: str
    created_at: datetime
    views: int
    rating: int

async def get_joke_rating(joke_id: int) -> int:
    """Получить рейтинг анекдота из Rating Service"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{RATING_SERVICE_URL}/rating/{joke_id}")
            if response.status_code == 200:
                return response.json()["rating"]
    except:
        pass
    return 0

@app.get("/")
async def root():
    return {"service": "Jokes Service", "status": "running"}

@app.get("/jokes", response_model=List[JokeWithRating])
async def get_jokes(category: Optional[str] = None, search: Optional[str] = None):
    """Получить список анекдотов с фильтрацией"""
    filtered_jokes = jokes_storage.copy()
    
    if category:
        filtered_jokes = [j for j in filtered_jokes if j["category"] == category]
    
    if search:
        filtered_jokes = [j for j in filtered_jokes 
                         if search.lower() in j["content"].lower() 
                         or search.lower() in j["title"].lower()]
    
    # Добавляем рейтинги к анекдотам
    jokes_with_ratings = []
    for joke in filtered_jokes:
        rating = await get_joke_rating(joke["id"])
        jokes_with_ratings.append(JokeWithRating(**joke, rating=rating))
    
    return jokes_with_ratings

@app.get("/jokes/{joke_id}", response_model=JokeWithRating)
async def get_joke(joke_id: int):
    """Получить конкретный анекдот"""
    joke = next((j for j in jokes_storage if j["id"] == joke_id), None)
    if not joke:
        raise HTTPException(status_code=404, detail="Joke not found")
    
    # Увеличиваем счетчик просмотров
    joke["views"] += 1
    
    # Получаем рейтинг
    rating = await get_joke_rating(joke_id)
    
    return JokeWithRating(**joke, rating=rating)

@app.get("/jokes/random")
async def get_random_joke():
    """Получить случайный анекдот"""
    import random
    if not jokes_storage:
        raise HTTPException(status_code=404, detail="No jokes found")
    
    joke = random.choice(jokes_storage)
    rating = await get_joke_rating(joke["id"])
    
    return JokeWithRating(**joke, rating=rating)

@app.get("/categories")
async def get_categories():
    """Получить список категорий"""
    return [{"value": cat[0], "label": cat[1]} for cat in CATEGORIES]

@app.post("/jokes/{joke_id}/rate")
async def rate_joke(joke_id: int, action: str):
    """Проксировать запрос рейтинга в Rating Service"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{RATING_SERVICE_URL}/rating/{joke_id}",
                json={"joke_id": joke_id, "action": action}
            )
            return response.json()
    except Exception as e:
        raise HTTPException(status_code=500, detail="Rating service unavailable")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=5002)
