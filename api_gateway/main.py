
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import httpx
import uvicorn
import asyncio
import websockets
import json

app = FastAPI(title="API Gateway", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# URLs микросервисов
JOKES_SERVICE_URL = "http://localhost:5002"
RATING_SERVICE_URL = "http://localhost:5001"

# Статические файлы
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", response_class=HTMLResponse)
async def home():
    """Главная страница"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Анекдоты - Микросервисы</title>
        <meta charset="utf-8">
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; }
            .joke { border: 1px solid #ddd; padding: 20px; margin: 20px 0; border-radius: 5px; }
            .rating { font-weight: bold; color: #007bff; }
            button { margin: 5px; padding: 5px 10px; cursor: pointer; }
        </style>
    </head>
    <body>
        <h1>🎭 Анекдоты (Микросервисная архитектура)</h1>
        <div id="jokes"></div>
        
        <script>
            let ws = null;
            
            function initWebSocket() {
                ws = new WebSocket('ws://localhost:5000/ws/ratings');
                ws.onmessage = function(event) {
                    const data = JSON.parse(event.data);
                    if (data.type === 'rating_update') {
                        updateRating(data.joke_id, data.rating);
                    }
                };
            }
            
            function updateRating(jokeId, rating) {
                const element = document.getElementById(`rating-${jokeId}`);
                if (element) {
                    element.textContent = rating;
                }
            }
            
            async function rateJoke(jokeId, action) {
                try {
                    const response = await fetch(`/api/jokes/${jokeId}/rate?action=${action}`, {
                        method: 'POST'
                    });
                    const data = await response.json();
                    console.log('Rating updated:', data);
                } catch (error) {
                    console.error('Error rating joke:', error);
                }
            }
            
            async function loadJokes() {
                try {
                    const response = await fetch('/api/jokes');
                    const jokes = await response.json();
                    
                    const container = document.getElementById('jokes');
                    container.innerHTML = jokes.map(joke => `
                        <div class="joke">
                            <h3>${joke.title}</h3>
                            <p>${joke.content}</p>
                            <div>
                                <span>Категория: ${joke.category}</span> | 
                                <span>Просмотры: ${joke.views}</span> | 
                                <span>Рейтинг: <span id="rating-${joke.id}" class="rating">${joke.rating}</span></span>
                            </div>
                            <div>
                                <button onclick="rateJoke(${joke.id}, 'up')">👍</button>
                                <button onclick="rateJoke(${joke.id}, 'down')">👎</button>
                            </div>
                        </div>
                    `).join('');
                } catch (error) {
                    console.error('Error loading jokes:', error);
                }
            }
            
            // Инициализация
            initWebSocket();
            loadJokes();
        </script>
    </body>
    </html>
    """

# Proxy к Jokes Service
@app.get("/api/jokes")
async def get_jokes(category: str = None, search: str = None):
    async with httpx.AsyncClient() as client:
        params = {}
        if category:
            params["category"] = category
        if search:
            params["search"] = search
        
        response = await client.get(f"{JOKES_SERVICE_URL}/jokes", params=params)
        return response.json()

@app.get("/api/jokes/{joke_id}")
async def get_joke(joke_id: int):
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{JOKES_SERVICE_URL}/jokes/{joke_id}")
        return response.json()

@app.post("/api/jokes/{joke_id}/rate")
async def rate_joke(joke_id: int, action: str):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{RATING_SERVICE_URL}/rating/{joke_id}",
            json={"joke_id": joke_id, "action": action}
        )
        return response.json()

# WebSocket proxy к Rating Service
@app.websocket("/ws/ratings")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    
    # Подключаемся к Rating Service WebSocket
    try:
        async with websockets.connect(f"ws://localhost:5001/ws") as rating_ws:
            async def forward_to_client():
                async for message in rating_ws:
                    await websocket.send_text(message)
            
            async def forward_to_service():
                try:
                    while True:
                        data = await websocket.receive_text()
                        await rating_ws.send(data)
                except WebSocketDisconnect:
                    pass
            
            await asyncio.gather(
                forward_to_client(),
                forward_to_service()
            )
    except Exception as e:
        print(f"WebSocket proxy error: {e}")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=5000)
