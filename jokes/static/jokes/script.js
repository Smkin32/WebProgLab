

// Get CSRF token from cookies
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

// WebSocket connection
let socket;
let reconnectInterval = 3000; // 3 seconds

function connectWebSocket() {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${protocol}//${window.location.host}/ws`;
    
    socket = new WebSocket(wsUrl);

    socket.onopen = function(e) {
        console.log('WebSocket connected');
        socket.send(JSON.stringify({
            type: 'connection',
            message: 'Client connected'
        }));
    };

    socket.onmessage = function(event) {
        try {
            const data = JSON.parse(event.data);
            
            if (data.type === 'rating_update') {
                // Update all rating displays for this joke
                const ratingElements = document.querySelectorAll(`#rating-${data.joke_id}`);
                ratingElements.forEach(element => {
                    element.textContent = data.rating;
                });
            }
        } catch (e) {
            console.log('Error parsing WebSocket message:', e.message);
        }
    };

    socket.onclose = function(e) {
        console.log('WebSocket disconnected. Attempting to reconnect...');
        setTimeout(connectWebSocket, reconnectInterval);
    };

    socket.onerror = function(error) {
        console.error('WebSocket error:', error);
    };
}

function rateJoke(jokeId, action) {
    // Send rating update via WebSocket if connected
    if (socket && socket.readyState === WebSocket.OPEN) {
        socket.send(JSON.stringify({
            type: 'rate_joke',
            joke_id: jokeId,
            action: action
        }));
    } else {
        // Fallback to HTTP request if WebSocket is not available
        const csrftoken = getCookie('csrftoken');
        
        fetch(`/rate/${jokeId}/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
                'X-CSRFToken': csrftoken
            },
            body: `action=${action}`
        })
        .then(response => response.json())
        .then(data => {
            if (data.rating !== undefined) {
                // Update all rating displays for this joke across the page
                const ratingElements = document.querySelectorAll(`#rating-${jokeId}`);
                ratingElements.forEach(element => {
                    element.textContent = data.rating;
                });
            }
        })
        .catch(error => {
            console.error('Error rating joke:', error);
        });
    }
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

// Close modal when clicking outside of it
window.onclick = function(event) {
    const modal = document.getElementById('randomJokeModal');
    if (event.target === modal) {
        closeRandomJoke();
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Connect to WebSocket
    connectWebSocket();
});
