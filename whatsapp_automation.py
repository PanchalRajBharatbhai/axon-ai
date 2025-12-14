"""
WhatsApp Automation Module for Axon AI
Automatic message sending using pywhatkit with contact database integration
"""

import pywhatkit as kit
import time
import webbrowser
from contacts_db import ContactDatabase, get_contact_phone

class WhatsAppAutomation:
    def __init__(self):
        """Initialize WhatsApp automation with contact database"""
        self.db = ContactDatabase()
    
    def send_message_instantly(self, contact_name, message, language='en'):
        """
        Send WhatsApp message instantly to a contact
        
        Args:
            contact_name: Name or variation of the contact
            message: Message to send
            language: Language of the response (en, hi, gu)
        
        Returns:
            dict: Status and message
        """
        try:
            # Get contact phone number from database
            contact = self.db.get_contact_by_name(contact_name)
            
            if not contact:
                return {
                    'success': False,
                    'message': self._get_error_message('contact_not_found', language, contact_name),
                    'error': 'Contact not found'
                }
            
            phone_number = contact['phone_number']
            contact_display_name = contact['name']
            
            # Validate phone number format
            if not phone_number.startswith('+'):
                return {
                    'success': False,
                    'message': self._get_error_message('invalid_phone', language, contact_display_name),
                    'error': 'Invalid phone number format'
                }
            
            # Send message using pywhatkit
            print(f"[*] Sending WhatsApp message to {contact_display_name} ({phone_number})...")
            
            # Use sendwhatmsg_instantly for immediate sending
            # Note: This will open WhatsApp Web and send the message
            kit.sendwhatmsg_instantly(
                phone_no=phone_number,
                message=message,
                wait_time=15,  # Wait 15 seconds for WhatsApp Web to load
                tab_close=True,  # Close the tab after sending
                close_time=3  # Wait 3 seconds before closing
            )
            
            return {
                'success': True,
                'message': self._get_success_message(language, contact_display_name, message),
                'contact': contact_display_name,
                'phone': phone_number
            }
            
        except Exception as e:
            print(f"[!] WhatsApp automation error: {e}")
            return {
                'success': False,
                'message': self._get_error_message('automation_failed', language, contact_name),
                'error': str(e)
            }
    
    def send_message_scheduled(self, contact_name, message, hour, minute, language='en'):
        """
        Schedule a WhatsApp message to be sent at a specific time
        
        Args:
            contact_name: Name or variation of the contact
            message: Message to send
            hour: Hour to send (24-hour format)
            minute: Minute to send
            language: Language of the response (en, hi, gu)
        
        Returns:
            dict: Status and message
        """
        try:
            # Get contact phone number from database
            contact = self.db.get_contact_by_name(contact_name)
            
            if not contact:
                return {
                    'success': False,
                    'message': self._get_error_message('contact_not_found', language, contact_name),
                    'error': 'Contact not found'
                }
            
            phone_number = contact['phone_number']
            contact_display_name = contact['name']
            
            # Schedule message using pywhatkit
            print(f"[*] Scheduling WhatsApp message to {contact_display_name} at {hour}:{minute:02d}...")
            
            kit.sendwhatmsg(
                phone_no=phone_number,
                message=message,
                time_hour=hour,
                time_min=minute,
                wait_time=15,
                tab_close=True,
                close_time=3
            )
            
            return {
                'success': True,
                'message': f"Message scheduled to {contact_display_name} at {hour}:{minute:02d}",
                'contact': contact_display_name,
                'phone': phone_number,
                'time': f"{hour}:{minute:02d}"
            }
            
        except Exception as e:
            print(f"[!] WhatsApp scheduling error: {e}")
            return {
                'success': False,
                'message': self._get_error_message('automation_failed', language, contact_name),
                'error': str(e)
            }
    
    def open_chat(self, contact_name, language='en'):
        """
        Open WhatsApp chat with a contact
        
        Args:
            contact_name: Name or variation of the contact
            language: Language of the response (en, hi, gu)
        
        Returns:
            dict: Status and message
        """
        try:
            # Get contact phone number from database
            contact = self.db.get_contact_by_name(contact_name)
            
            if not contact:
                return {
                    'success': False,
                    'message': self._get_error_message('contact_not_found', language, contact_name),
                    'error': 'Contact not found'
                }
            
            phone_number = contact['phone_number']
            contact_display_name = contact['name']
            
            # Open WhatsApp chat
            # Remove '+' from phone number for URL
            phone_clean = phone_number.replace('+', '')
            whatsapp_url = f"https://web.whatsapp.com/send?phone={phone_clean}"
            
            webbrowser.open(whatsapp_url)
            
            return {
                'success': True,
                'message': f"Opening WhatsApp chat with {contact_display_name}",
                'contact': contact_display_name,
                'phone': phone_number
            }
            
        except Exception as e:
            print(f"[!] WhatsApp open chat error: {e}")
            return {
                'success': False,
                'message': self._get_error_message('automation_failed', language, contact_name),
                'error': str(e)
            }
    
    def _get_success_message(self, language, contact_name, message):
        """Get success message in the specified language"""
        messages = {
            'en': f"WhatsApp message sent to {contact_name}: '{message}'",
            'hi': f"{contact_name} ko WhatsApp par message bhej diya: '{message}'",
            'gu': f"{contact_name} ne WhatsApp par message mokli didhu: '{message}'"
        }
        return messages.get(language, messages['en'])
    
    def _get_error_message(self, error_type, language, contact_name=''):
        """Get error message in the specified language"""
        messages = {
            'contact_not_found': {
                'en': f"Contact '{contact_name}' not found in database. Please add the contact first.",
                'hi': f"'{contact_name}' contact database mein nahi mila. Pehle contact add karein.",
                'gu': f"'{contact_name}' contact database ma nathi. Pehla contact add karo."
            },
            'invalid_phone': {
                'en': f"Invalid phone number for {contact_name}. Please update the contact.",
                'hi': f"{contact_name} ka phone number galat hai. Contact update karein.",
                'gu': f"{contact_name} nu phone number galat che. Contact update karo."
            },
            'automation_failed': {
                'en': f"Failed to send WhatsApp message to {contact_name}. Please try manually.",
                'hi': f"{contact_name} ko WhatsApp message nahi bhej paya. Manually bhejein.",
                'gu': f"{contact_name} ne WhatsApp message nahi mokli shakyu. Manually moklo."
            }
        }
        
        error_msgs = messages.get(error_type, messages['automation_failed'])
        return error_msgs.get(language, error_msgs['en'])


