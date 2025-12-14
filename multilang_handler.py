"""
Multi-Language Command Handler for Axon AI - IMPROVED VERSION
Supports: Hindi, Gujarati, English and code-mixed (Hinglish/Gujlish)
"""

import json
import re

class MultiLangHandler:
    def __init__(self):
        # Command patterns in all three languages
        self.command_patterns = {
            # Greetings
            'greeting': {
                'en': ['hi', 'hello', 'hey', 'good morning', 'good afternoon', 'good evening'],
                'hi': ['नमस्ते', 'हेलो', 'हाय', 'सुप्रभात', 'शुभ दोपहर', 'शुभ संध्या', 'namaste', 'namaskar'],
                'gu': ['નમસ્તે', 'હેલો', 'હાય', 'સુપ્રભાત', 'શુભ બપોર', 'શુભ સાંજ', 'kem cho', 'su pram']
            },
            
            # WhatsApp commands
            'whatsapp_send': {
                'en': ['send whatsapp', 'whatsapp send', 'message on whatsapp', 'send message', 'whatsapp message'],
                'hi': ['whatsapp bhej', 'whatsapp par bhej', 'message bhej', 'whatsapp pe message', 'whatsapp mein', 'whatsapp ko', 'bhejo', 'bhej do'],
                'gu': ['whatsapp moklo', 'whatsapp par moklo', 'message moklo', 'whatsapp ma message', 'whatsapp mein', 'mokalo', 'moklo']
            },
            
            # Phone call
            'phone_call': {
                'en': ['call', 'phone call', 'make a call', 'dial'],
                'hi': ['call karo', 'phone karo', 'call lagao', 'phone lagao'],
                'gu': ['call karo', 'phone karo', 'call lagavo', 'phone lagavo']
            },
            
            # App opening
            'open_app': {
                'en': ['open', 'launch', 'start', 'run'],
                'hi': ['khol', 'kholo', 'chalu karo', 'start karo'],
                'gu': ['kholo', 'chalu karo', 'start karo']
            },
            
            # Reminders/Tasks
            'reminder': {
                'en': ['remind me', 'set reminder', 'reminder', 'schedule'],
                'hi': ['yaad dilao', 'reminder lagao', 'yaad dila dena', 'reminder set karo'],
                'gu': ['yaad apaavo', 'reminder nakho', 'yaad dilavo']
            },
            
            # Time/Date
            'time': {
                'en': ['time', 'what time', 'current time'],
                'hi': ['samay', 'time kya hai', 'kitne baje hain', 'abhi kitne baje'],
                'gu': ['samay', 'time su che', 'ketla vaagya', 'aabhi ketla vaagya']
            },
            
            'date': {
                'en': ['date', 'what date', 'today date'],
                'hi': ['tarikh', 'aaj ki tarikh', 'date kya hai'],
                'gu': ['tarikh', 'aaje ni tarikh', 'date su che']
            },
            
            # Weather
            'weather': {
                'en': ['weather', 'temperature', 'how is weather'],
                'hi': ['mausam', 'mausam kaisa hai', 'temperature'],
                'gu': ['mausam', 'mausam kevu che', 'temperature']
            },
            
            # Music/YouTube
            'play_youtube': {
                'en': ['play on youtube', 'youtube play', 'search youtube'],
                'hi': ['youtube per chala', 'youtube pe play karo', 'youtube search'],
                'gu': ['youtube per chalavo', 'youtube play karo']
            },
            
            # News
            'news': {
                'en': ['news', 'headlines', 'latest news'],
                'hi': ['samachar', 'khabar', 'news'],
                'gu': ['samachar', 'khabar', 'news']
            },
            
            # Jokes
            'joke': {
                'en': ['joke', 'tell joke', 'make me laugh'],
                'hi': ['joke sunao', 'chutkula', 'hasao'],
                'gu': ['joke sunavo', 'chutkula', 'hasavo']
            },
            
            # System commands
            'volume_up': {
                'en': ['volume up', 'increase volume', 'louder'],
                'hi': ['volume badha', 'volume badhao', 'tej karo'],
                'gu': ['volume vadharo', 'tej karo']
            },
            
            'volume_down': {
                'en': ['volume down', 'decrease volume', 'lower'],
                'hi': ['volume kam karo', 'volume ghatao', 'dheema karo'],
                'gu': ['volume ghataavo', 'dheemu karo']
            },
            
            'screenshot': {
                'en': ['screenshot', 'take screenshot', 'capture screen'],
                'hi': ['screenshot lo', 'screen capture karo'],
                'gu': ['screenshot lo', 'screen capture karo']
            },
            
            # Exit
            'exit': {
                'en': ['exit', 'quit', 'goodbye', 'bye', 'close'],
                'hi': ['band karo', 'exit', 'alvida', 'bye'],
                'gu': ['band karo', 'exit', 'bye', 'aavjo']
            }
        }
        
        # Contact name patterns (common variations)
        self.contact_patterns = {
            'Mummy': ['mummy', 'mom', 'mother', 'ma', 'maa', 'mumma', 'મમ્મી', 'માં'],
            'Papa': ['papa', 'dad', 'father', 'pappa', 'પપ્પા', 'બાપુજી'],
            'Krish': ['bhai', 'brother', 'bro', 'ભાઈ'],
            'Sister': ['sister', 'sis', 'didi', 'બહેન'],
            'Harsh JG': ['friend', 'dost', 'yaar', 'મિત્ર']
        }
        
        # Language detection keywords
        self.lang_keywords = {
            'hi': ['hindi', 'hindi me', 'hindi mein', 'हिंदी में'],
            'gu': ['gujarati', 'gujarati ma', 'gujarati me', 'ગુજરાતી માં'],
            'en': ['english', 'english me', 'english mein', 'angrezi']
        }
    
    def detect_language(self, text):
        """Detect the primary language of the text"""
        text_lower = text.lower()
        
        # Check for explicit language specification
        for lang, keywords in self.lang_keywords.items():
            if any(kw in text_lower for kw in keywords):
                return lang
        
        # Check for language-specific characters
        if re.search(r'[\u0900-\u097F]', text):  # Devanagari (Hindi)
            return 'hi'
        elif re.search(r'[\u0A80-\u0AFF]', text):  # Gujarati
            return 'gu'
        
        # Default to English
        return 'en'
    
    def extract_command_type(self, text):
        """Extract the command type from text - IMPROVED"""
        text_lower = text.lower()
        
        # Priority check for WhatsApp commands (check first to avoid conflicts)
        whatsapp_indicators = ['whatsapp', 'व्हाट्सएप', 'વોટ્સએપ']
        message_indicators = ['bhej', 'bhejo', 'moklo', 'mokalo', 'message', 'msg','muki', 'mukhi', 'mukho', 'de', 'do']
        
        # Check if it has whatsapp keyword
        has_whatsapp = any(indicator in text_lower for indicator in whatsapp_indicators)
        has_message_action = any(msg_word in text_lower for msg_word in message_indicators)
        
        # Also check for contact patterns (ko/ne) + message action
        has_contact_pattern = any(word in text_lower for word in ['ko ', 'ne ', ' ko', ' ne'])
        
        if has_whatsapp and has_message_action:
            return 'whatsapp_send'
        
        # If no explicit whatsapp keyword but has contact pattern + message action, assume WhatsApp
        if has_contact_pattern and has_message_action:
            return 'whatsapp_send'
        
        # Check other command patterns
        for cmd_type, patterns in self.command_patterns.items():
            # Skip whatsapp_send as we already checked it
            if cmd_type == 'whatsapp_send':
                continue
                
            for lang in ['en', 'hi', 'gu']:
                if lang in patterns:
                    for pattern in patterns[lang]:
                        if pattern in text_lower:
                            return cmd_type
        
        return None
    
    def extract_contact_name(self, text):
        """Extract contact name from text - IMPROVED"""
        text_lower = text.lower()
        
        # Check for known contact patterns first
        for standard_name, variations in self.contact_patterns.items():
            for variation in variations:
                if variation in text_lower:
                    return standard_name
        
        # Extract custom name with improved patterns
        # Try multiple patterns in order of priority
        patterns = [
            r'^(\w+)\s+(?:whatsapp|message)',  # "Krishna whatsapp" - name FIRST
            r'^(\w+)\s+(?:ko|ne)',  # "Krishna ko" - name FIRST
            r'(\w+)\s+(?:ko|ne)\s+',  # "Krishna ko" or "Krishna ne"
            r'(?:whatsapp|message)\s+(?:par|mein|ma|pe|maa)\s+(\w+)',  # "whatsapp mein Krishna"
            r'(?:par|mein|ma|pe)\s+(\w+)\s+(?:ko|ne)',  # "par Krishna ko"
            r'(?:ko|ne)\s+(\w+)',  # "ko Krishna"
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text_lower)
            if match:
                name = match.group(1).strip()
                # Exclude common words
                excluded_words = ['whatsapp', 'message', 'msg', 'bhej', 'bhejo', 'moklo', 'mokalo', 
                                'send', 'par', 'mein', 'ma', 'pe', 'do', 'karo', 'hello', 'hi', 'maa', 'per']
                if name not in excluded_words:
                    return name
        
        return None
    
    def extract_message_content(self, text):
        """Extract message content from text - IMPROVED"""
        # Priority 1: Look for text in single quotes (most common in Indian languages)
        single_quote_match = re.search(r"'([^']+)'", text)
        if single_quote_match:
            return single_quote_match.group(1).strip()
        
        # Priority 2: Look for text in double quotes
        double_quote_match = re.search(r'"([^"]+)"', text)
        if double_quote_match:
            return double_quote_match.group(1).strip()
        
        # Priority 3: Extract message from specific patterns
        text_lower = text.lower()
        
        # Pattern 1: "ko/ne MESSAGE bhej/moklo/send/mukhi/de/do"
        # Example: "mummy ko hay bhej do" -> "hay"
        # Example: "mummy ne hay mukhi de" -> "hay"
        pattern1 = re.search(r'(?:ko|ne)\s+(.+?)\s+(?:bhej|moklo|send|mukhi|mukho|de|do)', text_lower)
        if pattern1:
            msg = pattern1.group(1).strip()
            # Remove common filler words but keep short messages
            excluded = ['karo', 'kar', 'please', 'message', 'msg', 'whatsapp', 'per', 'par', 'pe', 'mein', 'ma']
            words = msg.split()
            filtered = [w for w in words if w not in excluded]
            if filtered:
                return ' '.join(filtered)
        
        # Pattern 2: "bhej/send/moklo/mukhi MESSAGE (to/ko/ne)"
        # Example: "send hay to mummy" -> "hay"
        pattern2 = re.search(r'(?:bhej|bhejo|send|moklo|mokalo|mukhi|mukho)\s+(.+?)(?:\s+(?:ko|ne|to|par|pe|mein|ma)|$)', text_lower)
        if pattern2:
            msg = pattern2.group(1).strip()
            # Remove common filler words
            excluded = ['karo', 'de', 'do', 'dena', 'message', 'msg']
            words = msg.split()
            filtered = [w for w in words if w not in excluded]
            if filtered:
                return ' '.join(filtered)
        
        # Pattern 3: "MESSAGE bhej/moklo/send/mukhi" (at end)
        # Example: "hay bhej do" -> "hay"
        pattern3 = re.search(r'\s+(.+?)\s+(?:bhej|moklo|send|mukhi|mukho|de|do)(?:\s|$)', text_lower)
        if pattern3:
            msg = pattern3.group(1).strip()
            # Remove contact-related words and common fillers
            excluded = ['karo', 'kar', 'dena', 'ko', 'ne', 'par', 'pe', 'per', 'mein', 'ma', 
                       'whatsapp', 'message', 'msg', 'mummy', 'papa', 'bhai', 'sister']
            words = msg.split()
            filtered = [w for w in words if w not in excluded]
            if filtered and len(filtered) >= 1:
                return ' '.join(filtered)
        
        # If no message found, return None
        return None
    
    def extract_app_name(self, text):
        """Extract app name from text"""
        text_lower = text.lower()
        
        # Remove command keywords
        for lang in ['en', 'hi', 'gu']:
            if lang in self.command_patterns['open_app']:
                for keyword in self.command_patterns['open_app'][lang]:
                    text_lower = text_lower.replace(keyword, '').strip()
        
        # Common app names
        apps = {
            'whatsapp': ['whatsapp', 'व्हाट्सएप', 'વોટ્સએપ'],
            'chrome': ['chrome', 'browser', 'क्रोम', 'બ્રાઉઝર'],
            'youtube': ['youtube', 'यूट्यूब', 'યુટ્યુબ'],
            'instagram': ['instagram', 'insta', 'इंस्टाग्राम'],
            'facebook': ['facebook', 'fb', 'फेसबुक'],
            'calculator': ['calculator', 'calc', 'कैलकुलेटर', 'ગણતરી'],
            'notepad': ['notepad', 'नोटपैड'],
            'camera': ['camera', 'कैमरा', 'કેમેરા']
        }
        
        for app, variations in apps.items():
            if any(var in text_lower for var in variations):
                return app
        
        return text_lower.strip()
    
    def extract_time_info(self, text):
        """Extract time information from text"""
        text_lower = text.lower()
        
        # Time patterns
        time_patterns = [
            r'(\d+)\s*(?:baje|vaagya|o\'?clock|pm|am)',
            r'(?:subah|morning|savare)\s*(\d+)',
            r'(?:sham|evening|saanje)\s*(\d+)',
            r'(?:raat|night|raate)\s*(\d+)',
            r'(\d+:\d+)',
        ]
        
        for pattern in time_patterns:
            match = re.search(pattern, text_lower)
            if match:
                return match.group(0)
        
        # Relative time
        if any(word in text_lower for word in ['kal', 'tomorrow', 'kale']):
            return 'tomorrow'
        elif any(word in text_lower for word in ['aaj', 'today', 'aaje']):
            return 'today'
        elif any(word in text_lower for word in ['abhi', 'now', 'aabhi']):
            return 'now'
        
        return None
    
    def parse_command(self, text):
        """Parse command and return structured action"""
        cmd_type = self.extract_command_type(text)
        language = self.detect_language(text)
        
        action = {
            'command_type': cmd_type,
            'language': language,
            'original_text': text
        }
        
        if cmd_type == 'whatsapp_send':
            action['contact'] = self.extract_contact_name(text)
            action['message'] = self.extract_message_content(text)
            action['tool'] = 'send_whatsapp_message'
            
        elif cmd_type == 'phone_call':
            action['contact'] = self.extract_contact_name(text)
            action['tool'] = 'make_phone_call'
            
        elif cmd_type == 'open_app':
            action['app_name'] = self.extract_app_name(text)
            action['tool'] = 'open_app'
            
        elif cmd_type == 'reminder':
            action['time'] = self.extract_time_info(text)
            action['task'] = text  # Full text as task description
            action['tool'] = 'schedule_task'
            
        else:
            action['tool'] = 'no_action'
            action['reason'] = 'Information query or unrecognized command'
        
        return action
    
    def generate_response(self, action, language='en'):
        """Generate response in the specified language"""
        responses = {
            'whatsapp_send': {
                'en': f"Sending WhatsApp message to {action.get('contact', 'contact')}",
                'hi': f"WhatsApp par {action.get('contact', 'contact')} ko message bhej raha hoon",
                'gu': f"WhatsApp par {action.get('contact', 'contact')} ne message moklvu chu"
            },
            'phone_call': {
                'en': f"Calling {action.get('contact', 'contact')}",
                'hi': f"{action.get('contact', 'contact')} ko call kar raha hoon",
                'gu': f"{action.get('contact', 'contact')} ne call karu chu"
            },
            'open_app': {
                'en': f"Opening {action.get('app_name', 'app')}",
                'hi': f"{action.get('app_name', 'app')} khol raha hoon",
                'gu': f"{action.get('app_name', 'app')} kholvu chu"
            },
            'reminder': {
                'en': f"Setting reminder for {action.get('time', 'specified time')}",
                'hi': f"{action.get('time', 'specified time')} ka reminder laga raha hoon",
                'gu': f"{action.get('time', 'specified time')} nu reminder nakhvu chu"
            }
        }
        
        cmd_type = action.get('command_type')
        if cmd_type in responses:
            return responses[cmd_type].get(language, responses[cmd_type]['en'])
        
        return "Processing your request"
    
    def create_action_json(self, action):
        """Create JSON action block for the system"""
        actions_list = []
        
        if action['tool'] == 'send_whatsapp_message':
            # First open WhatsApp
            actions_list.append({
                'tool': 'open_app',
                'params': {'app_name': 'WhatsApp'}
            })
            # Then send message
            actions_list.append({
                'tool': 'send_whatsapp_message',
                'params': {
                    'contact_name': action.get('contact', ''),
                    'message': action.get('message', ''),
                    'language': action.get('language', 'en')
                }
            })
        
        elif action['tool'] == 'make_phone_call':
            actions_list.append({
                'tool': 'make_phone_call',
                'params': {
                    'contact_name': action.get('contact', '')
                }
            })
        
        elif action['tool'] == 'open_app':
            actions_list.append({
                'tool': 'open_app',
                'params': {
                    'app_name': action.get('app_name', '')
                }
            })
        
        elif action['tool'] == 'schedule_task':
            actions_list.append({
                'tool': 'schedule_task',
                'params': {
                    'task_description': action.get('task', ''),
                    'time': action.get('time', '')
                }
            })
        
        else:
            actions_list.append({
                'tool': 'no_action',
                'params': {
                    'reason': action.get('reason', 'No action required')
                }
            })
        
        return {'actions': actions_list}


# Test function
if __name__ == "__main__":
    handler = MultiLangHandler()
    
    # Test cases including the problematic ones
    test_commands = [
        "Krishna WhatsApp mein message mokalo",
        "per mummy ko hello bhejo",
        "WhatsApp par mummy ko 'hello' bhej do",
        "bhai ko call karo",
        "YouTube kholo",
    ]
    
    for cmd in test_commands:
        print(f"\nCommand: {cmd}")
        action = handler.parse_command(cmd)
        print(f"Parsed: {action}")
        response = handler.generate_response(action, action['language'])
        print(f"Response: {response}")
        json_action = handler.create_action_json(action)
        print(f"JSON: {json.dumps(json_action, indent=2)}")
