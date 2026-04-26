// Dashboard JavaScript
let socket;
let userLocation = null;

document.addEventListener('DOMContentLoaded', async () => {
    // Check authentication
    const token = getToken();
    if (!token) {
        window.location.href = 'login.html';
        return;
    }

    // Initialize Socket.IO
    socket = io('http://localhost:5000', {
        auth: {
            user_id: getUserId()
        }
    });

    socket.on('booking_status_changed', (data) => {
        console.log('Booking status changed:', data);
        loadBookings();
    });

    socket.on('provider_location_updated', (data) => {
        console.log('Provider location updated:', data);
        updateProviderLocation(data);
    });

    socket.on('notification', (data) => {
        console.log('Notification:', data);
        showNotification(data.message);
    });

    // Load initial data
    await loadUserProfile();
    await loadBookings();
    await loadRatings();

    // Get user location
    try {
        userLocation = await getUserLocation();
    } catch (error) {
        console.error('Error getting location:', error);
    }

    // Setup event listeners
    document.getElementById('search-form')?.addEventListener('submit', handleSearchSubmit);
    document.getElementById('profile-form')?.addEventListener('submit', handleProfileSubmit);
});

function showTab(tabName) {
    // Hide all tabs
    document.querySelectorAll('.tab-content').forEach(tab => {
        tab.classList.remove('active');
    });

    // Remove active class from menu items
    document.querySelectorAll('.menu-item').forEach(item => {
        item.classList.remove('active');
    });

    // Show selected tab
    const tabId = tabName === 'bookings' ? 'bookings-tab' : 
                  tabName === 'find-service' ? 'find-service-tab' :
                  tabName === 'profile' ? 'profile-tab' :
                  tabName === 'ratings' ? 'ratings-tab' : '';

    if (tabId) {
        document.getElementById(tabId).classList.add('active');
    }

    // Add active class to menu item
    event.target.classList.add('active');
}

async function loadUserProfile() {
    try {
        const user = await apiRequest(`/users/${getUserId()}`);
        document.getElementById('user-name').textContent = user.name;

        // Populate profile form
        if (document.getElementById('profile-form')) {
            document.getElementById('profile-name').value = user.name;
            document.getElementById('profile-phone').value = user.phone;
            document.getElementById('profile-address').value = user.location.address;
        }
    } catch (error) {
        console.error('Error loading profile:', error);
    }
}

async function loadBookings() {
    try {
        const response = await apiRequest(`/users/${getUserId()}/bookings`);
        const bookingsList = document.getElementById('bookings-list');

        if (response.bookings.length === 0) {
            bookingsList.innerHTML = '<p>No bookings yet.</p>';
            return;
        }

        bookingsList.innerHTML = response.bookings.map(booking => `
            <div class="booking-card">
                <div class="booking-header">
                    <div>
                        <h3>${booking.service_type}</h3>
                        <p>${new Date(booking.scheduled_date).toLocaleDateString()}</p>
                    </div>
                    <span class="booking-status ${booking.status}">${booking.status}</span>
                </div>
                <p><strong>Description:</strong> ${booking.description}</p>
                <p><strong>Estimated Hours:</strong> ${booking.estimated_hours}</p>
                <p><strong>Price:</strong> $${booking.final_price || booking.base_price || 'N/A'}</p>
                <div style="margin-top: 1rem;">
                    <button class="btn btn-primary btn-sm" onclick="viewBookingDetails('${booking._id}')">View Details</button>
                    ${booking.status === 'pending' ? `<button class="btn btn-secondary btn-sm" onclick="cancelBooking('${booking._id}')">Cancel</button>` : ''}
                </div>
            </div>
        `).join('');
    } catch (error) {
        console.error('Error loading bookings:', error);
    }
}

async function loadRatings() {
    try {
        const response = await apiRequest(`/ratings/${getUserId()}`);
        const ratingsList = document.getElementById('ratings-list');

        if (!ratingsList) return;

        if (response.ratings.length === 0) {
            ratingsList.innerHTML = `<p>Average Rating: ${response.average_rating}/5 (No ratings yet)</p>`;
            return;
        }

        ratingsList.innerHTML = `
            <p><strong>Average Rating:</strong> ${response.average_rating}/5 (${response.total_ratings} ratings)</p>
            <div>
                ${response.ratings.map(rating => `
                    <div style="border: 1px solid #e2e8f0; padding: 1rem; margin-top: 1rem; border-radius: 0.5rem;">
                        <p><strong>Rating:</strong> ${'⭐'.repeat(rating.rating)}</p>
                        <p><strong>Review:</strong> ${rating.review_text}</p>
                        <p style="color: #6b7280; font-size: 0.9rem;">${new Date(rating.created_at).toLocaleDateString()}</p>
                    </div>
                `).join('')}
            </div>
        `;
    } catch (error) {
        console.error('Error loading ratings:', error);
    }
}

