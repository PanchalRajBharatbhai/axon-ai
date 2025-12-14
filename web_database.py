# -*- coding: utf-8 -*-
"""
Web Database Manager for Axon AI
Manages users, chat history, and sessions for the web interface
"""

import sqlite3
import hashlib
import secrets
from datetime import datetime, timedelta
import json

def get_ist_now():
    """Get current time in Indian Standard Time (UTC+5:30)"""
    return datetime.utcnow() + timedelta(hours=5, minutes=30)

class WebDatabase:
    def __init__(self, db_path='web_axon.db'):
        """Initialize the web database"""
        self.db_path = db_path
        self.create_tables()
    
    def create_tables(self):
        """Create all necessary tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                is_admin INTEGER DEFAULT 0,
                is_superadmin INTEGER DEFAULT 0,
                is_active INTEGER DEFAULT 1,
                created_at TIMESTAMP,
                last_login TIMESTAMP
            )
        ''')
        
        # Add columns to existing users table if they don't exist
        try:
            cursor.execute('ALTER TABLE users ADD COLUMN is_admin INTEGER DEFAULT 0')
        except sqlite3.OperationalError:
            pass  # Column already exists
        
        try:
            cursor.execute('ALTER TABLE users ADD COLUMN is_superadmin INTEGER DEFAULT 0')
        except sqlite3.OperationalError:
            pass  # Column already exists
        
        try:
            cursor.execute('ALTER TABLE users ADD COLUMN is_active INTEGER DEFAULT 1')
        except sqlite3.OperationalError:
            pass  # Column already exists
        
        # Chat history table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS chat_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                message TEXT NOT NULL,
                response TEXT NOT NULL,
                mode TEXT DEFAULT 'text',
                language TEXT DEFAULT 'en',
                timestamp TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        ''')
        
        # Sessions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                session_token TEXT UNIQUE NOT NULL,
                created_at TIMESTAMP,
                expires_at TIMESTAMP NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        ''')
        
        # Activity logs table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS activity_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                action TEXT NOT NULL,
                details TEXT,
                ip_address TEXT,
                timestamp TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        ''')
        
        # System settings table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS system_settings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                setting_key TEXT UNIQUE NOT NULL,
                setting_value TEXT,
                updated_at TIMESTAMP
            )
        ''')
        
        # Create indexes for faster lookups
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_username ON users(username)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_email ON users(email)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_session_token ON sessions(session_token)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_chat_user ON chat_history(user_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_activity_user ON activity_logs(user_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_activity_timestamp ON activity_logs(timestamp)')
        
        # Make first user superadmin if no admins exist
        cursor.execute('SELECT COUNT(*) FROM users WHERE is_superadmin = 1')
        superadmin_count = cursor.fetchone()[0]
        if superadmin_count == 0:
            cursor.execute('UPDATE users SET is_admin = 1, is_superadmin = 1 WHERE id = (SELECT MIN(id) FROM users)')
        
        conn.commit()
        conn.close()
        print("[+] Database tables created successfully")
    
    def hash_password(self, password):
        """Hash a password using SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def create_user(self, username, email, password):
        """Create a new user"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Check if this is the first user
            cursor.execute('SELECT COUNT(*) FROM users')
            user_count = cursor.fetchone()[0]
            is_first_user = (user_count == 0)
            
            password_hash = self.hash_password(password)
            created_at = get_ist_now()
            
            if is_first_user:
                # First user becomes SuperAdmin
                cursor.execute('''
                    INSERT INTO users (username, email, password_hash, is_admin, is_superadmin, is_active, created_at)
                    VALUES (?, ?, ?, 1, 1, 1, ?)
                ''', (username, email, password_hash, created_at))
            else:
                # Regular user
                cursor.execute('''
                    INSERT INTO users (username, email, password_hash, created_at)
                    VALUES (?, ?, ?, ?)
                ''', (username, email, password_hash, created_at))
            
            conn.commit()
            user_id = cursor.lastrowid
            conn.close()
            
            if is_first_user:
                return {'success': True, 'user_id': user_id, 'message': 'SuperAdmin account created successfully', 'is_superadmin': True}
            else:
                return {'success': True, 'user_id': user_id, 'message': 'User created successfully'}
        
        except sqlite3.IntegrityError as e:
            conn.close()
            if 'username' in str(e):
                return {'success': False, 'message': 'Username already exists'}
            elif 'email' in str(e):
                return {'success': False, 'message': 'Email already exists'}
            else:
                return {'success': False, 'message': 'User creation failed'}
    
    def create_admin_user(self, requester_id, username, email, password):
        """Create a new admin user (SuperAdmin only)"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Verify requester is SuperAdmin
        cursor.execute('SELECT is_superadmin FROM users WHERE id = ?', (requester_id,))
        result = cursor.fetchone()
        
        if not result or not result[0]:
            conn.close()
            return {'success': False, 'message': 'Unauthorized to create admin accounts'}
        
        try:
            password_hash = self.hash_password(password)
            created_at = get_ist_now()
            
            cursor.execute('''
                INSERT INTO users (username, email, password_hash, is_admin, is_active, created_at)
                VALUES (?, ?, ?, 1, 1, ?)
            ''', (username, email, password_hash, created_at))
            
            conn.commit()
            user_id = cursor.lastrowid
            conn.close()
            return {'success': True, 'user_id': user_id, 'message': 'Admin user created successfully'}
        
        except sqlite3.IntegrityError as e:
            conn.close()
            if 'username' in str(e):
                return {'success': False, 'message': 'Username already exists'}
            elif 'email' in str(e):
                return {'success': False, 'message': 'Email already exists'}
            else:
                return {'success': False, 'message': 'Admin user creation failed'}
    
    def update_password(self, user_id, new_password):
        """Update user password"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        password_hash = self.hash_password(new_password)
        cursor.execute('''
            UPDATE users SET password_hash = ?
            WHERE id = ?
        ''', (password_hash, user_id))
        
        conn.commit()
        conn.close()
        return {'success': True, 'message': 'Password updated successfully'}
    
    def get_user_by_email(self, email):
        """Get user by email"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, username, email, is_admin, is_superadmin, is_active FROM users
            WHERE email = ?
        ''', (email,))
        
        user = cursor.fetchone()
        conn.close()
        
        if user:
            return {
                'success': True,
                'user': {
                    'id': user[0],
                    'username': user[1],
                    'email': user[2],
                    'is_admin': bool(user[3]),
                    'is_superadmin': bool(user[4]),
                    'is_active': bool(user[5])
                }
            }
        else:
            return {'success': False, 'message': 'User not found'}
    
    def verify_user(self, username, password):
        """Verify user credentials"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        password_hash = self.hash_password(password)
        cursor.execute('''
            SELECT id, username, email, is_admin, is_superadmin, is_active FROM users
            WHERE username = ? AND password_hash = ?
        ''', (username, password_hash))
        
        user = cursor.fetchone()
        
        if user:
            # Check if user is active
            if not user[5]:
                conn.close()
                return {'success': False, 'message': 'Account is banned'}
            
            # Update last login
            last_login = get_ist_now()
            cursor.execute('''
                UPDATE users SET last_login = ?
                WHERE id = ?
            ''', (last_login, user[0],))
            conn.commit()
            
            conn.close()
            return {
                'success': True,
                'user': {
                    'id': user[0],
                    'username': user[1],
                    'email': user[2],
                    'is_admin': bool(user[3]),
                    'is_superadmin': bool(user[4]),
                    'is_active': bool(user[5])
                }
            }
        else:
            conn.close()
            return {'success': False, 'message': 'Invalid credentials'}
    
    def create_session(self, user_id, hours=24):
        """Create a new session for a user"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Generate secure session token
        session_token = secrets.token_urlsafe(32)
        created_at = get_ist_now()
        expires_at = created_at + timedelta(hours=hours)
        
        cursor.execute('''
            INSERT INTO sessions (user_id, session_token, created_at, expires_at)
            VALUES (?, ?, ?, ?)
        ''', (user_id, session_token, created_at, expires_at))
        
        conn.commit()
        conn.close()
        
        return session_token
    
    def verify_session(self, session_token):
        """Verify if a session is valid"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        current_time = get_ist_now()
        
        cursor.execute('''
            SELECT s.user_id, u.username, u.email, u.is_admin, u.is_superadmin, u.is_active
            FROM sessions s
            JOIN users u ON s.user_id = u.id
            WHERE s.session_token = ? AND s.expires_at > ?
        ''', (session_token, current_time))
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return {
                'valid': True,
                'user': {
                    'id': result[0],
                    'username': result[1],
                    'email': result[2],
                    'is_admin': bool(result[3]),
                    'is_superadmin': bool(result[4]),
                    'is_active': bool(result[5])
                }
            }
        else:
            return {'valid': False}
    
    def delete_session(self, session_token):
        """Delete a session (logout)"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM sessions WHERE session_token = ?', (session_token,))
        
        conn.commit()
        conn.close()
    
    def add_chat_message(self, user_id, message, response, mode='text', language='en'):
        """Add a chat message to history"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        timestamp = get_ist_now()
        
        cursor.execute('''
            INSERT INTO chat_history (user_id, message, response, mode, language, timestamp)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (user_id, message, response, mode, language, timestamp))
        
        conn.commit()
        message_id = cursor.lastrowid
        conn.close()
        
        return message_id
    
    def get_chat_history(self, user_id, limit=50):
        """Get chat history for a user"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT message, response, mode, language, timestamp
            FROM chat_history
            WHERE user_id = ?
            ORDER BY timestamp DESC
            LIMIT ?
        ''', (user_id, limit))
        
        history = cursor.fetchall()
        conn.close()
        
        return [{
            'message': h[0],
            'response': h[1],
            'mode': h[2],
            'language': h[3],
            'timestamp': h[4]
        } for h in history]
    
    def clear_chat_history(self, user_id):
        """Clear chat history for a user"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM chat_history WHERE user_id = ?', (user_id,))
        
        conn.commit()
        rows_deleted = cursor.rowcount
        conn.close()
        
        return rows_deleted
    
    def get_user_stats(self, user_id):
        """Get statistics for a user"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Total messages
        cursor.execute('SELECT COUNT(*) FROM chat_history WHERE user_id = ?', (user_id,))
        total_messages = cursor.fetchone()[0]
        
        # Messages by mode
        cursor.execute('''
            SELECT mode, COUNT(*) FROM chat_history
            WHERE user_id = ?
            GROUP BY mode
        ''', (user_id,))
        mode_stats = dict(cursor.fetchall())
        
        # Messages by language
        cursor.execute('''
            SELECT language, COUNT(*) FROM chat_history
            WHERE user_id = ?
            GROUP BY language
        ''', (user_id,))
        language_stats = dict(cursor.fetchall())
        
        conn.close()
        
        return {
            'total_messages': total_messages,
            'by_mode': mode_stats,
            'by_language': language_stats
        }
    
    # ============================================================================
    # Admin Methods
    # ============================================================================
    
    def get_all_users(self, include_inactive=True):
        """Get all users (admin only)"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if include_inactive:
            cursor.execute('''
                SELECT id, username, email, is_admin, is_superadmin, is_active, created_at, last_login
                FROM users
                ORDER BY created_at DESC
            ''')
        else:
            cursor.execute('''
                SELECT id, username, email, is_admin, is_superadmin, is_active, created_at, last_login
                FROM users
                WHERE is_active = 1
                ORDER BY created_at DESC
            ''')
        
        users = cursor.fetchall()
        conn.close()
        
        return [{
            'id': u[0],
            'username': u[1],
            'email': u[2],
            'is_admin': bool(u[3]),
            'is_superadmin': bool(u[4]),
            'is_active': bool(u[5]),
            'created_at': u[6],
            'last_login': u[7]
        } for u in users]
    
    def get_user_by_id(self, user_id):
        """Get user details by ID"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, username, email, is_admin, is_superadmin, is_active, created_at, last_login
            FROM users
            WHERE id = ?
        ''', (user_id,))
        
        user = cursor.fetchone()
        conn.close()
        
        if user:
            return {
                'success': True,
                'user': {
                    'id': user[0],
                    'username': user[1],
                    'email': user[2],
                    'is_admin': bool(user[3]),
                    'is_superadmin': bool(user[4]),
                    'is_active': bool(user[5]),
                    'created_at': user[6],
                    'last_login': user[7]
                }
            }
        else:
            return {'success': False, 'message': 'User not found'}
    
    def update_user(self, user_id, username=None, email=None):
        """Update user details"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            if username and email:
                cursor.execute('''
                    UPDATE users SET username = ?, email = ?
                    WHERE id = ?
                ''', (username, email, user_id))
            elif username:
                cursor.execute('''
                    UPDATE users SET username = ?
                    WHERE id = ?
                ''', (username, user_id))
            elif email:
                cursor.execute('''
                    UPDATE users SET email = ?
                    WHERE id = ?
                ''', (email, user_id))
            
            conn.commit()
            conn.close()
            return {'success': True, 'message': 'User updated successfully'}
        except sqlite3.IntegrityError:
            conn.close()
            return {'success': False, 'message': 'Username or email already exists'}
    
    def delete_user(self, user_id):
        """Delete a user and all related data"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Delete chat history
        cursor.execute('DELETE FROM chat_history WHERE user_id = ?', (user_id,))
        # Delete sessions
        cursor.execute('DELETE FROM sessions WHERE user_id = ?', (user_id,))
        # Delete user
        cursor.execute('DELETE FROM users WHERE id = ?', (user_id,))
        
        conn.commit()
        conn.close()
        
        return {'success': True, 'message': 'User deleted successfully'}
    
    def toggle_admin_status(self, user_id):
        """Toggle admin status for a user"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT is_admin FROM users WHERE id = ?', (user_id,))
        result = cursor.fetchone()
        
        if result:
            new_status = 0 if result[0] else 1
            cursor.execute('UPDATE users SET is_admin = ? WHERE id = ?', (new_status, user_id))
            conn.commit()
            conn.close()
            return {'success': True, 'is_admin': bool(new_status)}
        else:
            conn.close()
            return {'success': False, 'message': 'User not found'}
    
    def toggle_active_status(self, user_id):
        """Toggle active status for a user (ban/unban)"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT is_active FROM users WHERE id = ?', (user_id,))
        result = cursor.fetchone()
        
        if result:
            new_status = 0 if result[0] else 1
            cursor.execute('UPDATE users SET is_active = ? WHERE id = ?', (new_status, user_id))
            conn.commit()
            conn.close()
            return {'success': True, 'is_active': bool(new_status)}
        else:
            conn.close()
            return {'success': False, 'message': 'User not found'}
    
    def log_activity(self, user_id, action, details=None, ip_address=None):
        """Log user activity"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        timestamp = get_ist_now()
        
        cursor.execute('''
            INSERT INTO activity_logs (user_id, action, details, ip_address, timestamp)
            VALUES (?, ?, ?, ?, ?)
        ''', (user_id, action, details, ip_address, timestamp))
        
        conn.commit()
        log_id = cursor.lastrowid
        conn.close()
        
        return log_id
    
    def get_activity_logs(self, limit=100, user_id=None):
        """Get activity logs"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if user_id:
            cursor.execute('''
                SELECT a.id, a.user_id, u.username, a.action, a.details, a.ip_address, a.timestamp
                FROM activity_logs a
                LEFT JOIN users u ON a.user_id = u.id
                WHERE a.user_id = ?
                ORDER BY a.timestamp DESC
                LIMIT ?
            ''', (user_id, limit))
        else:
            cursor.execute('''
                SELECT a.id, a.user_id, u.username, a.action, a.details, a.ip_address, a.timestamp
                FROM activity_logs a
                LEFT JOIN users u ON a.user_id = u.id
                ORDER BY a.timestamp DESC
                LIMIT ?
            ''', (limit,))
        
        logs = cursor.fetchall()
        conn.close()
        
        return [{
            'id': log[0],
            'user_id': log[1],
            'username': log[2],
            'action': log[3],
            'details': log[4],
            'ip_address': log[5],
            'timestamp': log[6]
        } for log in logs]
    
    def get_admin_analytics(self):
        """Get comprehensive analytics for admin dashboard"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Calculate start of today in IST for queries
        today_ist = get_ist_now().date()
        today_msg_query = f"{today_ist}%"
        
        # Total users
        cursor.execute('SELECT COUNT(*) FROM users')
        total_users = cursor.fetchone()[0]
        
        # Active users
        cursor.execute('SELECT COUNT(*) FROM users WHERE is_active = 1')
        active_users = cursor.fetchone()[0]
        
        # Admin users
        cursor.execute('SELECT COUNT(*) FROM users WHERE is_admin = 1')
        admin_users = cursor.fetchone()[0]
        
        # Total messages
        cursor.execute('SELECT COUNT(*) FROM chat_history')
        total_messages = cursor.fetchone()[0]
        
        # Messages today (Using IST date pattern match)
        cursor.execute('''
            SELECT COUNT(*) FROM chat_history
            WHERE timestamp LIKE ?
        ''', (today_msg_query,))
        messages_today = cursor.fetchone()[0]
        
        # Users registered today
        cursor.execute('''
            SELECT COUNT(*) FROM users
            WHERE created_at LIKE ?
        ''', (today_msg_query,))
        users_today = cursor.fetchone()[0]
        
        # Messages by language
        cursor.execute('''
            SELECT language, COUNT(*) as count
            FROM chat_history
            GROUP BY language
            ORDER BY count DESC
        ''')
        language_stats = [{'language': row[0], 'count': row[1]} for row in cursor.fetchall()]
        
        # Messages by mode
        cursor.execute('''
            SELECT mode, COUNT(*) as count
            FROM chat_history
            GROUP BY mode
            ORDER BY count DESC
        ''')
        mode_stats = [{'mode': row[0], 'count': row[1]} for row in cursor.fetchall()]
        
        # Popular commands (extract first word from message)
        cursor.execute('''
            SELECT LOWER(SUBSTR(message, 1, INSTR(message || ' ', ' ') - 1)) as command, COUNT(*) as count
            FROM chat_history
            WHERE LENGTH(message) > 0
            GROUP BY command
            ORDER BY count DESC
            LIMIT 10
        ''')
        popular_commands = [{'command': row[0], 'count': row[1]} for row in cursor.fetchall()]
        
        # User registration trend (last 7 days - simplified)
        # Note: SQLite extraction of date from timestamp string works if format is YYYY-MM-DD HH:MM:SS
        cursor.execute('''
            SELECT substr(created_at, 1, 10) as date, COUNT(*) as count
            FROM users
            GROUP BY date
            ORDER BY date DESC
            LIMIT 7
        ''')
        registration_trend = [{'date': row[0], 'count': row[1]} for row in cursor.fetchall()]
        
        # Message volume trend (last 7 days)
        cursor.execute('''
            SELECT substr(timestamp, 1, 10) as date, COUNT(*) as count
            FROM chat_history
            GROUP BY date
            ORDER BY date DESC
            LIMIT 7
        ''')
        message_trend = [{'date': row[0], 'count': row[1]} for row in cursor.fetchall()]
        
        conn.close()
        
        return {
            'overview': {
                'total_users': total_users,
                'active_users': active_users,
                'admin_users': admin_users,
                'total_messages': total_messages,
                'messages_today': messages_today,
                'users_today': users_today
            },
            'language_stats': language_stats,
            'mode_stats': mode_stats,
            'popular_commands': popular_commands,
            'registration_trend': registration_trend,
            'message_trend': message_trend
        }
    
    def get_setting(self, key):
        """Get a system setting"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT setting_value FROM system_settings WHERE setting_key = ?', (key,))
        result = cursor.fetchone()
        conn.close()
        
        return result[0] if result else None
    
    def set_setting(self, key, value):
        """Set a system setting"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        updated_at = get_ist_now()
        cursor.execute('''
            INSERT OR REPLACE INTO system_settings (setting_key, setting_value, updated_at)
            VALUES (?, ?, ?)
        ''', (key, value, updated_at))
        
        conn.commit()
        conn.close()
        
        return {'success': True, 'message': 'Setting updated'}
    
    def get_all_settings(self):
        """Get all system settings"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT setting_key, setting_value, updated_at FROM system_settings')
        settings = cursor.fetchall()
        conn.close()
        
        return [{
            'key': s[0],
            'value': s[1],
            'updated_at': s[2]
        } for s in settings]



# Test and demo
if __name__ == "__main__":
    print("=" * 60)
    print("WEB DATABASE MANAGER - DEMO")
    print("=" * 60)
    
    # Initialize database
    db = WebDatabase()
    
    # Test user creation
    print("\n[*] Testing User Creation:")
    print("-" * 60)
    result = db.create_user('testuser', 'test@example.com', 'password123')
    print(f"Create user: {result}")
    
    # Test user verification
    print("\n[*] Testing User Verification:")
    print("-" * 60)
    result = db.verify_user('testuser', 'password123')
    print(f"Verify user: {result}")
    
    if result['success']:
        user_id = result['user']['id']
        
        # Test session creation
        print("\n[*] Testing Session Creation:")
        print("-" * 60)
        session_token = db.create_session(user_id)
        print(f"Session token: {session_token[:20]}...")
        
        # Test session verification
        print("\n[*] Testing Session Verification:")
        print("-" * 60)
        session_result = db.verify_session(session_token)
        print(f"Session valid: {session_result}")
        
        # Test chat history
        print("\n[*] Testing Chat History:")
        print("-" * 60)
        db.add_chat_message(user_id, "Hello", "Hi there!", "text", "en")
        db.add_chat_message(user_id, "How are you?", "I'm doing great!", "text", "en")
        
        history = db.get_chat_history(user_id)
        print(f"Chat history ({len(history)} messages):")
        for msg in history:
            print(f"  User: {msg['message']}")
            print(f"  AI: {msg['response']}")
            print(f"  Mode: {msg['mode']}, Language: {msg['language']}")
            print()
        
        # Test stats
        print("\n[*] Testing User Stats:")
        print("-" * 60)
        stats = db.get_user_stats(user_id)
        print(f"Stats: {stats}")
    
    print("\n" + "=" * 60)
    print("[+] Database testing complete!")
    print("=" * 60)
