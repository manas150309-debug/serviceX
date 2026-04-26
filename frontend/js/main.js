// Main JavaScript
const API_URL = 'http://localhost:5000/api';

// Utility function to get token from localStorage
function getToken() {
    return localStorage.getItem('token');
}

// Utility function to get user ID from localStorage
function getUserId() {
    return localStorage.getItem('user_id');
}

// Utility function to get user role from localStorage
function getUserRole() {
    return localStorage.getItem('user_role');
}

// Utility function to get user location
function getUserLocation() {
    return new Promise((resolve, reject) => {
        if (navigator.geolocation) {
            navigator.geolocation.getCurrentPosition(
                position => {
                    resolve({
                        latitude: position.coords.latitude,
                        longitude: position.coords.longitude
                    });
                },
                error => reject(error)
            );
        } else {
            reject(new Error('Geolocation is not supported'));
        }
    });
}

// Make API request
async function apiRequest(endpoint, method = 'GET', data = null) {
    const options = {
        method: method,
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${getToken()}`
        }
    };

    if (data) {
        options.body = JSON.stringify(data);
    }

    try {
        const response = await fetch(`${API_URL}${endpoint}`, options);
        const result = await response.json();

        if (!response.ok) {
            throw new Error(result.message || 'API request failed');
        }

        return result;
    } catch (error) {
        console.error('API Error:', error);
        throw error;
    }
}

// Update navigation based on auth status
function updateNavigation() {
    const token = getToken();
    const navLinks = document.getElementById('nav-links');

    if (!navLinks) return;

    if (token) {
        navLinks.innerHTML = `
            <li><a href="dashboard.html">Dashboard</a></li>
            <li><a href="#" onclick="logout()">Logout</a></li>
        `;
    } else {
        navLinks.innerHTML = `
            <li><a href="index.html">Home</a></li>
            <li><a href="login.html">Login</a></li>
            <li><a href="register.html">Register</a></li>
        `;
    }
}

// Logout function
function logout() {
    localStorage.clear();
    window.location.href = 'index.html';
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', updateNavigation);
