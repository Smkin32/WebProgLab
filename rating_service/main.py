
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import json
import asyncio
from typing import Dict, List
import uvicorn

app = FastAPI(title="Rating Service", version="1.0.0")

# CORS middleware для взаимодействия с другими сервисами
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Временное хранилище рейтингов (в продакшене будет база данных)
ratings_storage: Dict[int, int] = {
    1: 15,
    2: 14,
    3: 8,
    4: 12,
    5: 20
}

# Активные WebSocket соединения
active_connections: List[WebSocket] = []

class RatingUpdate(BaseModel):
    joke_id: int
    action: str  # "up" или "down"

class RatingResponse(BaseModel):
    joke_id: int
    rating: int

# WebSocket manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            try:
                await connection.send_text(json.dumps(message))
            except:
                # Удаляем отключенные соединения
                self.active_connections.remove(connection)

manager = ConnectionManager()

@app.get("/")
async def root():
    return {"service": "Rating Service", "status": "running"}

@app.get("/rating/{joke_id}")
async def get_rating(joke_id: int):
    """Получить рейтинг анекдота"""
    if joke_id not in ratings_storage:
        ratings_storage[joke_id] = 0
    
    return RatingResponse(joke_id=joke_id, rating=ratings_storage[joke_id])

@app.post("/rating/{joke_id}")
async def update_rating(joke_id: int, rating_update: RatingUpdate):
    """Обновить рейтинг анекдота"""
    if joke_id not in ratings_storage:
        ratings_storage[joke_id] = 0
    
    if rating_update.action == "up":
        ratings_storage[joke_id] += 1
    elif rating_update.action == "down":
        ratings_storage[joke_id] -= 1
    else:
        raise HTTPException(status_code=400, detail="Invalid action")
    
    # Отправляем обновление всем подключенным клиентам
    await manager.broadcast({
        "type": "rating_update",
        "joke_id": joke_id,
        "rating": ratings_storage[joke_id]
    })
    
    return RatingResponse(joke_id=joke_id, rating=ratings_storage[joke_id])

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket для real-time обновлений рейтингов"""
    await manager.connect(websocket)
    try:
        while True:
            # Ожидаем сообщения от клиента (для поддержания соединения)
            data = await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=5001)
