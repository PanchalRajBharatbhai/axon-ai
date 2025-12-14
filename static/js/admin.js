// Admin Panel JavaScript for Axon AI
// Handles all admin panel functionality

const API_BASE = window.location.origin;
let sessionToken = localStorage.getItem('session_token');
let currentUser = null;
let charts = {};

// ============================================================================
// Initialization
// ============================================================================

document.addEventListener('DOMContentLoaded', () => {
    // Check authentication and admin status
    checkAdminAuth();

    // Setup event listeners
    setupEventListeners();

    // Load initial data
    loadDashboard();
});

async function checkAdminAuth() {
    if (!sessionToken) {
        window.location.href = '/index.html';
        return;
    }

    try {
        const response = await fetch(`${API_BASE}/api/user`, {
            headers: {
                'Authorization': sessionToken
            }
        });

        const data = await response.json();

        if (!data.success) {
            localStorage.removeItem('session_token');
            window.location.href = '/index.html';
            return;
        }

        currentUser = data.user;

        // Check if user is admin
        if (!currentUser.is_admin) {
            alert('Access denied. Admin privileges required.');
            window.location.href = '/chat.html';
            return;
        }

        // Update UI with user info
        document.getElementById('adminUsername').textContent = currentUser.username;
        document.getElementById('userAvatar').textContent = currentUser.username.charAt(0).toUpperCase();

        // Show create admin section if SuperAdmin
        if (currentUser.is_superadmin) {
            const createAdminCard = document.getElementById('createAdminCard');
            if (createAdminCard) {
                createAdminCard.style.display = 'block';
            }
        }

    } catch (error) {
        console.error('Auth check failed:', error);
        window.location.href = '/index.html';
    }
}

function setupEventListeners() {
    // Navigation
    document.querySelectorAll('.nav-item[data-section]').forEach(item => {
        item.addEventListener('click', (e) => {
            e.preventDefault();
            const section = item.dataset.section;
            if (section) {
                switchSection(section);
            }
        });
    });

    // Profile links (sidebar and dropdown)
    const profileLink = document.getElementById('profileLink');
    const dropdownProfileLink = document.getElementById('dropdownProfileLink');

    if (profileLink) {
        profileLink.addEventListener('click', (e) => {
            e.preventDefault();
            window.location.href = 'admin-profile.html';
        });
    }

    if (dropdownProfileLink) {
        dropdownProfileLink.addEventListener('click', (e) => {
            e.preventDefault();
            window.location.href = 'admin-profile.html';
        });
    }

    // Settings links (dropdown)
    const dropdownSettingsLink = document.getElementById('dropdownSettingsLink');
    if (dropdownSettingsLink) {
        dropdownSettingsLink.addEventListener('click', (e) => {
            e.preventDefault();
            switchSection('settings');
            // Close dropdown
            document.getElementById('adminProfileMenu').classList.remove('active');
        });
    }

    // Sidebar toggle for mobile
    const sidebarToggle = document.getElementById('sidebarToggle');
    const adminSidebar = document.getElementById('adminSidebar');
    const adminContainer = document.querySelector('.admin-container');

    if (sidebarToggle && adminSidebar) {
        sidebarToggle.addEventListener('click', () => {
            adminSidebar.classList.toggle('mobile-open');
            adminContainer.classList.toggle('sidebar-open');
        });

        // Close sidebar when clicking backdrop on mobile
        if (adminContainer) {
            adminContainer.addEventListener('click', (e) => {
                if (e.target === adminContainer && adminSidebar.classList.contains('mobile-open')) {
                    adminSidebar.classList.remove('mobile-open');
                    adminContainer.classList.remove('sidebar-open');
                }
            });
        }

        // Close sidebar when clicking nav items on mobile
        document.querySelectorAll('.nav-item').forEach(item => {
            item.addEventListener('click', () => {
                if (window.innerWidth <= 1024) {
                    adminSidebar.classList.remove('mobile-open');
                    adminContainer.classList.remove('sidebar-open');
                }
            });
        });
    }

    // Dropdown menu toggle
    const adminProfileTrigger = document.getElementById('adminProfileTrigger');
    const adminProfileMenu = document.getElementById('adminProfileMenu');

    if (adminProfileTrigger && adminProfileMenu) {
        adminProfileTrigger.addEventListener('click', (e) => {
            e.stopPropagation();
            adminProfileMenu.classList.toggle('active');
        });

        // Close dropdown when clicking outside
        document.addEventListener('click', (e) => {
            if (!adminProfileMenu.contains(e.target)) {
                adminProfileMenu.classList.remove('active');
            }
        });
    }

    // Logout
    const logoutBtn = document.getElementById('logoutBtn');
    if (logoutBtn) {
        logoutBtn.addEventListener('click', (e) => {
            e.preventDefault();
            logout();
        });
    }

    // Refresh buttons
    const refreshUsersBtn = document.getElementById('refreshUsersBtn');
    if (refreshUsersBtn) {
        refreshUsersBtn.addEventListener('click', loadUsers);
    }

    const refreshLogsBtn = document.getElementById('refreshLogsBtn');
    if (refreshLogsBtn) {
        refreshLogsBtn.addEventListener('click', loadActivityLogs);
    }

    // Save settings button
    const saveSettingsBtn = document.getElementById('saveSettingsBtn');
    if (saveSettingsBtn) {
        saveSettingsBtn.addEventListener('click', saveSettings);
    }

    // User search
    const userSearch = document.getElementById('userSearch');
    if (userSearch) {
        userSearch.addEventListener('input', filterUsers);
    }

    // Global search
    const globalSearch = document.getElementById('globalSearch');
    if (globalSearch) {
        globalSearch.addEventListener('input', performGlobalSearch);
        globalSearch.addEventListener('focus', () => {
            const resultsDiv = document.getElementById('searchResults');
            if (resultsDiv && resultsDiv.innerHTML) {
                resultsDiv.style.display = 'block';
            }
        });
    }

    // Log filter
    const logFilter = document.getElementById('logFilter');
    if (logFilter) {
        logFilter.addEventListener('change', loadActivityLogs);
    }
}

