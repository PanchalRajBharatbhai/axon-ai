# -*- coding: utf-8 -*-
"""
Flask Backend API for Axon AI Web Interface
Provides REST API and WebSocket support for the chat interface
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from web_database import WebDatabase
from ai_integration import AIBridge
from functools import wraps
import os
import smtplib
from email.message import EmailMessage
import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'axon-ai-secret-key-change-in-production'
CORS(app)

# Initialize SocketIO (will auto-detect best async mode)
# Supports: eventlet, gevent, threading (in order of preference)

# Initialize database and AI bridge
db = WebDatabase()
ai_bridge = AIBridge()

# Store active sessions
active_sessions = {}


# ============================================================================
# Static File Routes
# ============================================================================
app = Flask(
    __name__,
    static_folder="static",
    static_url_path=""
)

@app.route("/")
def index():
    return app.send_static_file("index.html")

@app.route("/login")
def login_page():
    return app.send_static_file("login.html")

@app.route("/privacy-policy")
def privacy_policy():
    return app.send_static_file("privacy-policy.html")

# ============================================================================
# Admin Authentication Middleware
# ============================================================================

def admin_required(f):
    """Decorator to require admin authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        session_token = request.headers.get('Authorization')
        
        if not session_token:
            return jsonify({'success': False, 'message': 'Not authenticated'}), 401
        
        session = db.verify_session(session_token)
        
        if not session['valid']:
            return jsonify({'success': False, 'message': 'Invalid session'}), 401
        
        # Check if user is admin
        user_result = db.get_user_by_id(session['user']['id'])
        if not user_result['success'] or not user_result['user']['is_admin']:
            return jsonify({'success': False, 'message': 'Admin access required'}), 403
        
        # Pass user info to the route
        return f(session['user'], *args, **kwargs)
    
    return decorated_function


# ============================================================================
# Authentication API
# ============================================================================

@app.route('/api/register', methods=['POST'])
def register():
    """Register a new user"""
    data = request.json
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    
    if not all([username, email, password]):
        return jsonify({'success': False, 'message': 'Missing required fields'}), 400
    
    result = db.create_user(username, email, password)
    
    if result['success']:
        return jsonify(result), 201
    else:
        return jsonify(result), 400


@app.route('/api/login', methods=['POST'])
def login():
    """Login a user"""
    data = request.json
    username = data.get('username')
    password = data.get('password')
    
    if not all([username, password]):
        return jsonify({'success': False, 'message': 'Missing credentials'}), 400
    
    result = db.verify_user(username, password)
    
    if result['success']:
        # Create session
        user_id = result['user']['id']
        session_token = db.create_session(user_id)
        
        # Store in active sessions
        active_sessions[session_token] = result['user']
        
        return jsonify({
            'success': True,
            'session_token': session_token,
            'user': result['user']
        }), 200
    else:
        return jsonify(result), 401


@app.route('/api/admin/login', methods=['POST'])
def admin_login():
    """Admin login with email and password"""
    data = request.json
    email = data.get('email')
    password = data.get('password')
    
    if not all([email, password]):
        return jsonify({'success': False, 'message': 'Missing credentials'}), 400
    
    # Get user by email
    user_result = db.get_user_by_email(email)
    
    if not user_result['success']:
        return jsonify({'success': False, 'message': 'Invalid admin credentials'}), 401
    
    # Verify password
    username = user_result['user']['username']
    verify_result = db.verify_user(username, password)
    
    if not verify_result['success']:
        return jsonify({'success': False, 'message': 'Invalid admin credentials'}), 401
    
    user = verify_result['user']
    
    # Check if user is admin
    if not user.get('is_admin'):
        return jsonify({'success': False, 'message': 'Invalid admin credentials'}), 403
    
    # Create session
    user_id = user['id']
    session_token = db.create_session(user_id)
    
    # Store in active sessions
    active_sessions[session_token] = user
    
    # Log activity
    db.log_activity(user_id, 'ADMIN_LOGIN', f'Admin logged in via email: {email}')
    
    return jsonify({
        'success': True,
        'session_token': session_token,
        'user': user
    }), 200


