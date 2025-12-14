"""
Utility script to manually set a user as SuperAdmin
Use this if you already registered before the auto-SuperAdmin feature was fixed
"""

import sqlite3
import sys

def list_users():
    """List all users in the database"""
    conn = sqlite3.connect('web_axon.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT id, username, email, is_admin, is_superadmin, is_active 
        FROM users 
        ORDER BY id
    ''')
    
    users = cursor.fetchall()
    conn.close()
    
    if not users:
        print("\n❌ No users found in database.")
        return []
    
    print("\n📋 Current Users:")
    print("-" * 80)
    print(f"{'ID':<5} {'Username':<20} {'Email':<30} {'Admin':<8} {'SuperAdmin':<12} {'Active'}")
    print("-" * 80)
    
    for user in users:
        user_id, username, email, is_admin, is_superadmin, is_active = user
        admin_status = "✅ Yes" if is_admin else "❌ No"
        superadmin_status = "👑 Yes" if is_superadmin else "❌ No"
        active_status = "✅" if is_active else "🚫"
        
        print(f"{user_id:<5} {username:<20} {email:<30} {admin_status:<8} {superadmin_status:<12} {active_status}")
    
    print("-" * 80)
    return users

def make_superadmin(user_id):
    """Make a user SuperAdmin"""
    conn = sqlite3.connect('web_axon.db')
    cursor = conn.cursor()
    
    # Check if user exists
    cursor.execute('SELECT username, email FROM users WHERE id = ?', (user_id,))
    user = cursor.fetchone()
    
    if not user:
        conn.close()
        print(f"\n❌ User with ID {user_id} not found!")
        return False
    
    username, email = user
    
    # Update user to SuperAdmin
    cursor.execute('''
        UPDATE users 
        SET is_admin = 1, is_superadmin = 1 
        WHERE id = ?
    ''', (user_id,))
    
    conn.commit()
    conn.close()
    
    print(f"\n✅ Success! User '{username}' (ID: {user_id}) is now a SuperAdmin!")
    print(f"   Email: {email}")
    print(f"   You can now login at: http://localhost:5000/admin-login.html")
    return True

def main():
    print("=" * 80)
    print("🔧 Axon AI - SuperAdmin Setup Utility")
    print("=" * 80)
    
    users = list_users()
    
    if not users:
        print("\n💡 Tip: Register a new user and they will automatically become SuperAdmin!")
        return
    
    print("\n🎯 Options:")
    print("1. Make a user SuperAdmin")
    print("2. Exit")
    
    choice = input("\nEnter your choice (1-2): ").strip()
    
    if choice == "1":
        try:
            user_id = int(input("\nEnter the User ID to make SuperAdmin: ").strip())
            make_superadmin(user_id)
        except ValueError:
            print("\n❌ Invalid input! Please enter a valid user ID number.")
        except Exception as e:
            print(f"\n❌ Error: {e}")
    elif choice == "2":
        print("\n👋 Goodbye!")
    else:
        print("\n❌ Invalid choice!")

if __name__ == "__main__":
    main()