// Global Search Function
function performGlobalSearch() {
    const searchTerm = document.getElementById('globalSearch').value.toLowerCase().trim();

    // Create or get search results dropdown
    let resultsDiv = document.getElementById('searchResults');
    if (!resultsDiv) {
        resultsDiv = document.createElement('div');
        resultsDiv.id = 'searchResults';
        resultsDiv.className = 'search-results-dropdown';
        document.querySelector('.topbar-search').appendChild(resultsDiv);
    }

    if (!searchTerm) {
        resultsDiv.style.display = 'none';
        resultsDiv.innerHTML = '';
        return;
    }

    const results = [];

    // Search in navigation items
    const navItems = [
        { name: 'Dashboard', icon: '📊', section: 'dashboard' },
        { name: 'Users', icon: '👥', section: 'users' },
        { name: 'Analytics', icon: '📈', section: 'analytics' },
        { name: 'Activity Logs', icon: '📋', section: 'logs' },
        { name: 'Settings', icon: '⚙️', section: 'settings' }
    ];

    navItems.forEach(item => {
        if (item.name.toLowerCase().includes(searchTerm)) {
            results.push({
                type: 'section',
                icon: item.icon,
                title: item.name,
                action: () => switchSection(item.section)
            });
        }
    });

    // Search in features
    const features = [
        { name: 'User Management', icon: '👥', section: 'users', desc: 'Manage users, promote admins' },
        { name: 'Message Analytics', icon: '💬', section: 'dashboard', desc: 'View message trends' },
        { name: 'Language Stats', icon: '🌐', section: 'dashboard', desc: 'Language distribution' },
        { name: 'Activity Monitoring', icon: '📋', section: 'logs', desc: 'Track user activities' },
        { name: 'Registration Trends', icon: '📊', section: 'analytics', desc: 'New user signups' },
        { name: 'Mode Usage', icon: '🎙️', section: 'analytics', desc: 'Text vs Voice usage' }
    ];

    features.forEach(feature => {
        if (feature.name.toLowerCase().includes(searchTerm) || feature.desc.toLowerCase().includes(searchTerm)) {
            results.push({
                type: 'feature',
                icon: feature.icon,
                title: feature.name,
                subtitle: feature.desc,
                action: () => switchSection(feature.section)
            });
        }
    });

    // Search in dashboard stats
    const stats = [
        { name: 'Total Users', icon: '👥', section: 'dashboard' },
        { name: 'Active Users', icon: '✅', section: 'dashboard' },
        { name: 'Total Messages', icon: '💬', section: 'dashboard' },
        { name: 'Messages Today', icon: '📅', section: 'dashboard' }
    ];

    stats.forEach(stat => {
        if (stat.name.toLowerCase().includes(searchTerm)) {
            results.push({
                type: 'stat',
                icon: stat.icon,
                title: stat.name,
                action: () => switchSection(stat.section)
            });
        }
    });

    // Display results
    if (results.length === 0) {
        resultsDiv.innerHTML = '<div class="search-result-item no-results">No results found</div>';
        resultsDiv.style.display = 'block';
    } else {
        resultsDiv.innerHTML = results.map((result, index) => `
            <div class="search-result-item" data-result-index="${index}">
                <span class="result-icon">${result.icon}</span>
                <div class="result-content">
                    <div class="result-title">${result.title}</div>
                    ${result.subtitle ? `<div class="result-subtitle">${result.subtitle}</div>` : ''}
                </div>
                <span class="result-type">${result.type}</span>
            </div>
        `).join('');
        resultsDiv.style.display = 'block';

        // Add click handlers to results
        resultsDiv.querySelectorAll('.search-result-item').forEach((item, index) => {
            item.addEventListener('click', () => {
                results[index].action();
                resultsDiv.style.display = 'none';
                document.getElementById('globalSearch').value = '';
            });
        });
    }
}

