// Authentication JavaScript
let currentUserType = 'customer';

// Tab switching
document.addEventListener('DOMContentLoaded', () => {
    const customerTab = document.getElementById('customer-tab');
    const providerTab = document.getElementById('provider-tab');

    if (customerTab) {
        customerTab.addEventListener('click', (e) => {
            e.preventDefault();
            switchUserType('customer');
        });
    }

    if (providerTab) {
        providerTab.addEventListener('click', (e) => {
            e.preventDefault();
            switchUserType('provider');
        });
    }

    // Form submission
    const form = document.getElementById('login-form') || document.getElementById('register-form');
    if (form) {
        form.addEventListener('submit', handleFormSubmit);
    }
});

function switchUserType(type) {
    currentUserType = type;

    // Update tabs
    document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
    if (type === 'customer') {
        document.getElementById('customer-tab').classList.add('active');
    } else {
        document.getElementById('provider-tab').classList.add('active');
    }

    // Update form fields
    const customerFields = document.getElementById('customer-fields');
    const providerFields = document.getElementById('provider-fields');

    if (customerFields && providerFields) {
        if (type === 'customer') {
            customerFields.style.display = 'block';
            providerFields.style.display = 'none';
        } else {
            customerFields.style.display = 'block';
            providerFields.style.display = 'block';
        }
    }
}

async function handleFormSubmit(e) {
    e.preventDefault();
    const form = e.target;
    const isLoginForm = form.id === 'login-form';

    try {
        const formData = new FormData(form);
        const data = {
            email: formData.get('email'),
            password: formData.get('password')
        };

        if (!isLoginForm) {
            // Register form
            const location = await getUserLocation();
            data.name = formData.get('name');
            data.phone = formData.get('phone');
            data.location = {
                latitude: location.latitude,
                longitude: location.longitude,
                address: formData.get('address')
            };

            if (currentUserType === 'provider') {
                data.service_type = formData.get('service-type');
                data.experience_years = parseInt(formData.get('experience')) || 0;
                data.hourly_rate = parseFloat(formData.get('hourly-rate')) || 0;
            }
        }

        const endpoint = isLoginForm 
            ? `/auth/login/${currentUserType}` 
            : `/auth/register/${currentUserType}`;

        const method = 'POST';
        const response = await apiRequest(endpoint, method, data);

        // Store token and user info
        localStorage.setItem('token', response.token);
        localStorage.setItem('user_id', response.user_id || response.provider_id);
        localStorage.setItem('user_role', currentUserType);

        // Redirect to dashboard
        window.location.href = 'dashboard.html';
    } catch (error) {
        const errorMessage = document.getElementById('error-message');
        if (errorMessage) {
            errorMessage.textContent = error.message;
            errorMessage.style.display = 'block';
        }
    }
}

// Redirect if already logged in
document.addEventListener('DOMContentLoaded', () => {
    const token = localStorage.getItem('token');
    if (token && (window.location.pathname.includes('login.html') || window.location.pathname.includes('register.html'))) {
        window.location.href = 'dashboard.html';
    }
});
