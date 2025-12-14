# -*- coding: utf-8 -*-
"""
Contact Database Manager for Axon AI
Uses SQLite to store contact information including phone numbers and name variations
"""

import sqlite3
import os
import json
from datetime import datetime, timedelta

def get_ist_now():
    """Get current time in Indian Standard Time (UTC+5:30)"""
    return datetime.utcnow() + timedelta(hours=5, minutes=30)

class ContactDatabase:
    def __init__(self, db_path='contacts.db'):
        """Initialize the contact database"""
        self.db_path = db_path
        self.create_tables()
        self.populate_default_contacts()
    
    def create_tables(self):
        """Create the contacts table if it doesn't exist"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create contacts table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS contacts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                phone_number TEXT NOT NULL,
                variations TEXT,
                created_at TIMESTAMP,
                updated_at TIMESTAMP
            )
        ''')
        
        # Create index for faster lookups
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_name ON contacts(name)
        ''')
        
        conn.commit()
        conn.close()
    
    def populate_default_contacts(self):
        """Populate database with default contacts if empty"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Check if database is empty
        cursor.execute('SELECT COUNT(*) FROM contacts')
        count = cursor.fetchone()[0]
        
        if count == 0:
            # Default contacts with variations (ASCII only for Windows compatibility)
            default_contacts = [
                {
                    'name': 'Mummy',
                    'phone_number': '+917600851158',  # REPLACE WITH ACTUAL NUMBER
                    'variations': ['mummy', 'mom', 'mother', 'ma', 'maa', 'mumma']
                },
                {
                    'name': 'Papa',
                    'phone_number': '+919876543211',  # REPLACE WITH ACTUAL NUMBER
                    'variations': ['papa', 'dad', 'father', 'pappa']
                },
                {
                    'name': 'Krish',
                    'phone_number': '+916355028893',  # REPLACE WITH ACTUAL NUMBER
                    'variations': ['krish', 'krishna', 'bhai', 'brother', 'bro']
                },
                {
                    'name': 'Jainam',
                    'phone_number': '+917265873596',  # REPLACE WITH ACTUAL NUMBER
                    'variations': ['jainam', 'jainam jg', 'jk jg']
                },
                {
                    'name': 'Harsh JG',
                    'phone_number': '+916356865968',  # REPLACE WITH ACTUAL NUMBER
                    'variations': ['harsh', 'harsh jg', 'harsh (jg)']
                }
            ]
            
            for contact in default_contacts:
                self.add_contact(
                    contact['name'],
                    contact['phone_number'],
                    contact['variations']
                )
            
            print(f"[+] Populated database with {len(default_contacts)} default contacts")
        
        conn.close()
    
    def add_contact(self, name, phone_number, variations=None):
        """Add a new contact to the database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Convert variations list to JSON string
        variations_json = json.dumps(variations) if variations else json.dumps([])
        
        timestamp = get_ist_now()
        
        cursor.execute('''
            INSERT INTO contacts (name, phone_number, variations, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?)
        ''', (name, phone_number, variations_json, timestamp, timestamp))
        
        conn.commit()
        contact_id = cursor.lastrowid
        conn.close()
        
        return contact_id
    
    def get_contact_by_name(self, search_name):
        """Get contact by name or variation"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get all contacts
        cursor.execute('SELECT name, phone_number, variations FROM contacts')
        contacts = cursor.fetchall()
        
        search_name_lower = search_name.lower().strip()
        
        for name, phone_number, variations_json in contacts:
            # Check exact name match
            if name.lower() == search_name_lower:
                conn.close()
                return {'name': name, 'phone_number': phone_number}
            
            # Check variations
            variations = json.loads(variations_json) if variations_json else []
            if search_name_lower in [v.lower() for v in variations]:
                conn.close()
                return {'name': name, 'phone_number': phone_number}
        
        conn.close()
        return None
    
    def update_contact(self, name, phone_number=None, variations=None):
        """Update an existing contact"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        timestamp = get_ist_now()
        
        if phone_number:
            cursor.execute('''
                UPDATE contacts 
                SET phone_number = ?, updated_at = ?
                WHERE name = ?
            ''', (phone_number, timestamp, name))
        
        if variations:
            variations_json = json.dumps(variations)
            cursor.execute('''
                UPDATE contacts 
                SET variations = ?, updated_at = ?
                WHERE name = ?
            ''', (variations_json, timestamp, name))
        
        conn.commit()
        conn.close()
    
    def delete_contact(self, name):
        """Delete a contact from the database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM contacts WHERE name = ?', (name,))
        
        conn.commit()
        conn.close()
    
    def list_all_contacts(self):
        """List all contacts in the database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT name, phone_number, variations FROM contacts ORDER BY name')
        contacts = cursor.fetchall()
        
        result = []
        for name, phone_number, variations_json in contacts:
            variations = json.loads(variations_json) if variations_json else []
            result.append({
                'name': name,
                'phone_number': phone_number,
                'variations': variations
            })
        
        conn.close()
        return result
    
    def search_contacts(self, query):
        """Search contacts by name or variation"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT name, phone_number, variations FROM contacts')
        contacts = cursor.fetchall()
        
        query_lower = query.lower()
        results = []
        
        for name, phone_number, variations_json in contacts:
            variations = json.loads(variations_json) if variations_json else []
            
            # Check if query matches name or any variation
            if (query_lower in name.lower() or 
                any(query_lower in v.lower() for v in variations)):
                results.append({
                    'name': name,
                    'phone_number': phone_number,
                    'variations': variations
                })
        
        conn.close()
        return results


# Utility functions for easy access
def get_contact_phone(contact_name):
    """Get phone number for a contact name"""
    db = ContactDatabase()
    contact = db.get_contact_by_name(contact_name)
    return contact['phone_number'] if contact else None


def add_new_contact(name, phone_number, variations=None):
    """Add a new contact"""
    db = ContactDatabase()
    return db.add_contact(name, phone_number, variations)


def list_contacts():
    """List all contacts"""
    db = ContactDatabase()
    return db.list_all_contacts()


# Test and demo
if __name__ == "__main__":
    print("=" * 60)
    print("CONTACT DATABASE MANAGER - DEMO")
    print("=" * 60)
    
    # Initialize database
    db = ContactDatabase()
    
    # List all contacts
    print("\n[*] All Contacts:")
    print("-" * 60)
    contacts = db.list_all_contacts()
    for contact in contacts:
        print(f"Name: {contact['name']}")
        print(f"Phone: {contact['phone_number']}")
        num_vars = len(contact['variations'])
        print(f"Variations: {num_vars} variations")
        print("-" * 60)
    
    # Test contact lookup
    print("\n[*] Testing Contact Lookup:")
    print("-" * 60)
    test_names = ['mummy', 'mom', 'papa', 'bhai', 'dost', 'sister']
    for test_name in test_names:
        contact = db.get_contact_by_name(test_name)
        if contact:
            print(f"[+] '{test_name}' -> {contact['name']} ({contact['phone_number']})")
        else:
            print(f"[-] '{test_name}' -> Not found")
    
    print("\n" + "=" * 60)
    print("[+] Database initialized and tested successfully!")
    print("=" * 60)