// Close search results when clicking outside
document.addEventListener('click', (e) => {
    const searchResults = document.getElementById('searchResults');
    const globalSearch = document.getElementById('globalSearch');
    if (searchResults && globalSearch && !e.target.closest('.topbar-search')) {
        searchResults.style.display = 'none';
    }
});


function switchSection(section) {
    // Update navigation
    document.querySelectorAll('.nav-item').forEach(item => {
        item.classList.remove('active');
    });
    document.querySelector(`[data-section="${section}"]`).classList.add('active');

    // Update content
    document.querySelectorAll('.content-section').forEach(sec => {
        sec.classList.remove('active');
    });
    document.getElementById(`${section}-section`).classList.add('active');

    // Update page title
    const titles = {
        'dashboard': 'Dashboard',
        'users': 'User Management',
        'analytics': 'Analytics & Insights',
        'logs': 'Activity Logs',
        'settings': 'System Settings'
    };
    document.getElementById('pageTitle').textContent = titles[section];

    // Load section data
    switch (section) {
        case 'dashboard':
            loadDashboard();
            break;
        case 'users':
            loadUsers();
            break;
        case 'analytics':
            loadAnalytics();
            break;
        case 'logs':
            loadActivityLogs();
            break;
        case 'settings':
            loadSettings();
            break;
    }
}

async function logout() {
    try {
        await fetch(`${API_BASE}/api/logout`, {
            method: 'POST',
            headers: {
                'Authorization': sessionToken
            }
        });
    } catch (error) {
        console.error('Logout error:', error);
    }

    localStorage.removeItem('session_token');
    window.location.href = '/index.html';
}

// ============================================================================
// Dashboard Functions
// ============================================================================

async function loadDashboard() {
    try {
        const response = await fetch(`${API_BASE}/api/admin/analytics`, {
            headers: {
                'Authorization': sessionToken
            }
        });

        const data = await response.json();

        if (data.success) {
            const analytics = data.analytics;

            // Update stats cards
            document.getElementById('totalUsers').textContent = analytics.overview.total_users;
            document.getElementById('activeUsers').textContent = analytics.overview.active_users;
            document.getElementById('totalMessages').textContent = analytics.overview.total_messages;
            document.getElementById('messagesToday').textContent = analytics.overview.messages_today;

            // Create charts
            createMessageTrendChart(analytics.message_trend);
            createLanguageChart(analytics.language_stats);
        }
    } catch (error) {
        console.error('Failed to load dashboard:', error);
    }
}