@app.route('/api/admin/create-admin', methods=['POST'])
def create_admin():
    """Create a new admin account (SuperAdmin only)"""
    session_token = request.headers.get('Authorization')
    
    if not session_token:
        return jsonify({'success': False, 'message': 'Not authenticated'}), 401
    
    session = db.verify_session(session_token)
    
    if not session['valid']:
        return jsonify({'success': False, 'message': 'Invalid session'}), 401
    
    # Get requester details
    requester_id = session['user']['id']
    user_result = db.get_user_by_id(requester_id)
    
    if not user_result['success'] or not user_result['user']['is_superadmin']:
        return jsonify({'success': False, 'message': 'Unauthorized to create admin accounts'}), 403
    
    # Get new admin details
    data = request.json
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    
    if not all([username, email, password]):
        return jsonify({'success': False, 'message': 'Missing required fields: name, email, password'}), 400
    
    # Create admin user
    result = db.create_admin_user(requester_id, username, email, password)
    
    if result['success']:
        # Log activity
        db.log_activity(requester_id, 'CREATE_ADMIN', f'Created admin account: {username}')
        return jsonify(result), 201
    else:
        return jsonify(result), 400


@app.route('/api/logout', methods=['POST'])
def logout():
    """Logout a user"""
    session_token = request.headers.get('Authorization')
    
    if session_token:
        db.delete_session(session_token)
        if session_token in active_sessions:
            del active_sessions[session_token]
        
        return jsonify({'success': True, 'message': 'Logged out successfully'}), 200
    else:
        return jsonify({'success': False, 'message': 'No session token provided'}), 400


@app.route('/api/user', methods=['GET'])
def get_user():
    """Get current user info"""
    session_token = request.headers.get('Authorization')
    
    if not session_token:
        return jsonify({'success': False, 'message': 'Not authenticated'}), 401
    
    session = db.verify_session(session_token)
    
    if session['valid']:
        return jsonify({'success': True, 'user': session['user']}), 200
    else:
        return jsonify({'success': False, 'message': 'Invalid session'}), 401


# ============================================================================
# Chat History API
# ============================================================================

@app.route('/api/history', methods=['GET'])
def get_history():
    """Get chat history for current user"""
    session_token = request.headers.get('Authorization')
    
    if not session_token:
        return jsonify({'success': False, 'message': 'Not authenticated'}), 401
    
    session = db.verify_session(session_token)
    
    if session['valid']:
        user_id = session['user']['id']
        limit = request.args.get('limit', 50, type=int)
        
        history = db.get_chat_history(user_id, limit)
        
        return jsonify({'success': True, 'history': history}), 200
    else:
        return jsonify({'success': False, 'message': 'Invalid session'}), 401


@app.route('/api/history', methods=['DELETE'])
def clear_history():
    """Clear chat history for current user"""
    session_token = request.headers.get('Authorization')
    
    if not session_token:
        return jsonify({'success': False, 'message': 'Not authenticated'}), 401
    
    session = db.verify_session(session_token)
    
    if session['valid']:
        user_id = session['user']['id']
        rows_deleted = db.clear_chat_history(user_id)
        
        return jsonify({
            'success': True,
            'message': f'Cleared {rows_deleted} messages'
        }), 200
    else:
        return jsonify({'success': False, 'message': 'Invalid session'}), 401


# ============================================================================
# Forgot Password & Profile Management API
# ============================================================================

@app.route('/api/forgot-password', methods=['POST'])
def forgot_password():
    """Verify email for password reset"""
    data = request.json
    email = data.get('email')
    
    if not email:
        return jsonify({'success': False, 'message': 'Email required'}), 400
    
    result = db.get_user_by_email(email)
    
    if result['success']:
        return jsonify({'success': True, 'message': 'Email verified'}), 200
    else:
        return jsonify({'success': False, 'message': 'Email not found'}), 404


