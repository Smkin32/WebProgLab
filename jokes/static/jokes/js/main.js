
// Main JavaScript for jokes application

// CSRF token handling
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

const csrftoken = getCookie('csrftoken');

// Joke rating functionality
function rateJoke(jokeId, action) {
    fetch(`/rate/${jokeId}/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
            'X-CSRFToken': csrftoken,
        },
        body: `action=${action}`
    })
    .then(response => response.json())
    .then(data => {
        if (data.rating !== undefined) {
            document.getElementById(`rating-${jokeId}`).textContent = data.rating;
        }
    })
    .catch(error => {
        console.error('Error:', error);
    });
}

// Random joke functionality
function loadRandomJoke() {
    const button = document.getElementById('random-joke-btn');
    const container = document.getElementById('random-joke-container');
    
    if (button) {
        button.textContent = 'Загружаем...';
        button.disabled = true;
    }
    
    fetch('/random/')
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            if (container) {
                container.innerHTML = `<div class="error">${data.error}</div>`;
            }
        } else {
            if (container) {
                container.innerHTML = `
                    <div class="joke-card">
                        <div class="joke-meta">
                            <span class="category-tag">${data.category}</span>
                        </div>
                        <h3>${data.title}</h3>
                        <div class="joke-content">${data.content}</div>
                        <div class="joke-actions">
                            <div class="rating">
                                <button onclick="rateJoke(${data.id}, 'up')" class="up">👍</button>
                                <span id="rating-${data.id}">0</span>
                                <button onclick="rateJoke(${data.id}, 'down')" class="down">👎</button>
                            </div>
                            <a href="/joke/${data.id}/" class="btn btn-primary">Читать полностью</a>
                        </div>
                    </div>
                `;
            }
        }
    })
    .catch(error => {
        console.error('Error:', error);
        if (container) {
            container.innerHTML = '<div class="error">Ошибка загрузки анекдота</div>';
        }
    })
    .finally(() => {
        if (button) {
            button.textContent = '🎲 Случайный анекдот';
            button.disabled = false;
        }
    });
}

// Form validation
function validateContactForm() {
    const form = document.getElementById('contact-form');
    if (!form) return true;
    
    const name = form.querySelector('input[name="name"]');
    const email = form.querySelector('input[name="email"]');
    const subject = form.querySelector('input[name="subject"]');
    const message = form.querySelector('textarea[name="message"]');
    
    let isValid = true;
    
    // Reset previous error styles
    [name, email, subject, message].forEach(field => {
        if (field) field.style.borderColor = '#ddd';
    });
    
    // Validate name
    if (name && name.value.trim().length < 2) {
        name.style.borderColor = '#dc3545';
        isValid = false;
    }
    
    // Validate email
    if (email && !email.value.match(/^[^\s@]+@[^\s@]+\.[^\s@]+$/)) {
        email.style.borderColor = '#dc3545';
        isValid = false;
    }
    
    // Validate subject
    if (subject && subject.value.trim().length < 3) {
        subject.style.borderColor = '#dc3545';
        isValid = false;
    }
    
    // Validate message
    if (message && message.value.trim().length < 10) {
        message.style.borderColor = '#dc3545';
        isValid = false;
    }
    
    return isValid;
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Auto-hide messages after 5 seconds
    const messages = document.querySelectorAll('.message');
    messages.forEach(message => {
        setTimeout(() => {
            message.style.opacity = '0';
            setTimeout(() => {
                message.remove();
            }, 300);
        }, 5000);
    });
    
    // Add form validation to contact form
    const contactForm = document.getElementById('contact-form');
    if (contactForm) {
        contactForm.addEventListener('submit', function(e) {
            if (!validateContactForm()) {
                e.preventDefault();
                alert('Пожалуйста, заполните все поля корректно');
            }
        });
    }
    
    // Add smooth scrolling to anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth'
                });
            }
        });
    });
});

// Search functionality
function initializeSearch() {
    const searchForm = document.getElementById('search-form');
    const searchInput = document.getElementById('search-input');
    
    if (searchInput) {
        searchInput.addEventListener('input', function() {
            const query = this.value.trim();
            if (query.length > 2) {
                // Debounce search
                clearTimeout(this.searchTimeout);
                this.searchTimeout = setTimeout(() => {
                    performSearch(query);
                }, 300);
            }
        });
    }
}

function performSearch(query) {
    // This would be implemented if you want live search
    console.log('Searching for:', query);
}

// Mobile menu toggle
function toggleMobileMenu() {
    const navLinks = document.querySelector('.nav-links');
    if (navLinks) {
        navLinks.classList.toggle('mobile-open');
    }
}

// Add mobile menu styles
const mobileStyles = `
    @media (max-width: 768px) {
        .nav-links.mobile-open {
            display: flex;
            position: absolute;
            top: 100%;
            left: 0;
            right: 0;
            background: white;
            flex-direction: column;
            padding: 1rem;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
    }
`;

// Add styles to head
const styleSheet = document.createElement('style');
styleSheet.textContent = mobileStyles;
document.head.appendChild(styleSheet);