function createMessageTrendChart(data) {
    const ctx = document.getElementById('messageTrendChart');
    if (!ctx) return;

    // Destroy existing chart
    if (charts.messageTrend) {
        charts.messageTrend.destroy();
    }

    charts.messageTrend = new Chart(ctx, {
        type: 'line',
        data: {
            labels: data.map(d => d.date),
            datasets: [{
                label: 'Messages',
                data: data.map(d => d.count),
                borderColor: '#4F81BD',
                backgroundColor: 'rgba(79, 129, 189, 0.1)',
                tension: 0.4,
                fill: true
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    labels: {
                        color: '#ffffff'
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        color: '#b8b8b8'
                    },
                    grid: {
                        color: '#2d3561'
                    }
                },
                x: {
                    ticks: {
                        color: '#b8b8b8'
                    },
                    grid: {
                        color: '#2d3561'
                    }
                }
            }
        }
    });
}

function createLanguageChart(data) {
    const ctx = document.getElementById('languageChart');
    if (!ctx) return;

    // Destroy existing chart
    if (charts.language) {
        charts.language.destroy();
    }

    charts.language = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: data.map(d => d.language.toUpperCase()),
            datasets: [{
                data: data.map(d => d.count),
                backgroundColor: [
                    '#4F81BD',
                    '#6C5CE7',
                    '#00B894',
                    '#FDCB6E',
                    '#D63031'
                ]
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        color: '#ffffff'
                    }
                }
            }
        }
    });
}

function refreshDashboard() {
    loadDashboard();
}

// ============================================================================
// User Management Functions
// ============================================================================

async function loadUsers() {
    try {
        const response = await fetch(`${API_BASE}/api/admin/users`, {
            headers: {
                'Authorization': sessionToken
            }
        });

        const data = await response.json();

        if (data.success) {
            displayUsers(data.users);
        }
    } catch (error) {
        console.error('Failed to load users:', error);
    }
}

function displayUsers(users) {
    const tbody = document.getElementById('usersTableBody');

    if (users.length === 0) {
        tbody.innerHTML = '<tr><td colspan="8" class="loading">No users found</td></tr>';
        return;
    }

    tbody.innerHTML = users.map(user => `
        <tr>
            <td>${user.id}</td>
            <td>
                ${user.username}
                ${user.is_superadmin ? '<span style="margin-left: 8px;">👑</span>' : ''}
            </td>
            <td>${user.email}</td>
            <td>
                <span class="badge ${user.is_admin ? 'badge-success' : 'badge-info'}">
                    ${user.is_admin ? 'Yes' : 'No'}
                </span>
            </td>
            <td>
                <span class="badge ${user.is_active ? 'badge-success' : 'badge-danger'}">
                    ${user.is_active ? 'Active' : 'Banned'}
                </span>
            </td>
            <td>${new Date(user.created_at).toLocaleDateString()}</td>
            <td>${user.last_login ? new Date(user.last_login).toLocaleDateString() : 'Never'}</td>
            <td>
                <div class="table-actions">
                    ${!user.is_superadmin ? `
                        <button class="table-btn table-btn-toggle" onclick="toggleAdmin(${user.id})">
                            ${user.is_admin ? '⬇️ Demote' : '⬆️ Promote'}
                        </button>
                        <button class="table-btn table-btn-toggle" onclick="toggleActive(${user.id})">
                            ${user.is_active ? '🚫 Ban' : '✅ Unban'}
                        </button>
                        <button class="table-btn table-btn-delete" onclick="deleteUser(${user.id})">🗑️ Delete</button>
                    ` : `
                        <span class="badge badge-success">SuperAdmin</span>
                    `}
                </div>
            </td>
        </tr>
    `).join('');
}

function filterUsers() {
    const searchTerm = document.getElementById('userSearch').value.toLowerCase();
    const rows = document.querySelectorAll('#usersTableBody tr');

    rows.forEach(row => {
        const text = row.textContent.toLowerCase();
        row.style.display = text.includes(searchTerm) ? '' : 'none';
    });
}