@app.route('/api/reset-password', methods=['POST'])
def reset_password():
    """Reset user password"""
    data = request.json
    email = data.get('email')
    new_password = data.get('new_password')
    
    if not all([email, new_password]):
        return jsonify({'success': False, 'message': 'Missing required fields'}), 400
    
    # Get user by email
    user_result = db.get_user_by_email(email)
    
    if user_result['success']:
        user_id = user_result['user']['id']
        # Update password
        result = db.update_password(user_id, new_password)
        return jsonify(result), 200
    else:
        return jsonify({'success': False, 'message': 'User not found'}), 404


@app.route('/api/update-profile', methods=['POST'])
def update_profile():
    """Update user profile"""
    session_token = request.headers.get('Authorization')
    
    if not session_token:
        return jsonify({'success': False, 'message': 'Not authenticated'}), 401
    
    session = db.verify_session(session_token)
    
    if session['valid']:
        data = request.json
        user_id = session['user']['id']
        username = data.get('username')
        email = data.get('email')
        
        # Update user info in database
        conn = db.db_path
        import sqlite3
        connection = sqlite3.connect(conn)
        cursor = connection.cursor()
        
        try:
            cursor.execute('''
                UPDATE users SET username = ?, email = ?
                WHERE id = ?
            ''', (username, email, user_id))
            connection.commit()
            connection.close()
            
            return jsonify({
                'success': True,
                'message': 'Profile updated successfully'
            }), 200
        except sqlite3.IntegrityError:
            connection.close()
            return jsonify({
                'success': False,
                'message': 'Username or email already exists'
            }), 400
    else:
        return jsonify({'success': False, 'message': 'Invalid session'}), 401


@app.route('/api/change-password', methods=['POST'])
def change_password():
    """Change user password"""
    session_token = request.headers.get('Authorization')
    
    if not session_token:
        return jsonify({'success': False, 'message': 'Not authenticated'}), 401
    
    session = db.verify_session(session_token)
    
    if session['valid']:
        data = request.json
        current_password = data.get('current_password')
        new_password = data.get('new_password')
        
        # Verify current password
        username = session['user']['username']
        verify_result = db.verify_user(username, current_password)
        
        if verify_result['success']:
            user_id = session['user']['id']
            result = db.update_password(user_id, new_password)
            return jsonify(result), 200
        else:
            return jsonify({
                'success': False,
                'message': 'Current password is incorrect'
            }), 400
    else:
        return jsonify({'success': False, 'message': 'Invalid session'}), 401


