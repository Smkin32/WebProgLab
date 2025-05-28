
// WebSocket connection for real-time updates
let socket = null;

function initializeWebSocket() {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${protocol}//${window.location.host}/ws/jokes/`;
    
    socket = new WebSocket(wsUrl);
    
    socket.onopen = function(e) {
        console.log('WebSocket connection established');
        updateConnectionStatus('connected');
    };
    
    socket.onmessage = function(e) {
        const data = JSON.parse(e.data);
        if (data.type === 'rating_update') {
            updateRatingDisplay(data.joke_id, data.new_rating, data.action);
        }
    };
    
    socket.onclose = function(e) {
        console.log('WebSocket connection closed');
        updateConnectionStatus('disconnected');
        // Attempt to reconnect after 3 seconds
        setTimeout(initializeWebSocket, 3000);
    };
    
    socket.onerror = function(e) {
        console.error('WebSocket error:', e);
        updateConnectionStatus('connecting');
    };
}

function updateConnectionStatus(status) {
    let statusEl = document.getElementById('connection-status');
    if (!statusEl) {
        statusEl = document.createElement('div');
        statusEl.id = 'connection-status';
        statusEl.className = 'connection-status';
        document.body.appendChild(statusEl);
    }
    
    statusEl.className = `connection-status ${status}`;
    switch(status) {
        case 'connected':
            statusEl.textContent = '🟢 Подключено';
            break;
        case 'disconnected':
            statusEl.textContent = '🔴 Отключено';
            break;
        case 'connecting':
            statusEl.textContent = '🟡 Подключение...';
            break;
    }
}

function rateJoke(jokeId, action) {
    // Send rating via WebSocket if connected
    if (socket && socket.readyState === WebSocket.OPEN) {
        socket.send(JSON.stringify({
            'action': action,
            'joke_id': jokeId
        }));
    } else {
        // Fallback to HTTP request if WebSocket is not available
        fetch(`/rate/${jokeId}/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({
                'action': action
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                updateRatingDisplay(jokeId, data.new_rating, action);
            }
        })
        .catch(error => {
            console.error('Error rating joke:', error);
        });
    }
}

function updateRatingDisplay(jokeId, newRating, action) {
    const ratingEl = document.querySelector(`[data-joke-id="${jokeId}"] .joke-rating`);
    if (ratingEl) {
        ratingEl.textContent = `Рейтинг: ${newRating}`;
        ratingEl.classList.add('rating-updated');
        setTimeout(() => {
            ratingEl.classList.remove('rating-updated');
        }, 600);
    }
}

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function showRandomJoke() {
    fetch('/random/')
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            alert('Анекдоты не найдены!');
            return;
        }

        document.getElementById('randomJokeContent').innerHTML = data.content.replace(/\n/g, '<br>');
        document.getElementById('randomJokeCategory').innerHTML = `<span class="category-tag">${data.category}</span>`;
        document.getElementById('randomJokeModal').style.display = 'block';
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Ошибка при загрузке анекдота');
    });
}

function closeRandomJoke() {
    document.getElementById('randomJokeModal').style.display = 'none';
}

// Initialize WebSocket when page loads
document.addEventListener('DOMContentLoaded', function() {
    updateConnectionStatus('connecting');
    initializeWebSocket();
});

// Close modal when clicking outside of it
window.onclick = function(event) {
    const modal = document.getElementById('randomJokeModal');
    if (event.target === modal) {
        modal.style.display = 'none';
    }
}