async function editUser(userId) {
    try {
        const response = await fetch(`${API_BASE}/api/admin/users/${userId}`, {
            headers: {
                'Authorization': sessionToken
            }
        });

        const data = await response.json();

        if (data.success) {
            document.getElementById('editUserId').value = userId;
            document.getElementById('editUsername').value = data.user.username;
            document.getElementById('editEmail').value = data.user.email;

            document.getElementById('editUserModal').classList.add('active');
        }
    } catch (error) {
        console.error('Failed to load user:', error);
    }
}

async function saveUserEdit() {
    const userId = document.getElementById('editUserId').value;
    const username = document.getElementById('editUsername').value;
    const email = document.getElementById('editEmail').value;

    try {
        const response = await fetch(`${API_BASE}/api/admin/users/${userId}`, {
            method: 'PUT',
            headers: {
                'Authorization': sessionToken,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ username, email })
        });

        const data = await response.json();

        if (data.success) {
            closeModal('editUserModal');
            loadUsers();
            alert('User updated successfully!');
        } else {
            alert('Failed to update user: ' + data.message);
        }
    } catch (error) {
        console.error('Failed to update user:', error);
        alert('Failed to update user');
    }
}

async function toggleAdmin(userId) {
    if (!confirm('Are you sure you want to toggle admin status for this user?')) {
        return;
    }

    try {
        const response = await fetch(`${API_BASE}/api/admin/users/${userId}/toggle-admin`, {
            method: 'POST',
            headers: {
                'Authorization': sessionToken
            }
        });

        const data = await response.json();

        if (data.success) {
            loadUsers();
            alert(`User ${data.is_admin ? 'promoted to' : 'demoted from'} admin!`);
        } else {
            alert('Failed: ' + data.message);
        }
    } catch (error) {
        console.error('Failed to toggle admin:', error);
    }
}

async function toggleActive(userId) {
    if (!confirm('Are you sure you want to toggle active status for this user?')) {
        return;
    }

    try {
        const response = await fetch(`${API_BASE}/api/admin/users/${userId}/toggle-active`, {
            method: 'POST',
            headers: {
                'Authorization': sessionToken
            }
        });

        const data = await response.json();

        if (data.success) {
            loadUsers();
            alert(`User ${data.is_active ? 'unbanned' : 'banned'} successfully!`);
        } else {
            alert('Failed: ' + data.message);
        }
    } catch (error) {
        console.error('Failed to toggle active:', error);
    }
}

async function deleteUser(userId) {
    if (!confirm('Are you sure you want to delete this user? This action cannot be undone!')) {
        return;
    }

    try {
        const response = await fetch(`${API_BASE}/api/admin/users/${userId}`, {
            method: 'DELETE',
            headers: {
                'Authorization': sessionToken
            }
        });

        const data = await response.json();

        if (data.success) {
            loadUsers();
            alert('User deleted successfully!');
        } else {
            alert('Failed to delete user: ' + data.message);
        }
    } catch (error) {
        console.error('Failed to delete user:', error);
    }
}

// ============================================================================
// Analytics Functions
// ============================================================================

async function loadAnalytics() {
    try {
        const response = await fetch(`${API_BASE}/api/admin/analytics`, {
            headers: {
                'Authorization': sessionToken
            }
        });

        const data = await response.json();

        if (data.success) {
            const analytics = data.analytics;

            createRegistrationChart(analytics.registration_trend);
            createModeChart(analytics.mode_stats);
            createCommandsChart(analytics.popular_commands);
        }
    } catch (error) {
        console.error('Failed to load analytics:', error);
    }
}