async function handleSearchSubmit(e) {
    e.preventDefault();
    const formData = new FormData(e.target);

    try {
        const data = {
            service_type: formData.get('service-type'),
            description: formData.get('description'),
            location: userLocation || { latitude: 0, longitude: 0 },
            scheduled_date: formData.get('date'),
            estimated_hours: parseFloat(formData.get('hours'))
        };

        // Create booking
        const bookingResponse = await apiRequest('/bookings', 'POST', {
            service_type: data.service_type,
            description: data.description,
            location: data.location,
            scheduled_date: data.scheduled_date,
            estimated_hours: data.estimated_hours
        });

        const bookingId = bookingResponse.booking_id;

        // Find providers
        const providersResponse = await apiRequest('/matching/find-providers/' + data.service_type, 'POST', {
            location: data.location
        });

        const providersList = document.getElementById('providers-list');
        if (providersResponse.providers.length === 0) {
            providersList.innerHTML = '<p>No providers available for this service.</p>';
            providersList.style.display = 'block';
            return;
        }

        providersList.innerHTML = providersResponse.providers.map(provider => `
            <div class="provider-card">
                <div class="provider-info">
                    <h3>${provider.name}</h3>
                    <p class="provider-rating">⭐ ${provider.rating || 'N/A'}</p>
                    <p class="provider-distance">${provider.experience_years} years experience</p>
                </div>
                <div>
                    <div class="provider-price">$${provider.hourly_rate}/hr</div>
                    <button class="btn btn-primary" onclick="placeBid('${bookingId}', '${provider._id}', ${provider.hourly_rate})">Place Bid</button>
                </div>
            </div>
        `).join('');

        providersList.style.display = 'block';

        showNotification('Booking created! Waiting for provider bids...');
    } catch (error) {
        showNotification('Error creating booking: ' + error.message, 'error');
    }
}

async function placeBid(bookingId, providerId, bidPrice) {
    // This will be called by providers to place bids
    try {
        const bidResponse = await apiRequest(`/matching/bid/${bookingId}`, 'POST', {
            bid_price: bidPrice,
            estimated_time: '2 hours'
        });

        showNotification('Bid placed successfully!');
        loadBookings();
    } catch (error) {
        showNotification('Error placing bid: ' + error.message, 'error');
    }
}

async function handleProfileSubmit(e) {
    e.preventDefault();
    const formData = new FormData(e.target);

    try {
        const data = {
            name: formData.get('name'),
            phone: formData.get('phone'),
            location: {
                address: formData.get('address'),
                latitude: userLocation?.latitude || 0,
                longitude: userLocation?.longitude || 0
            }
        };

        await apiRequest(`/users/${getUserId()}`, 'PUT', data);
        showNotification('Profile updated successfully!');
    } catch (error) {
        showNotification('Error updating profile: ' + error.message, 'error');
    }
}

async function viewBookingDetails(bookingId) {
    try {
        const booking = await apiRequest(`/bookings/${bookingId}`);
        alert(`Booking Details:\n\nService: ${booking.service_type}\nStatus: ${booking.status}\nPrice: $${booking.final_price || booking.base_price || 'N/A'}\nEstimated Hours: ${booking.estimated_hours}`);
    } catch (error) {
        showNotification('Error loading booking details: ' + error.message, 'error');
    }
}

async function cancelBooking(bookingId) {
    if (confirm('Are you sure you want to cancel this booking?')) {
        try {
            await apiRequest(`/bookings/${bookingId}/cancel`, 'POST');
            showNotification('Booking cancelled successfully!');
            loadBookings();
        } catch (error) {
            showNotification('Error cancelling booking: ' + error.message, 'error');
        }
    }
}

function updateProviderLocation(data) {
    console.log('Updating provider location on map:', data);
    // This would integrate with a map library like Google Maps
}

function showNotification(message, type = 'success') {
    // Create a simple notification
    const notification = document.createElement('div');
    notification.style.cssText = `
        position: fixed;
        top: 80px;
        right: 20px;
        padding: 1rem;
        background-color: ${type === 'error' ? '#fee2e2' : '#dcfce7'};
        color: ${type === 'error' ? '#991b1b' : '#166534'};
        border-radius: 0.5rem;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
        z-index: 1000;
    `;
    notification.textContent = message;
    document.body.appendChild(notification);

    setTimeout(() => {
        notification.remove();
    }, 3000);
}

// Logout function
function logout() {
    localStorage.clear();
    if (socket) {
        socket.disconnect();
    }
    window.location.href = 'index.html';
}
