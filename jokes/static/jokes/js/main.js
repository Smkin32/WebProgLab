
// WebSocket connection for real-time updates
let socket = null;

function initializeWebSocket() {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${protocol}//${window.location.host}/ws/jokes/`;
    
    socket = new WebSocket(wsUrl);
    
    socket.onopen = function(e) {
        console.log('WebSocket connection established');
    };
    
    socket.onmessage = function(e) {
        const data = JSON.parse(e.data);
        if (data.type === 'rating_update') {
            updateRatingDisplay(data.joke_id, data.new_rating, data.action);
        }
    };
    
    socket.onclose = function(e) {
        console.log('WebSocket connection closed');
        // Attempt to reconnect after 3 seconds
        setTimeout(initializeWebSocket, 3000);
    };
    
    socket.onerror = function(e) {
        console.error('WebSocket error:', e);
    };
}

function updateRatingDisplay(jokeId, newRating, action) {
    const ratingElement = document.querySelector(`#rating-${jokeId}`);
    const likesElement = document.querySelector(`#likes-${jokeId}`);
    const dislikesElement = document.querySelector(`#dislikes-${jokeId}`);
    
    if (ratingElement) {
        ratingElement.textContent = newRating;
        
        // Add visual feedback
        ratingElement.style.transform = 'scale(1.2)';
        ratingElement.style.color = action === 'like' ? '#28a745' : '#dc3545';
        
        setTimeout(() => {
            ratingElement.style.transform = 'scale(1)';
            ratingElement.style.color = '#333';
        }, 300);
    }
    
    // Update individual like/dislike counters if they exist
    if (action === 'like' && likesElement) {
        const currentLikes = parseInt(likesElement.textContent) || 0;
        likesElement.textContent = currentLikes + 1;
    } else if (action === 'dislike' && dislikesElement) {
        const currentDislikes = parseInt(dislikesElement.textContent) || 0;
        dislikesElement.textContent = currentDislikes + 1;
    }
}

function rateJoke(jokeId, action) {
    // Send rating through WebSocket for real-time updates
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
                'Content-Type': 'application/x-www-form-urlencoded',
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
            },
            body: `action=${action}`
        })
        .then(response => response.json())
        .then(data => {
            if (data.rating !== undefined) {
                updateRatingDisplay(jokeId, data.rating, action);
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

// Initialize WebSocket when page loads
document.addEventListener('DOMContentLoaded', function() {
    initializeWebSocket();
});

// Close modal when clicking outside of it
window.onclick = function(event) {
    const modal = document.getElementById('randomJokeModal');
    if (event.target === modal) {
        closeRandomJoke();
    }
}