@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get user statistics"""
    session_token = request.headers.get('Authorization')
    
    if not session_token:
        return jsonify({'success': False, 'message': 'Not authenticated'}), 401
    
    session = db.verify_session(session_token)
    
    if session['valid']:
        user_id = session['user']['id']
        stats = db.get_user_stats(user_id)
        
        return jsonify({
            'success': True,
            'stats': stats
        }), 200
    else:
        return jsonify({'success': False, 'message': 'Invalid session'}), 401


@app.route('/api/delete-account', methods=['DELETE'])
def delete_account():
    """Delete user account"""
    session_token = request.headers.get('Authorization')
    
    if not session_token:
        return jsonify({'success': False, 'message': 'Not authenticated'}), 401
    
    session = db.verify_session(session_token)
    
    if session['valid']:
        user_id = session['user']['id']
        
        # Delete user data
        import sqlite3
        conn = sqlite3.connect(db.db_path)
        cursor = conn.cursor()
        
        # Delete chat history
        cursor.execute('DELETE FROM chat_history WHERE user_id = ?', (user_id,))
        # Delete sessions
        cursor.execute('DELETE FROM sessions WHERE user_id = ?', (user_id,))
        # Delete user
        cursor.execute('DELETE FROM users WHERE id = ?', (user_id,))
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': 'Account deleted successfully'
        }), 200
    else:
        return jsonify({'success': False, 'message': 'Invalid session'}), 401


# ============================================================================
# Admin API Endpoints
# ============================================================================

@app.route('/api/admin/users', methods=['GET'])
@admin_required
def admin_get_users(current_user):
    """Get all users (admin only)"""
    include_inactive = request.args.get('include_inactive', 'true').lower() == 'true'
    users = db.get_all_users(include_inactive=include_inactive)
    
    # Log activity
    db.log_activity(current_user['id'], 'VIEW_USERS', f'Viewed {len(users)} users')
    
    return jsonify({'success': True, 'users': users}), 200


@app.route('/api/admin/users/<int:user_id>', methods=['GET'])
@admin_required
def admin_get_user(current_user, user_id):
    """Get specific user details (admin only)"""
    result = db.get_user_by_id(user_id)
    
    if result['success']:
        # Get user stats
        stats = db.get_user_stats(user_id)
        result['user']['stats'] = stats
        
        db.log_activity(current_user['id'], 'VIEW_USER', f'Viewed user {user_id}')
        return jsonify(result), 200
    else:
        return jsonify(result), 404


@app.route('/api/admin/users/<int:user_id>', methods=['PUT'])
@admin_required
def admin_update_user(current_user, user_id):
    """Update user details (admin only)"""
    data = request.json
    username = data.get('username')
    email = data.get('email')
    
    result = db.update_user(user_id, username=username, email=email)
    
    if result['success']:
        db.log_activity(current_user['id'], 'UPDATE_USER', f'Updated user {user_id}')
    
    return jsonify(result), 200 if result['success'] else 400


@app.route('/api/admin/users/<int:user_id>', methods=['DELETE'])
@admin_required
def admin_delete_user(current_user, user_id):
    """Delete user (admin only)"""
    # Prevent self-deletion
    if user_id == current_user['id']:
        return jsonify({'success': False, 'message': 'Cannot delete your own account'}), 400
    
    # Prevent deletion of SuperAdmin
    user_result = db.get_user_by_id(user_id)
    if user_result['success'] and user_result['user'].get('is_superadmin'):
        return jsonify({'success': False, 'message': 'Cannot delete SuperAdmin account'}), 403
    
    result = db.delete_user(user_id)
    
    if result['success']:
        db.log_activity(current_user['id'], 'DELETE_USER', f'Deleted user {user_id}')
    
    return jsonify(result), 200


@app.route('/api/admin/users/<int:user_id>/toggle-admin', methods=['POST'])
@admin_required
def admin_toggle_admin(current_user, user_id):
    """Toggle admin status for user (admin only)"""
    result = db.toggle_admin_status(user_id)
    
    if result['success']:
        action = 'GRANT_ADMIN' if result['is_admin'] else 'REVOKE_ADMIN'
        db.log_activity(current_user['id'], action, f'User {user_id}')
    
    return jsonify(result), 200 if result['success'] else 404


@app.route('/api/admin/users/<int:user_id>/toggle-active', methods=['POST'])
@admin_required
def admin_toggle_active(current_user, user_id):
    """Toggle active status for user (ban/unban) (admin only)"""
    # Prevent self-ban
    if user_id == current_user['id']:
        return jsonify({'success': False, 'message': 'Cannot ban your own account'}), 400
    
    result = db.toggle_active_status(user_id)
    
    if result['success']:
        action = 'UNBAN_USER' if result['is_active'] else 'BAN_USER'
        db.log_activity(current_user['id'], action, f'User {user_id}')
    
    return jsonify(result), 200 if result['success'] else 404


@app.route('/api/admin/analytics', methods=['GET'])
@admin_required
def admin_get_analytics(current_user):
    """Get analytics data (admin only)"""
    analytics = db.get_admin_analytics()
    
    db.log_activity(current_user['id'], 'VIEW_ANALYTICS', 'Viewed dashboard analytics')
    
    return jsonify({'success': True, 'analytics': analytics}), 200


@app.route('/api/admin/activity-logs', methods=['GET'])
@admin_required
def admin_get_activity_logs(current_user):
    """Get activity logs (admin only)"""
    limit = request.args.get('limit', 100, type=int)
    user_id = request.args.get('user_id', type=int)
    
    logs = db.get_activity_logs(limit=limit, user_id=user_id)
    
    return jsonify({'success': True, 'logs': logs}), 200


@app.route('/api/admin/settings', methods=['GET'])
@admin_required
def admin_get_settings(current_user):
    """Get all system settings (admin only)"""
    settings = db.get_all_settings()
    return jsonify({'success': True, 'settings': settings}), 200


@app.route('/api/admin/settings', methods=['POST'])
@admin_required
def admin_update_settings(current_user):
    """Update system settings (admin only)"""
    data = request.json
    key = data.get('key')
    value = data.get('value')
    
    if not key:
        return jsonify({'success': False, 'message': 'Setting key required'}), 400
    
    result = db.set_setting(key, value)
    
    if result['success']:
        db.log_activity(current_user['id'], 'UPDATE_SETTING', f'Updated {key}')
    
    return jsonify(result), 200




# ============================================================================
# Contact Form API
# ============================================================================

@app.route('/api/contact', methods=['POST'])
def contact_form():
    """Handle contact form submissions"""
    data = request.json
    name = data.get('name')
    email = data.get('email')
    message = data.get('message')
    
    if not all([name, email, message]):
        return jsonify({'success': False, 'message': 'All fields are required'}), 400
    
    # Calculate IST time
    ist_now = datetime.datetime.utcnow() + datetime.timedelta(hours=5, minutes=30)
    ist_time_str = ist_now.strftime("%Y-%m-%d %H:%M:%S")
    
    # Email configuration (using environment variables)
    EMAIL_ADDRESS = os.environ.get('EMAIL_ADDRESS')
    EMAIL_PASSWORD = os.environ.get('EMAIL_PASSWORD')
    
    if not EMAIL_ADDRESS or not EMAIL_PASSWORD:
        return jsonify({'success': False, 'message': 'Email configuration missing'}), 500
    
    try:
        # Create email message
        msg = EmailMessage()
        msg['Subject'] = f'New Contact Form Message from {name}'
        msg['From'] = EMAIL_ADDRESS
        msg['To'] = 'rajpanchal342006@gmail.com'
        msg['Reply-To'] = email
        
        content = f"""
