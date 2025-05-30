
// WebSocket connection for real-time rating updates
let ratingSocket = null;

function initializeWebSocket() {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${protocol}//${window.location.host}/ws/ratings/`;
    
    ratingSocket = new WebSocket(wsUrl);
    
    ratingSocket.onopen = function(e) {
        console.log('WebSocket connection established');
    };
    
    ratingSocket.onmessage = function(e) {
        const data = JSON.parse(e.data);
        if (data.type === 'rating_update') {
            updateRatingDisplay(data.joke_id, data.rating);
        }
    };
    
    ratingSocket.onclose = function(e) {
        console.log('WebSocket connection closed. Attempting to reconnect...');
        setTimeout(initializeWebSocket, 3000);
    };
    
    ratingSocket.onerror = function(e) {
        console.error('WebSocket error:', e);
    };
}

function updateRatingDisplay(jokeId, rating) {
    const ratingElements = document.querySelectorAll(`#rating-${jokeId}`);
    ratingElements.forEach(element => {
        element.textContent = rating;
    });
}

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

function rateJoke(jokeId, action) {
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
            // Update will be handled by WebSocket message
            console.log('Rating updated successfully');
        }
    })
    .catch(error => {
        console.error('Error rating joke:', error);
    });
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
    // Initialize WebSocket connection
    initializeWebSocket();
});