function createRegistrationChart(data) {
    const ctx = document.getElementById('registrationChart');
    if (!ctx) return;

    if (charts.registration) {
        charts.registration.destroy();
    }

    charts.registration = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: data.map(d => d.date),
            datasets: [{
                label: 'New Users',
                data: data.map(d => d.count),
                backgroundColor: '#4F81BD'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    labels: {
                        color: '#ffffff'
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        color: '#b8b8b8',
                        stepSize: 1
                    },
                    grid: {
                        color: '#2d3561'
                    }
                },
                x: {
                    ticks: {
                        color: '#b8b8b8'
                    },
                    grid: {
                        color: '#2d3561'
                    }
                }
            }
        }
    });
}

function createModeChart(data) {
    const ctx = document.getElementById('modeChart');
    if (!ctx) return;

    if (charts.mode) {
        charts.mode.destroy();
    }

    charts.mode = new Chart(ctx, {
        type: 'pie',
        data: {
            labels: data.map(d => d.mode.toUpperCase()),
            datasets: [{
                data: data.map(d => d.count),
                backgroundColor: ['#4F81BD', '#6C5CE7', '#00B894']
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        color: '#ffffff'
                    }
                }
            }
        }
    });
}

function createCommandsChart(data) {
    const ctx = document.getElementById('commandsChart');
    if (!ctx) return;

    if (charts.commands) {
        charts.commands.destroy();
    }

    charts.commands = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: data.map(d => d.command),
            datasets: [{
                label: 'Usage Count',
                data: data.map(d => d.count),
                backgroundColor: '#6C5CE7'
            }]
        },
        options: {
            indexAxis: 'y',
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    labels: {
                        color: '#ffffff'
                    }
                }
            },
            scales: {
                x: {
                    beginAtZero: true,
                    ticks: {
                        color: '#b8b8b8'
                    },
                    grid: {
                        color: '#2d3561'
                    }
                },
                y: {
                    ticks: {
                        color: '#b8b8b8'
                    },
                    grid: {
                        color: '#2d3561'
                    }
                }
            }
        }
    });
}

// ============================================================================
// Activity Logs Functions
// ============================================================================

async function loadActivityLogs() {
    const filter = document.getElementById('logFilter').value;

    try {
        const response = await fetch(`${API_BASE}/api/admin/activity-logs?limit=100`, {
            headers: {
                'Authorization': sessionToken
            }
        });

        const data = await response.json();

        if (data.success) {
            let logs = data.logs;

            // Apply filter
            if (filter) {
                logs = logs.filter(log => log.action.includes(filter));
            }

            displayLogs(logs);
        }
    } catch (error) {
        console.error('Failed to load logs:', error);
    }
}

function displayLogs(logs) {
    const tbody = document.getElementById('logsTableBody');

    if (logs.length === 0) {
        tbody.innerHTML = '<tr><td colspan="6" class="loading">No logs found</td></tr>';
        return;
    }

    tbody.innerHTML = logs.map(log => `
        <tr>
            <td>${log.id}</td>
            <td>${log.username || 'System'}</td>
            <td><span class="badge badge-info">${log.action}</span></td>
            <td>${log.details || '-'}</td>
            <td>${log.ip_address || '-'}</td>
            <td>${new Date(log.timestamp).toLocaleString()}</td>
        </tr>
    `).join('');
}

// ============================================================================
// Settings Functions
// ============================================================================

async function loadSettings() {
    try {
        const response = await fetch(`${API_BASE}/api/admin/settings`, {
            headers: {
                'Authorization': sessionToken
            }
        });

        const data = await response.json();

        if (data.success && data.settings.length > 0) {
            data.settings.forEach(setting => {
                const element = document.getElementById(setting.key);
                if (element) {
                    if (element.type === 'checkbox') {
                        element.checked = setting.value === 'true';
                    } else {
                        element.value = setting.value;
                    }
                }
            });
        }
    } catch (error) {
        console.error('Failed to load settings:', error);
    }
}