New message received from Axon AI Website Contact Form:

Name: {name}
Email: {email}

Message:
{message}

------------------------------------------------
Received at: {ist_time_str} (IST)
"""
        msg.set_content(content)
        
        # Send email
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            smtp.send_message(msg)
            
        # Log to activity log if user is logged in (optional)
        # Store in database as backup (optional but recommended)
        try:
            conn = db.db_path
            import sqlite3
            connection = sqlite3.connect(conn)
            cursor = connection.cursor()
            
            # Create contact_messages table if not exists (simple inline check)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS contact_messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    email TEXT NOT NULL,
                    message TEXT NOT NULL,
                    timestamp DATETIME,
                    status TEXT DEFAULT 'unread'
                )
            ''')
            
            cursor.execute('''
                INSERT INTO contact_messages (name, email, message, timestamp)
                VALUES (?, ?, ?, ?)
            ''', (name, email, message, ist_now))
            
            connection.commit()
            connection.close()
        except Exception as db_error:
            print(f"Database backup error: {db_error}")
            # Don't fail the request if just DB storage fails, since email worked
            
        return jsonify({'success': True, 'message': 'Message sent successfully'}), 200
        
    except Exception as e:
        print(f"Email Error: {e}")
        return jsonify({'success': False, 'message': 'Failed to send message over email. Please try again later.'}), 500

# ============================================================================
# Application Entry Point
# ============================================================================
# For Render deployment: Gunicorn will import 'app' and 'socketio' directly
# No if __name__ == '__main__' block needed for production deployment

