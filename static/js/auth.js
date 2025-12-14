// Authentication JavaScript
const API_URL = '/api';

// Login Form Handler
if (document.getElementById('loginForm')) {
    document.getElementById('loginForm').addEventListener('submit', async (e) => {
        e.preventDefault();

        const username = document.getElementById('username').value;
        const password = document.getElementById('password').value;
        const errorDiv = document.getElementById('errorMessage');
        const submitBtn = e.target.querySelector('button[type="submit"]');

        // Clear previous errors
        errorDiv.style.display = 'none';
        submitBtn.classList.add('loading');

        try {
            const response = await fetch(`${API_URL}/login`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ username, password })
            });

            const data = await response.json();

            if (data.success) {
                // Store session token
                localStorage.setItem('session_token', data.session_token);
                localStorage.setItem('user', JSON.stringify(data.user));

                // Redirect to chat
                window.location.href = 'chat.html';
            } else {
                errorDiv.textContent = data.message || 'Login failed';
                errorDiv.style.display = 'block';
            }
        } catch (error) {
            errorDiv.textContent = 'Connection error. Please try again.';
            errorDiv.style.display = 'block';
        } finally {
            submitBtn.classList.remove('loading');
        }
    });
}

// Register Form Handler
if (document.getElementById('registerForm')) {
    const passwordInput = document.getElementById('password');
    const confirmPasswordInput = document.getElementById('confirmPassword');
    const strengthBar = document.querySelector('.strength-bar');

    // Password strength indicator
    passwordInput.addEventListener('input', () => {
        const password = passwordInput.value;
        let strength = 0;

        if (password.length >= 6) strength++;
        if (password.length >= 10) strength++;
        if (/[a-z]/.test(password) && /[A-Z]/.test(password)) strength++;
        if (/\d/.test(password)) strength++;
        if (/[^a-zA-Z\d]/.test(password)) strength++;

        if (strength <= 2) {
            strengthBar.className = 'strength-bar weak';
        } else if (strength <= 4) {
            strengthBar.className = 'strength-bar medium';
        } else {
            strengthBar.className = 'strength-bar strong';
        }
    });

    document.getElementById('registerForm').addEventListener('submit', async (e) => {
        e.preventDefault();

        const username = document.getElementById('username').value;
        const email = document.getElementById('email').value;
        const password = passwordInput.value;
        const confirmPassword = confirmPasswordInput.value;
        const errorDiv = document.getElementById('errorMessage');
        const successDiv = document.getElementById('successMessage');
        const submitBtn = e.target.querySelector('button[type="submit"]');

        // Clear previous messages
        errorDiv.style.display = 'none';
        successDiv.style.display = 'none';

        // Validate passwords match
        if (password !== confirmPassword) {
            errorDiv.textContent = 'Passwords do not match';
            errorDiv.style.display = 'block';
            return;
        }

        submitBtn.classList.add('loading');

        try {
            const response = await fetch(`${API_URL}/register`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ username, email, password })
            });

            const data = await response.json();

            if (data.success) {
                successDiv.textContent = 'Account created successfully! Redirecting to login...';
                successDiv.style.display = 'block';

                // Redirect to login after 2 seconds
                setTimeout(() => {
                    window.location.href = 'index.html';
                }, 2000);
            } else {
                errorDiv.textContent = data.message || 'Registration failed';
                errorDiv.style.display = 'block';
            }
        } catch (error) {
            errorDiv.textContent = 'Connection error. Please try again.';
            errorDiv.style.display = 'block';
        } finally {
            submitBtn.classList.remove('loading');
        }
    });
}
