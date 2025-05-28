
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

// Update all visible joke ratings every second
function updateAllRatings() {
    const ratingElements = document.querySelectorAll('[id^="rating-"]');
    const jokeIds = Array.from(ratingElements).map(el => el.id.replace('rating-', ''));
    
    // Remove duplicates
    const uniqueJokeIds = [...new Set(jokeIds)];
    
    uniqueJokeIds.forEach(jokeId => {
        fetch(`/joke/${jokeId}/rating/`)
        .then(response => response.json())
        .then(data => {
            if (data.rating !== undefined) {
                const ratingElems = document.querySelectorAll(`#rating-${jokeId}`);
                ratingElems.forEach(elem => {
                    elem.textContent = data.rating;
                });
            }
        })
        .catch(error => {
            console.error('Error updating rating:', error);
        });
    });
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
    // Update ratings every 1 second
    setInterval(updateAllRatings, 1000);
});