async function saveSettings() {
    const settings = [];

    // Only add settings if the elements exist
    const systemNameEl = document.getElementById('systemName');
    const defaultLanguageEl = document.getElementById('defaultLanguage');

    if (systemNameEl) {
        settings.push({ key: 'systemName', value: systemNameEl.value });
    }

    if (defaultLanguageEl) {
        settings.push({ key: 'defaultLanguage', value: defaultLanguageEl.value });
    }

    try {
        for (const setting of settings) {
            const response = await fetch(`${API_BASE}/api/admin/settings`, {
                method: 'POST',
                headers: {
                    'Authorization': sessionToken,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(setting)
            });

            const data = await response.json();
            if (!data.success) {
                throw new Error(data.message || 'Failed to save setting');
            }
        }

        showToast('Settings saved successfully!', 'success');
    } catch (error) {
        console.error('Failed to save settings:', error);
        showToast('Failed to save settings: ' + error.message, 'error');
    }
}

function backupDatabase() {
    alert('Database backup functionality will be implemented in a future update.');
}

function clearOldLogs() {
    if (confirm('Are you sure you want to clear old activity logs?')) {
        alert('Clear old logs functionality will be implemented in a future update.');
    }
}

async function createNewAdmin() {
    const username = document.getElementById('newAdminUsername').value.trim();
    const email = document.getElementById('newAdminEmail').value.trim();
    const password = document.getElementById('newAdminPassword').value;

    if (!username || !email || !password) {
        alert('Please fill in all fields');
        return;
    }

    if (!confirm(`Create admin account for ${username}?`)) {
        return;
    }

    try {
        const response = await fetch(`${API_BASE}/api/admin/create-admin`, {
            method: 'POST',
            headers: {
                'Authorization': sessionToken,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ username, email, password })
        });

        const data = await response.json();

        if (data.success) {
            alert('Admin account created successfully!');
            // Clear form
            document.getElementById('newAdminUsername').value = '';
            document.getElementById('newAdminEmail').value = '';
            document.getElementById('newAdminPassword').value = '';
        } else {
            alert('Failed to create admin: ' + data.message);
        }
    } catch (error) {
        console.error('Failed to create admin:', error);
        alert('Failed to create admin account');
    }
}

// ============================================================================
// Export Functions
// ============================================================================

async function exportData(type, format) {
    let endpoint = '';
    let filename = '';

    switch (type) {
        case 'users':
            endpoint = `/api/admin/export/users?format=${format}`;
            filename = `users_${Date.now()}.${format === 'excel' ? 'xlsx' : 'csv'}`;
            break;
        case 'chat':
            endpoint = '/api/admin/export/chat-history';
            filename = `chat_history_${Date.now()}.xlsx`;
            break;
        case 'logs':
            endpoint = `/api/admin/export/activity-logs?format=${format}`;
            filename = `activity_logs_${Date.now()}.${format === 'excel' ? 'xlsx' : 'csv'}`;
            break;
        case 'analytics':
            endpoint = '/api/admin/export/analytics';
            filename = `analytics_report_${Date.now()}.pdf`;
            break;
        default:
            alert('Invalid export type');
            return;
    }

    try {
        const response = await fetch(`${API_BASE}${endpoint}`, {
            headers: {
                'Authorization': sessionToken
            }
        });

        if (!response.ok) {
            const error = await response.json();
            alert('Export failed: ' + error.message);
            return;
        }

        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);

        alert('Export completed successfully!');
    } catch (error) {
        console.error('Export failed:', error);
        alert('Export failed. Please make sure required libraries are installed.');
    }
}

// ============================================================================
// Modal Functions
// ============================================================================

function closeModal(modalId) {
    document.getElementById(modalId).classList.remove('active');
}

// Close modal when clicking outside
window.addEventListener('click', (e) => {
    if (e.target.classList.contains('modal')) {
        e.target.classList.remove('active');
    }
});

// ============================================================================
// Toast Notification Function
// ============================================================================

function showToast(message, type = 'info') {
    const toastContainer = document.getElementById('toastContainer');

    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;

    const icon = type === 'success' ? '✓' : type === 'error' ? '✕' : 'ℹ';

    toast.innerHTML = `
        <div class="toast-icon">${icon}</div>
        <div class="toast-content">
            <div class="toast-message">${message}</div>
        </div>
        <button class="toast-close" onclick="this.parentElement.remove()">✕</button>
    `;

    toastContainer.appendChild(toast);

    setTimeout(() => {
        toast.style.animation = 'slideOutRight 0.3s ease-out';
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}
