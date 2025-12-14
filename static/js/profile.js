// Profile Page JavaScript
const API_URL = '/api';

// Check authentication
const sessionToken = localStorage.getItem('session_token');
const user = JSON.parse(localStorage.getItem('user') || '{}');

if (!sessionToken) {
    window.location.href = 'index.html';
}

// Initialize
init();

function init() {
    // Set user info
    document.getElementById('profileInitial').textContent = (user.username || 'U')[0].toUpperCase();
    document.getElementById('profileUsername').textContent = user.username || 'User';
    document.getElementById('profileEmail').textContent = user.email || '';
    document.getElementById('username').value = user.username || '';
    document.getElementById('email').value = user.email || '';

    // Load chat statistics
    loadChatStats();

    // Tab switching
    const tabBtns = document.querySelectorAll('.tab-btn');
    tabBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            const tabName = btn.dataset.tab;
            switchTab(tabName);
        });
    });

    // Form handlers
    document.getElementById('updateProfileForm').addEventListener('submit', updateProfile);
    document.getElementById('changePasswordForm').addEventListener('submit', changePassword);
    document.getElementById('deleteAccountBtn').addEventListener('click', deleteAccount);

    // Password strength
    const newPasswordInput = document.getElementById('newPassword');
    const strengthBar = document.querySelector('.strength-bar');

    newPasswordInput.addEventListener('input', () => {
        const password = newPasswordInput.value;
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
}

function switchTab(tabName) {
    // Remove active class from all tabs
    document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
    document.querySelectorAll('.tab-content').forEach(content => content.classList.remove('active'));

    // Add active class to selected tab
    document.querySelector(`[data-tab="${tabName}"]`).classList.add('active');
    document.getElementById(`${tabName}-tab`).classList.add('active');

    // Load data for specific tabs
    if (tabName === 'history') {
        loadChatHistory();
    }
}

async function loadChatStats() {
    try {
        const response = await fetch(`${API_URL}/stats`, {
            headers: {
                'Authorization': sessionToken
            }
        });

        const data = await response.json();

        if (data.success) {
            document.getElementById('totalMessages').textContent = data.stats.total_messages || 0;
            document.getElementById('textMessages').textContent = data.stats.by_mode?.text || 0;
            document.getElementById('voiceMessages').textContent = data.stats.by_mode?.voice || 0;
        }
    } catch (error) {
        console.error('Failed to load stats:', error);
    }
}

async function loadChatHistory() {
    const historyList = document.getElementById('historyList');
    historyList.innerHTML = '<p class="loading">Loading...</p>';

    try {
        const response = await fetch(`${API_URL}/history?limit=50`, {
            headers: {
                'Authorization': sessionToken
            }
        });

        const data = await response.json();

        if (data.success && data.history.length > 0) {
            historyList.innerHTML = '';
            data.history.forEach(msg => {
                const historyItem = document.createElement('div');
                historyItem.className = 'history-item';
                historyItem.innerHTML = `
                    <div class="history-time">${new Date(msg.timestamp).toLocaleString()}</div>
                    <div class="history-message">
                        <strong>You:</strong> ${msg.message}
                    </div>
                    <div class="history-response">
                        <strong>AI:</strong> ${msg.response.substring(0, 100)}${msg.response.length > 100 ? '...' : ''}
                    </div>
                    <div class="history-meta">
                        Mode: ${msg.mode} | Language: ${msg.language}
                    </div>
                `;
                historyList.appendChild(historyItem);
            });
        } else {
            historyList.innerHTML = '<p class="no-data">No chat history yet</p>';
        }
    } catch (error) {
        historyList.innerHTML = '<p class="error">Failed to load history</p>';
    }
}

async function updateProfile(e) {
    e.preventDefault();

    const username = document.getElementById('username').value;
    const email = document.getElementById('email').value;
    const submitBtn = e.target.querySelector('button[type="submit"]');
    const messageDiv = document.getElementById('profileMessage');
    const errorDiv = document.getElementById('profileError');

    messageDiv.style.display = 'none';
    errorDiv.style.display = 'none';
    submitBtn.classList.add('loading');

    try {
        const response = await fetch(`${API_URL}/update-profile`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': sessionToken
            },
            body: JSON.stringify({ username, email })
        });

        const data = await response.json();

        if (data.success) {
            // Update local storage
            user.username = username;
            user.email = email;
            localStorage.setItem('user', JSON.stringify(user));

            // Update UI
            document.getElementById('profileUsername').textContent = username;
            document.getElementById('profileEmail').textContent = email;
            document.getElementById('profileInitial').textContent = username[0].toUpperCase();

            messageDiv.textContent = 'Profile updated successfully!';
            messageDiv.style.display = 'block';
        } else {
            errorDiv.textContent = data.message || 'Update failed';
            errorDiv.style.display = 'block';
        }
    } catch (error) {
        errorDiv.textContent = 'Connection error';
        errorDiv.style.display = 'block';
    }

    submitBtn.classList.remove('loading');
}

async function changePassword(e) {
    e.preventDefault();

    const currentPassword = document.getElementById('currentPassword').value;
    const newPassword = document.getElementById('newPassword').value;
    const confirmNewPassword = document.getElementById('confirmNewPassword').value;
    const submitBtn = e.target.querySelector('button[type="submit"]');
    const messageDiv = document.getElementById('passwordMessage');
    const errorDiv = document.getElementById('passwordError');

    messageDiv.style.display = 'none';
    errorDiv.style.display = 'none';

    if (newPassword !== confirmNewPassword) {
        errorDiv.textContent = 'Passwords do not match';
        errorDiv.style.display = 'block';
        return;
    }

    submitBtn.classList.add('loading');

    try {
        const response = await fetch(`${API_URL}/change-password`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': sessionToken
            },
            body: JSON.stringify({
                current_password: currentPassword,
                new_password: newPassword
            })
        });

        const data = await response.json();

        if (data.success) {
            messageDiv.textContent = 'Password changed successfully!';
            messageDiv.style.display = 'block';
            e.target.reset();
        } else {
            errorDiv.textContent = data.message || 'Password change failed';
            errorDiv.style.display = 'block';
        }
    } catch (error) {
        errorDiv.textContent = 'Connection error';
        errorDiv.style.display = 'block';
    }

    submitBtn.classList.remove('loading');
}

async function deleteAccount() {
    if (!confirm('Are you sure you want to delete your account? This action cannot be undone!')) {
        return;
    }

    if (!confirm('This will permanently delete all your data. Are you absolutely sure?')) {
        return;
    }

    try {
        const response = await fetch(`${API_URL}/delete-account`, {
            method: 'DELETE',
            headers: {
                'Authorization': sessionToken
            }
        });

        const data = await response.json();

        if (data.success) {
            alert('Account deleted successfully');
            localStorage.removeItem('session_token');
            localStorage.removeItem('user');
            window.location.href = 'index.html';
        } else {
            alert('Failed to delete account');
        }
    } catch (error) {
        alert('Connection error');
    }
}