# Utility functions for easy access
def send_whatsapp_message(contact_name, message, language='en'):
    """Send WhatsApp message to a contact"""
    wa = WhatsAppAutomation()
    return wa.send_message_instantly(contact_name, message, language)


def schedule_whatsapp_message(contact_name, message, hour, minute, language='en'):
    """Schedule a WhatsApp message"""
    wa = WhatsAppAutomation()
    return wa.send_message_scheduled(contact_name, message, hour, minute, language)


def open_whatsapp_chat(contact_name, language='en'):
    """Open WhatsApp chat with a contact"""
    wa = WhatsAppAutomation()
    return wa.open_chat(contact_name, language)


# Test and demo
if __name__ == "__main__":
    print("=" * 60)
    print("WHATSAPP AUTOMATION - DEMO")
    print("=" * 60)
    
    wa = WhatsAppAutomation()
    
    # Test contact lookup
    print("\n[*] Testing Contact Lookup:")
    print("-" * 60)
    test_contacts = ['mummy', 'papa', 'bhai']
    for contact in test_contacts:
        result = wa.db.get_contact_by_name(contact)
        if result:
            print(f"[+] '{contact}' -> {result['name']} ({result['phone_number']})")
        else:
            print(f"[-] '{contact}' -> Not found")
    
    print("\n" + "=" * 60)
    print("[!] NOTE: Actual message sending requires WhatsApp Web login")
    print("=" * 60)
    
    # Uncomment to test actual sending (requires WhatsApp Web login)
    # result = wa.send_message_instantly('mummy', 'Hello from Axon AI!', 'en')
    # print(f"\nResult: {result}")
