import pyttsx3
import speech_recognition as sr
import datetime
import wikipedia
import webbrowser
import os
import subprocess
from gtts import gTTS
import random
import pywhatkit as kit
import requests
import json
import wolframalpha
import pyjokes
import smtplib
from email.message import EmailMessage
import threading
import time
import sys
import calendar
import math
import pyautogui
import screen_brightness_control as sbc
import speedtest
import psutil
from pygame import mixer
import pygame
import pyperclip
import clipboard
import pyfiglet
import cv2
import numpy as np
from PIL import Image
import pyqrcode
import png

# Import audio configuration module
from audio_config import create_tts_engine, get_microphone, configure_recognizer, print_audio_config
from input_handler import create_input_handler
from multilang_handler import MultiLangHandler
from whatsapp_automation import WhatsAppAutomation

# Import new AI modules
try:
    from advanced_ai import create_advanced_ai, analyze_sentiment, summarize_text
    from vision_ai import create_vision_ai, analyze_image
    from code_assistant import create_code_assistant, generate_code, explain_code
    from recommendation_engine import create_recommendation_engine
    AI_MODULES_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Some AI modules not available: {e}")
    AI_MODULES_AVAILABLE = False

# Configuration
CONFIG = {
    'email': 'rajpanchal342006@gmail.com',
    'password': 'djds jqim nxrp yevw',
    'REMOVED_HF_TOKEN': 'REMOVED_HF_TOKEN',
    'REMOVED_HF_TOKEN': 'https://api-inference.huggingface.co/models/gpt2',
    'owner_name': 'Raj Panchal',
    'assistant_name': 'Axon'
}

# Display audio configuration at startup
print_audio_config()

# Create global input handler (supports both voice and text input)
# Default mode is 'text' - use 'switch to voice' command to enable voice input
input_handler = create_input_handler(mode='text')

# Create global multi-language handler
multilang_handler = MultiLangHandler()

# Create global WhatsApp automation handler
whatsapp_automation = WhatsAppAutomation()

# Create global AI enhancement modules
if AI_MODULES_AVAILABLE:
    try:
        advanced_ai = create_advanced_ai(REMOVED_HF_TOKEN=CONFIG.get('REMOVED_HF_TOKEN'), max_history=10)
        vision_ai = create_vision_ai(REMOVED_HF_TOKEN=CONFIG.get('REMOVED_HF_TOKEN'))
        code_assistant = create_code_assistant(REMOVED_HF_TOKEN=CONFIG.get('REMOVED_HF_TOKEN'))
        recommendation_engine = create_recommendation_engine()
        print("✓ Advanced AI modules loaded successfully")
    except Exception as e:
        print(f"Warning: Could not initialize AI modules: {e}")
        AI_MODULES_AVAILABLE = False
else:
    print("⚠ Advanced AI modules not available. Install dependencies with: pip install -r requirements.txt")

def speak(audio):
    """Platform-aware text-to-speech using audio_config module"""
    try:
        # Create a fresh engine for each call using audio_config
        local_engine = create_tts_engine(rate=194, voice_index=0)
        
        local_engine.say(audio)
        local_engine.runAndWait()
        
        # Clean up the engine
        try:
            local_engine.stop()
            del local_engine
        except:
            pass
            
    except Exception as e:
        print(f"Speech Error: {e}")
        # Fallback: print to console
        print(f"[SPEAK]: {audio}")

def wish_me():
    """Enhanced greeting function with more personalization"""
    hour = datetime.datetime.now().hour
    day_name = datetime.datetime.now().strftime("%A")
    month_name = datetime.datetime.now().strftime("%B")
    date = datetime.datetime.now().strftime("%d")
    year = datetime.datetime.now().strftime("%Y")
    
    if 5 <= hour < 12:
        greeting = f"Good Morning {CONFIG['owner_name']}!"
    elif 12 <= hour < 17:
        greeting = f"Good Afternoon {CONFIG['owner_name']}!"
    elif 17 <= hour < 22:
        greeting = f"Good Evening {CONFIG['owner_name']}!"
    else:
        greeting = f"Good Night {CONFIG['owner_name']}!"
    
    full_greeting = f"{greeting}. I am {CONFIG['assistant_name']}, your personal assistant. How may I help you today?"
    
    print(full_greeting)
    speak(full_greeting)

def take_command(timeout=5, use_voice=None):

    global input_handler
    if 'input_handler' not in globals():
        input_handler = create_input_handler(mode='voice')
    
    return input_handler.get_input(timeout=timeout, use_voice=use_voice)

def search_youtube():
    """Enhanced YouTube search with validation - respects current input mode"""
    global input_handler
    
    # Get current input mode
    current_mode = get_current_input_mode()
    
    # Prompt user based on mode
    if current_mode == 'voice':
        print("Say the song or video name...")
        speak("Say the song or video name...")
    else:
        print("Type the song or video name...")
        speak("Type the song or video name...")
    
    try:
        # Use input_handler to get search query (respects current mode)
        search_query = input_handler.get_input()
        
        if not search_query or search_query.lower() == "none" or len(search_query.strip()) < 2:
            raise ValueError("Search query too short or invalid")
        
        print(f"Searching for: {search_query}")
        speak(f"Playing {search_query} on YouTube")
        kit.playonyt(search_query)
        return True
    except Exception as e:
        print(f"Error: {e}")
        speak("I couldn't get the video name. Please try again.")
        return False

def speak_hindi(text):
    """Improved Hindi speech using pygame for audio playback"""
    try:
        filename = "hindi_audio.mp3"
        tts = gTTS(text=text, lang='hi')
        tts.save(filename)
        
        # Use pygame for reliable audio playback
        try:
            pygame.mixer.init()
            pygame.mixer.music.load(filename)
            pygame.mixer.music.play()
            
            # Wait for playback to finish
            while pygame.mixer.music.get_busy():
                pygame.time.Clock().tick(10)
            
            pygame.mixer.quit()
        except Exception as pygame_error:
            print(f"Pygame audio error: {pygame_error}")
            # Fallback to os.system
            os.system(f'start wmplayer "{filename}"')
            time.sleep(3)
        
        # Clean up the audio file
        time.sleep(0.5)  # Small delay before deletion
        try:
            os.remove(filename)
        except:
            pass  # File might still be in use
    except Exception as e:
        print(f"Hindi speech error: {e}")
        speak("I encountered an error while trying to speak in Hindi.")

def tell_joke():
    """Enhanced joke telling with error handling"""
    try:
        # pyjokes sometimes has issues with categories, so we'll use neutral category
        joke_type = random.choice(['pyjokes', 'hindi'])
        
        if joke_type == 'pyjokes':
            # Use default category (neutral) which is more reliable
            joke = pyjokes.get_joke(language='en', category='neutral')
        else:
            # Hindi jokes
            joke = random.choice([
                "टीचर: बच्चो, ईमानदारी का सबसे बड़ा उदाहरण दो। गोलू: गांधी जी की चप्पलें चोरी हो गई थीं, फिर भी उन्होंने दूसरी नहीं खरीदी!",
                "पप्पू: बैंक में नौकरी के लिए इंटरव्यू देने गया। मैनेजर: अगर बैंक में आग लग जाए तो तुम क्या करोगे? पप्पू: सर, मैं तुरंत लोन लेकर भाग जाऊंगा!",
                "पत्नी: सुनिए, मुझे ताजमहल देखने की बहुत इच्छा है। पति: ओह! काश तुम 1631 में पैदा हुई होतीं!"
            ])
        
        print(f"Here's a joke for you:\n{joke}")
        if joke_type == 'hindi':
            speak_hindi(joke)
        else:
            speak(joke)
    except Exception as e:
        print(f"Joke Error: {e}")
        # Fallback to a simple joke
        fallback_joke = "Why do programmers prefer dark mode? Because light attracts bugs!"
        print(f"Here's a joke for you:\n{fallback_joke}")
        speak(fallback_joke)

def get_weather(city="Ahmedabad"):
    """Get weather information for a city"""
    try:
        api_key = "bc4a160d51ac5b63706f5302bbcc8e94"  # Replace with your API key
        base_url = "http://api.openweathermap.org/data/2.5/weather?"
        complete_url = f"{base_url}appid={api_key}&q={city}&units=metric"
        
        response = requests.get(complete_url)
        data = response.json()
        
        if data["cod"] != "404":
            main = data["main"]
            temperature = main["temp"]
            pressure = main["pressure"]
            humidity = main["humidity"]
            weather_desc = data["weather"][0]["description"]
            
            weather_report = (
                f"Weather in {city}:\n"
                f"Temperature: {temperature}°C\n"
                f"Atmospheric Pressure: {pressure} hPa\n"
                f"Humidity: {humidity}%\n"
                f"Description: {weather_desc.capitalize()}"
            )
            
            print(weather_report)
            speak(f"The current weather in {city} is {temperature} degrees Celsius with {weather_desc}")
        else:
            print("City not found. Please try again.")
            speak("Sorry, I couldn't find weather information for that city.")
    except Exception as e:
        print(f"Weather API Error: {e}")
        speak("I'm having trouble accessing weather information right now.")

def send_email(receiver, subject, content):
    """Send email using SMTP"""
    try:
        msg = EmailMessage()
        msg['From'] = CONFIG['email']
        msg['To'] = receiver
        msg['Subject'] = subject
        msg.set_content(content)
        
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(CONFIG['email'], CONFIG['password'])
            smtp.send_message(msg)
            
        print("Email sent successfully!")
        speak("Email has been sent successfully.")
    except Exception as e:
        print(f"Email Error: {e}")
        speak("Sorry, I couldn't send the email. Please check your credentials and connection.")

def get_news(api_key="bc4a160d51ac5b63706f5302bbcc8e94", topic="general", num_articles=3):
    """Get news headlines"""
    try:
        url = f"https://newsapi.org/v2/top-headlines?country=in&category={topic}&apiKey={api_key}"
        response = requests.get(url)
        data = response.json()
        
        if data["status"] == "ok":
            articles = data["articles"][:num_articles]
            speak(f"Here are the latest {topic} news headlines")
            
            for idx, article in enumerate(articles, 1):
                title = article["title"]
                source = article["source"]["name"]
                print(f"{idx}. {title} - {source}")
                speak(title)
        else:
            print("Could not fetch news at this time.")
            speak("Sorry, I couldn't fetch the news right now.")
    except Exception as e:
        print(f"News API Error: {e}")
        speak("I'm having trouble accessing news information.")

def set_reminder(reminder_text, minutes):
    """Set a reminder"""
    try:
        minutes = float(minutes)
        seconds = minutes * 60
        speak(f"I'll remind you to {reminder_text} in {minutes} minutes")
        
        def reminder():
            time.sleep(seconds)
            speak(f"Reminder: {reminder_text}")
            # Show notification
            pyautogui.alert(text=f"Reminder: {reminder_text}", title="Reminder")
        
        reminder_thread = threading.Thread(target=reminder)
        reminder_thread.daemon = True
        reminder_thread.start()
        
        print(f"Reminder set for {reminder_text} in {minutes} minutes")
    except Exception as e:
        print(f"Reminder Error: {e}")
        speak("Sorry, I couldn't set that reminder.")

def system_info():
    """Get system information"""
    try:
        # CPU info
        cpu_usage = psutil.cpu_percent(interval=1)
        cpu_freq = psutil.cpu_freq().current / 1000  # Convert to GHz
        
        # Memory info
        memory = psutil.virtual_memory()
        memory_total = round(memory.total / (1024 ** 3), 2)  # Convert to GB
        memory_used = round(memory.used / (1024 ** 3), 2)
        memory_percent = memory.percent
        
        # Battery info
        battery = psutil.sensors_battery()
        battery_percent = battery.percent
        battery_plugged = "plugged in" if battery.power_plugged else "not plugged in"
        
        # Disk info
        disk = psutil.disk_usage('/')
        disk_total = round(disk.total / (1024 ** 3), 2)
        disk_used = round(disk.used / (1024 ** 3), 2)
        disk_percent = disk.percent
        
        info = (
            f"System Information:\n"
            f"CPU Usage: {cpu_usage}% at {cpu_freq:.2f} GHz\n"
            f"Memory: {memory_used}GB used of {memory_total}GB ({memory_percent}%)\n"
            f"Disk: {disk_used}GB used of {disk_total}GB ({disk_percent}%)\n"
            f"Battery: {battery_percent}% ({battery_plugged})"
        )
        
        print(info)
        speak("Here's your system information:")
        speak(f"CPU is at {cpu_usage} percent. Memory usage is {memory_percent} percent.")
        speak(f"Disk usage is {disk_percent} percent. Battery is at {battery_percent} percent and is {battery_plugged}.")
    except Exception as e:
        print(f"System Info Error: {e}")
        speak("I couldn't retrieve system information.")

def internet_speed_test():
    """Test internet speed"""
    try:
        speak("Testing your internet speed. This may take a moment.")
        st = speedtest.Speedtest()
        download_speed = st.download() / 10**6  # Convert to Mbps
        upload_speed = st.upload() / 10**6  # Convert to Mbps
        ping = st.results.ping
        
        result = (
            f"Internet Speed Test Results:\n"
            f"Download Speed: {download_speed:.2f} Mbps\n"
            f"Upload Speed: {upload_speed:.2f} Mbps\n"
            f"Ping: {ping:.2f} ms"
        )
        
        print(result)
        speak(f"Your download speed is {download_speed:.2f} megabits per second.")
        speak(f"Upload speed is {upload_speed:.2f} megabits per second.")
        speak(f"Ping is {ping:.2f} milliseconds.")
    except Exception as e:
        print(f"Speed Test Error: {e}")
        speak("I couldn't test your internet speed right now.")

def take_screenshot():
    """Take and save a screenshot"""
    try:
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"screenshot_{timestamp}.png"
        screenshot = pyautogui.screenshot()
        screenshot.save(filename)
        print(f"Screenshot saved as {filename}")
        speak("Screenshot taken and saved successfully.")
    except Exception as e:
        print(f"Screenshot Error: {e}")
        speak("Sorry, I couldn't take a screenshot.")

def adjust_volume(level):
    """Adjust system volume"""
    try:
        level = int(level)
        if 0 <= level <= 100:
            # Try using pycaw for precise Windows volume control
            try:
                from pycaw.pycaw import AudioUtilities
                
                # Get the default audio device and its volume interface
                devices = AudioUtilities.GetSpeakers()
                volume = devices.EndpointVolume
                
                # Set volume (0.0 to 1.0)
                volume.SetMasterVolumeLevelScalar(level / 100.0, None)
                
                print(f"Volume set to {level}%")
                speak(f"Volume set to {level} percent")
                
            except (ImportError, AttributeError, Exception) as pycaw_error:
                # Fallback: Use key presses (less precise but works without pycaw)
                print(f"pycaw error ({pycaw_error}), using key press method")
                
                # First, unmute if muted
                pyautogui.press('volumemute')
                time.sleep(0.1)
                pyautogui.press('volumemute')
                
                # Set volume to 0 first by pressing volume down many times
                for _ in range(50):
                    pyautogui.press('volumedown')
                    time.sleep(0.01)
                
                # Then increase to desired level (assuming 50 steps = 100%)
                steps = int(level / 2)
                for _ in range(steps):
                    pyautogui.press('volumeup')
                    time.sleep(0.01)
                
                print(f"Volume adjusted to approximately {level}%")
                speak(f"Volume set to approximately {level} percent")
                
        else:
            speak("Please specify a volume level between 0 and 100")
    except ValueError:
        print(f"Volume Control Error: Invalid level '{level}'")
        speak("Please specify a valid volume level between 0 and 100")
    except Exception as e:
        print(f"Volume Control Error: {e}")
        speak("I couldn't adjust the volume.")

def set_brightness(level):
    """Set screen brightness"""
    try:
        level = int(level)
        if 0 <= level <= 100:
            sbc.set_brightness(level)
            speak(f"Screen brightness set to {level} percent")
        else:
            speak("Please specify a brightness level between 0 and 100")
    except Exception as e:
        print(f"Brightness Control Error: {e}")
        speak("I couldn't adjust the screen brightness.")

def open_application(app_name):
    """Open applications based on name"""
    # Simple apps that are in PATH
    simple_apps = {
        'notepad': 'notepad.exe',
        'calculator': 'calc.exe',
        'paint': 'mspaint.exe',
        'command prompt': 'cmd.exe',
        'task manager': 'taskmgr.exe',
    }
    
    # Apps with full paths (common installation locations)
    full_path_apps = {
        'chrome': r'C:\Program Files\Google\Chrome\Application\chrome.exe',
        'google chrome': r'C:\Program Files\Google\Chrome\Application\chrome.exe',
        'firefox': r'C:\Program Files\Mozilla Firefox\firefox.exe',
        'edge': r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe',
        'microsoft edge': r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe',
        'vs code': r'C:\Users\{}\AppData\Local\Programs\Microsoft VS Code\Code.exe'.format(os.getenv('USERNAME')),
        'vscode': r'C:\Users\{}\AppData\Local\Programs\Microsoft VS Code\Code.exe'.format(os.getenv('USERNAME')),
        'whatsapp app': r'C:\Users\{}\AppData\Local\WhatsApp\WhatsApp.exe'.format(os.getenv('USERNAME')),
    }
    
    # Office apps (may vary by installation)
    office_apps = {
        'word': 'winword.exe',
        'excel': 'excel.exe',
        'powerpoint': 'powerpnt.exe',
    }
    
    try:
        app_lower = app_name.lower()
        
        # Try simple apps first
        if app_lower in simple_apps:
            os.system(simple_apps[app_lower])
            speak(f"Opening {app_name}")
            return
        
        # Try full path apps
        if app_lower in full_path_apps:
            app_path = full_path_apps[app_lower]
            if os.path.exists(app_path):
                os.startfile(app_path)
                speak(f"Opening {app_name}")
                return
            else:
                os.system(f'start "" "{app_path}"')
                speak(f"Opening {app_name}")
                return
        
        # Try office apps
        if app_lower in office_apps:
            os.system(office_apps[app_lower])
            speak(f"Opening {app_name}")
            return
        
        # If not found in mappings, try opening as-is
        speak(f"I don't know how to open {app_name}")
        
    except Exception as e:
        print(f"Application Error: {e}")
        speak(f"Sorry, I couldn't open {app_name}")


def open_website(site_name):
    """Open popular websites in default browser"""
    website_mapping = {
        'youtube': 'https://www.youtube.com',
        'whatsapp': 'https://web.whatsapp.com',
        'instagram': 'https://www.instagram.com',
        'facebook': 'https://www.facebook.com',
        'twitter': 'https://twitter.com',
        'x': 'https://twitter.com',
        'linkedin': 'https://www.linkedin.com',
        'gmail': 'https://mail.google.com',
        'github': 'https://github.com',
        'reddit': 'https://www.reddit.com',
        'netflix': 'https://www.netflix.com',
        'amazon': 'https://www.amazon.com',
        'google': 'https://www.google.com',
        'spotify': 'https://www.spotify.com',
        'discord': 'https://discord.com',
        'twitch': 'https://www.twitch.tv',
        'pinterest': 'https://www.pinterest.com',
        'tiktok': 'https://www.tiktok.com'
    }
    
    try:
        url = website_mapping.get(site_name.lower())
        if url:
            webbrowser.open(url)
            speak(f"Opening {site_name}")
            return True
        else:
            # Don't speak error - let it try as application
            return False
    except Exception as e:
        print(f"Website Error: {e}")
        return False

def chat_with_ai(prompt):
    """Chat with Hugging Face AI model - Using GPT-2"""
    try:
        headers = {
            "Authorization": f"Bearer {CONFIG['REMOVED_HF_TOKEN']}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "inputs": prompt,
            "parameters": {
                "max_new_tokens": 100,
                "temperature": 0.7,
                "top_p": 0.9,
                "do_sample": True
            },
            "options": {
                "wait_for_model": True
            }
        }
        
        response = requests.post(CONFIG['REMOVED_HF_TOKEN'], headers=headers, json=payload, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            
            if isinstance(result, list) and len(result) > 0:
                if isinstance(result[0], dict):
                    answer = result[0].get('generated_text', '')
                    if answer.startswith(prompt):
                        answer = answer[len(prompt):].strip()
                    answer = answer if answer else f"Let me help you with that question about {prompt}."
                else:
                    answer = str(result[0])
            elif isinstance(result, dict):
                if 'generated_text' in result:
                    answer = result['generated_text']
                    if answer.startswith(prompt):
                        answer = answer[len(prompt):].strip()
                elif 'error' in result:
                    answer = "The AI model is loading. Please try again in a moment."
                else:
                    answer = f"I understand your question about {prompt}."
            else:
                answer = f"Regarding {prompt}: Let me help you with that!"
            
            print(f"AI: {answer}")
            speak(answer)
            return answer
            
        elif response.status_code == 503:
            answer = "The AI model is currently loading. Please try again in a few seconds."
            print(f"AI: {answer}")
            speak(answer)
            return answer
        else:
            answer = f"I'm here to help with '{prompt}'. Please try again."
            print(f"AI: {answer}")
            speak(answer)
            return answer
            
    except Exception as e:
        print(f"Hugging Face AI Error: {e}")
        speak("I'm having trouble connecting to the AI service right now.")
        return None

def create_qr_code(data, filename="qrcode.png"):
    """Generate a QR code"""
    try:
        qr = pyqrcode.create(data)
        qr.png(filename, scale=8)
        print(f"QR code saved as {filename}")
        speak("QR code generated successfully.")
        # Open the image
        img = Image.open(filename)
        img.show()
    except Exception as e:
        print(f"QR Code Error: {e}")
        speak("Sorry, I couldn't generate the QR code.")

def translate_text(text, target_lang='hi'):
    """Translate text using Google Translate"""
    try:
        from googletrans import Translator
        translator = Translator()
        
        # Translate the text
        translation = translator.translate(text, dest=target_lang)
        translated_text = translation.text
        
        # Speak the translation using pygame
        filename = "translation.mp3"
        tts = gTTS(text=translated_text, lang=target_lang)
        tts.save(filename)
        
        # Use pygame for reliable audio playback
        try:
            pygame.mixer.init()
            pygame.mixer.music.load(filename)
            pygame.mixer.music.play()
            
            # Wait for playback to finish
            while pygame.mixer.music.get_busy():
                pygame.time.Clock().tick(10)
            
            pygame.mixer.quit()
        except Exception as pygame_error:
            print(f"Pygame audio error: {pygame_error}")
            # Fallback to os.system
            os.system(f'start wmplayer "{filename}"')
            time.sleep(3)
        
        # Clean up the audio file
        time.sleep(0.5)
        try:
            os.remove(filename)
        except:
            pass  # File might still be in use
        
        return translated_text
    except ImportError:
        print("googletrans library not installed. Install with: pip install googletrans==4.0.0-rc1")
        speak("Translation library is not installed.")
        return None
    except Exception as e:
        print(f"Translation Error: {e}")
        speak("I couldn't translate that text.")
        return None

def check_calendar(year=None, month=None):
    """Display calendar"""
    try:
        now = datetime.datetime.now()
        year = year or now.year
        month = month or now.month
        
        cal = calendar.month(year, month)
        print(cal)
        speak(f"Here's the calendar for {calendar.month_name[month]} {year}")
    except Exception as e:
        print(f"Calendar Error: {e}")
        speak("I couldn't display the calendar.")

def perform_math_operation(operation, *args):
    """Perform mathematical operations with improved number extraction"""
    try:
        # Helper function to extract numbers from text
        def extract_number(text):
            import re
            # Remove common words
            text = text.lower().strip()
            text = re.sub(r'\b(what is|calculate|the|of|is)\b', '', text).strip()
            
            # Try to convert to float
            try:
                return float(text)
            except ValueError:
                # Try to find a number in the text
                numbers = re.findall(r'-?\d+\.?\d*', text)
                if numbers:
                    return float(numbers[0])
                raise ValueError(f"Could not extract number from: {text}")
        
        # Convert all arguments to numbers
        numbers = [extract_number(str(arg)) for arg in args]
        
        operations = {
            'add': lambda x: sum(x),
            'subtract': lambda x: x[0] - sum(x[1:]) if len(x) > 1 else -x[0],
            'multiply': lambda x: x[0] * x[1] if len(x) >= 2 else x[0],
            'divide': lambda x: x[0] / x[1] if len(x) >= 2 and x[1] != 0 else None,
            'power': lambda x: x[0] ** x[1] if len(x) >= 2 else x[0] ** 2,
            'sqrt': lambda x: math.sqrt(x[0]),
            'log': lambda x: math.log(x[0], x[1]) if len(x) > 1 else math.log10(x[0])
        }
        
        if operation in operations:
            result = operations[operation](numbers)
            if result is None:
                speak("Cannot divide by zero")
                return
            
            # Format result nicely
            if isinstance(result, float) and result.is_integer():
                result = int(result)
            
            print(f"Result: {result}")
            speak(f"The result is {result}")
            return result
        else:
            speak("I don't know that mathematical operation.")
    except ValueError as ve:
        print(f"Math Error: {ve}")
        speak("I couldn't understand the numbers. Please try again with clear numbers.")
    except Exception as e:
        print(f"Math Error: {e}")
        speak("I couldn't perform that calculation.")

def take_notes():
    """Take and save notes"""
    try:
        speak("What would you like to note down?")
        note_text = take_command()
        if note_text.lower() != "none":
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            filename = f"note_{timestamp}.txt"
            with open(filename, 'w') as f:
                f.write(note_text)
            print(f"Note saved as {filename}")
            speak("Note saved successfully.")
    except Exception as e:
        print(f"Notes Error: {e}")
        speak("Sorry, I couldn't save your note.")

def clipboard_operations(action, data=None):
    """Handle clipboard operations"""
    try:
        if action == 'copy':
            pyperclip.copy(data)
            speak("Text copied to clipboard")
        elif action == 'paste':
            text = pyperclip.paste()
            print(f"Clipboard content: {text}")
            speak("Here's the clipboard content")
            speak(text)
        elif action == 'clear':
            pyperclip.copy('')
            speak("Clipboard cleared")
    except Exception as e:
        print(f"Clipboard Error: {e}")
        speak("I couldn't perform that clipboard operation.")


def switch_input_mode(mode=None):
    """Switch between voice and text input modes"""
    global input_handler
    if mode is None:
        current = input_handler.get_mode()
        mode = 'text' if current == 'voice' else 'voice'
    
    if input_handler.set_mode(mode):
        speak(f"Input mode switched to {mode}")
        return True
    return False

def get_current_input_mode():
    """Get the current input mode"""
    global input_handler
    return input_handler.get_mode()


def process_multilang_command(query):
    """
    Process multi-language commands and generate action blocks
    Supports: Hindi, Gujarati, English, and code-mixed
    """
    global multilang_handler
    
    try:
        # Parse the command
        action = multilang_handler.parse_command(query)
        
        # Generate response in the detected language
        response_text = multilang_handler.generate_response(action, action['language'])
        
        # Generate JSON action block
        action_json = multilang_handler.create_action_json(action)
        
        # Print response
        print(response_text)
        
        # Speak response (use appropriate TTS based on language)
        if action['language'] == 'hi':
            speak_hindi(response_text)
        elif action['language'] == 'gu':
            # Use gTTS for Gujarati
            try:
                filename = "gujarati_audio.mp3"
                from gtts import gTTS
                tts = gTTS(text=response_text, lang='gu')
                tts.save(filename)
                
                pygame.mixer.init()
                pygame.mixer.music.load(filename)
                pygame.mixer.music.play()
                
                while pygame.mixer.music.get_busy():
                    pygame.time.Clock().tick(10)
                
                pygame.mixer.quit()
                
                time.sleep(0.5)
                try:
                    os.remove(filename)
                except:
                    pass
            except Exception as e:
                print(f"Gujarati speech error: {e}")
                speak(response_text)
        else:
            speak(response_text)
        
        # Print action JSON block
        print("\n<action>")
        print(json.dumps(action_json, indent=2))
        print("</action>\n")
        
        # Execute the action if it's a recognized command
        if action['tool'] != 'no_action':
            execute_action(action)
        
        return True
        
    except Exception as e:
        print(f"Multi-language processing error: {e}")
        return False


def execute_action(action):
    """Execute the parsed action"""
    global whatsapp_automation
    
    try:
        tool = action.get('tool')
        language = action.get('language', 'en')
        
        if tool == 'send_whatsapp_message':
            contact = action.get('contact', '')
            message = action.get('message', '')
            
            if contact and message:
                # Use WhatsApp automation to send message automatically
                result = whatsapp_automation.send_message_instantly(contact, message, language)
                
                if result['success']:
                    speak(result['message'])
                    print(f"✓ {result['message']}")
                else:
                    speak(result['message'])
                    print(f"✗ {result['message']}")
                    if 'error' in result:
                        print(f"Error details: {result['error']}")
            else:
                error_msg = {
                    'en': "Contact name or message is missing",
                    'hi': "Contact ka naam ya message nahi mila",
                    'gu': "Contact nu naam ke message nathi"
                }
                speak(error_msg.get(language, error_msg['en']))
        
        elif tool == 'make_phone_call':
            contact = action.get('contact', '')
            if contact:
                speak(f"To call {contact}, please use your phone's dialer")
                # In a real mobile implementation, this would trigger the phone app
            else:
                speak("Contact name is missing")
        
        elif tool == 'open_app':
            app_name = action.get('app_name', '')
            if app_name:
                # Try opening as website first, then as application
                if not open_website(app_name):
                    open_application(app_name)
        
        elif tool == 'schedule_task':
            task = action.get('task', '')
            time_info = action.get('time', '')
            
            if task:
                speak(f"Task scheduled: {task} at {time_info}")
                # In a real implementation, this would create a system reminder
            else:
                speak("Task description is missing")
    
    except Exception as e:
        print(f"Action execution error: {e}")
        speak("I encountered an error while executing the action")


def main():
    """Main function to run the AI assistant"""
    # Display ASCII art banner
    banner = pyfiglet.figlet_format(CONFIG['assistant_name'], font="slant")
    print(banner)
    print(f"{CONFIG['assistant_name']} AI Assistant - Version 2.0\n")
    
    # Greet the user
    #wish_me()
    
    while True:
        query = take_command()
        
        if not query or query == "none":
            continue
        
        # PRIORITY 0: Multi-language commands (Hindi, Gujarati, English)
        # Check if this is a multi-language command that should be processed specially
        multilang_keywords = [
            'whatsapp', 'व्हाट्सएप', 'વોટ્સએપ',
            'bhej', 'moklo', 'મોકલો', 'भेज',
            'call', 'कॉल', 'કોલ', 'phone',
            'yaad', 'याद', 'યાદ', 'reminder',
            'khol', 'खोल', 'ખોલ', 'chalu'
        ]
        
        if any(keyword in query.lower() for keyword in multilang_keywords):
            # Try processing as multi-language command
            if process_multilang_command(query):
                continue  # Command processed, skip to next iteration
        
        # PRIORITY 1: Math operations (check FIRST to avoid conflicts with "what is")
        if any(op in query for op in ['plus', 'minus', 'times', 'divided by', 'power of', 'square root', 'log','+','-','*','/']):
            try:
                # Clean up the query
                query_clean = query.replace("what is", "").replace("calculate", "").strip()
                
                if 'plus' in query_clean or 'add' in query_clean or '+' in query_clean:
                    if 'plus' in query_clean:
                        separator = 'plus'  
                    elif 'add' in query_clean:
                        separator = 'add' 
                    elif '+' in query_clean:
                        separator = '+'
                    nums = [num.strip() for num in query_clean.split(separator)]
                    perform_math_operation('add', *nums)
                    
                elif 'minus' in query_clean or 'subtract' in query_clean or '-' in query_clean:
                    if 'minus' in query_clean:
                        separator = 'minus' 
                    elif 'subtract' in query_clean:
                        separator = 'subtract' 
                    elif '-' in query_clean:
                        separator = '-'
                    nums = [num.strip() for num in query_clean.split(separator)]
                    perform_math_operation('subtract', *nums)
                    
                elif 'times' in query_clean or 'multiplied by' in query_clean or 'multiply' in query_clean or '*' in query_clean:
                    if 'times' in query_clean:
                        separator = 'times'
                    elif 'multiplied by' in query_clean:
                        separator = 'multiplied by'
                    elif '*' in query_clean:
                        separator = '*' 
                    else:
                        separator = 'multiply'
                    nums = [num.strip() for num in query_clean.split(separator)]
                    perform_math_operation('multiply', *nums)
                    
                elif 'divided by' in query_clean or 'divide' in query_clean or '/' in query_clean:
                    if 'divided by' in query_clean:
                        separator = 'divided by' 
                    elif '/' in query_clean:
                        separator = '/'
                    else:
                        separator = 'divide'
                    nums = [num.strip() for num in query_clean.split(separator)]
                    perform_math_operation('divide', *nums)
                    
                elif 'power of' in query_clean or 'to the power' in query_clean:
                    separator = 'power of' if 'power of' in query_clean else 'to the power'
                    nums = [num.strip() for num in query_clean.split(separator)]
                    perform_math_operation('power', *nums)
                    
                elif 'square root' in query_clean or 'sqrt' in query_clean:
                    num = query_clean.replace("square root of", "").replace("square root", "").replace("sqrt", "").strip()
                    perform_math_operation('sqrt', num)
                    
                elif 'log' in query_clean:
                    # Handle "log of 100" or "log 100 base 10"
                    query_clean = query_clean.replace("log of", "log").replace("logarithm", "log")
                    if 'base' in query_clean:
                        parts = query_clean.replace("log", "").split("base")
                        num = parts[0].strip()
                        base = parts[1].strip() if len(parts) > 1 else "10"
                        perform_math_operation('log', num, base)
                    else:
                        num = query_clean.replace("log", "").strip()
                        perform_math_operation('log', num)
            except Exception as e:
                print(f"Math Operation Error: {e}")
                speak("Sorry, I couldn't perform that calculation.")
            continue  # Skip other command checks
            
        # PRIORITY 2: Basic commands (with improved word boundary detection)
        # Use word boundaries to avoid matching 'hi' in 'hindu', 'this', etc.
        elif any(f' {word} ' in f' {query} ' or query.startswith(f'{word} ') or query.endswith(f' {word}') or query == word 
                 for word in ['hi', 'hey', 'hello']):
            responses = [
                "Hello there! How can I assist you today?",
                "Hi! What can I do for you?",
                "Hey! How can I help?"
            ]
            response = random.choice(responses)
            print(response)
            speak(response)
            
        elif 'how are you' in query or 'how r u' in query:
            responses = [
                "I'm functioning optimally, thank you for asking!",
                "I'm doing great! Ready to assist you.",
                "All systems are go! How about you?"
            ]
            response = random.choice(responses)
            print(response)
            speak(response)
            
        elif 'your name' in query:
            print(f"My name is {CONFIG['assistant_name']}, your personal AI assistant.")
            speak(f"My name is {CONFIG['assistant_name']}, your personal AI assistant.")
            
        elif 'who made you' in query or 'who created you' in query:
            print(f"I was created by {CONFIG['owner_name']} to assist with various tasks.")
            speak(f"I was created by {CONFIG['owner_name']} to assist with various tasks.")
            
        elif 'thank you' in query or 'thanks' in query:
            responses = [
                "You're welcome!",
                "Happy to help!",
                "Anytime!",
                "My pleasure!"
            ]
            response = random.choice(responses)
            print(response)
            speak(response)
            

        # Input mode switching commands
        elif 'switch to text' in query or 'text mod' in query or 'text mode' in query or 'type mod' in query:
            switch_input_mode('text')
            
        elif 'switch to voice' in query or 'voice mod' in query or 'voice mod' in query or 'speech mod' in query:
            switch_input_mode('voice')
            
        elif 'toggle input' in query or 'switch input' in query:
            switch_input_mode()
            
        elif 'input mode' in query or 'current mode' in query:
            mode = get_current_input_mode()
            response = f"Current input mode is {mode}"
            print(response)
            speak(response)
            
            
        # Information commands
        elif 'wikipedia' in query or 'wikipedia to search' in query or 'wikipedia search' in query or 'according to wikipedia' in query:
            try:
                speak('Searching Wikipedia...')
                query = query.replace("wikipedia", "")
                results = wikipedia.summary(query, sentences=3)
                speak("According to Wikipedia")
                print(results)
                speak(results)
            except Exception as e:
                print(f"Wikipedia Error: {e}")
                speak("Sorry, I couldn't find that information on Wikipedia.")
                
        elif 'search' in query and 'youtube' not in query:
            try:
                query = query.replace("search", "")
                speak(f"Searching for {query}")
                webbrowser.open(f"https://www.google.com/search?q={query}")
            except Exception as e:
                print(f"Search Error: {e}")
                speak("Sorry, I couldn't perform that search.")
                
        elif 'youtube to search' in query or 'youtube search' in query or 'search youtube' in query:
            search_youtube()
            
        # Media commands
        elif 'play music' in query or 'play song' in query:
            try:
                music_dir = 'C:\\Users\\lenovo\\Music\\songs'  # Update this path
                songs = os.listdir(music_dir)
                if songs:
                    song = random.choice(songs)
                    os.startfile(os.path.join(music_dir, song))
                    print(f"Playing: {song}")
                    speak(f"Playing {os.path.splitext(song)[0]}")
                else:
                    speak("No songs found in the music directory.")
            except Exception as e:
                print(f"Music Error: {e}")
                speak("Sorry, I couldn't play music right now.")
                
        # System commands - UNIFIED OPEN COMMAND (websites + applications)
        elif 'open' in query:
            item_name = query.replace("open", "").strip()
            
            # Try opening as website first
            website_opened = open_website(item_name)
            
            # If not a website, try as application
            if not website_opened:
                open_application(item_name)

        elif 'date and time' in query or 'date & time' in query or 'time and date' in query or 'time & date' in query:
            current_date = datetime.datetime.now().strftime("%A, %B %d, %Y")
            current_time = datetime.datetime.now().strftime("%H:%M:%S")
            print(f"Today's date is {current_date} and time is {current_time}")
            speak(f"Today's date is {current_date} and time is {current_time}")
            
        elif 'time' in query:
            current_time = datetime.datetime.now().strftime("%H:%M:%S")
            print(f"The current time is {current_time}")
            speak(f"The current time is {current_time}")
            
        elif 'date' in query:
            current_date = datetime.datetime.now().strftime("%A, %B %d, %Y")
            print(f"Today's date is {current_date}")
            speak(f"Today's date is {current_date}")
            
        # Utility commands
        elif 'weather' in query:
            city = query.split("in")[-1].strip() if "in" in query else "Ahmedabad"
            get_weather(city)
            
        elif 'joke' in query or 'tell joke' in query:
            tell_joke()
            
        elif 'email' in query or 'send mail' in query or 'send email' in query or 'mail' in query:
            try:
                speak("Who should I send the email to?")
                receiver = input("Receiver's email: ")  # Or use speech recognition
                speak("What should be the subject?")
                subject = input("Subject: ")
                speak("What should I say in the email?")
                content = input("Content: ")
                
                if "none" not in [receiver, subject, content]:
                    send_email(receiver, subject, content)
                else:
                    speak("Email cancelled.")
            except Exception as e:
                print(f"Email Setup Error: {e}")
                speak("Sorry, I couldn't set up the email.")
                
        elif 'news' in query:
            topic = "general"
            if 'sports' in query:
                topic = "sports"
            elif 'technology' in query:
                topic = "technology"
            elif 'business' in query:
                topic = "business"
            get_news(topic=topic)
            
        elif 'remind me' in query or 'reminder' in query or 'remind' in query:
            try:
                speak("What should I remind you about?")
                print("What should I remind you about?")
                reminder_text = take_command()
                if reminder_text.lower() != "none":
                    speak("In how many minutes?")
                    print("In how many minutes?")
                    minutes = take_command()
                    if minutes.isdigit():
                        set_reminder(reminder_text, minutes)
                    else:
                        speak("Please specify a valid number of minutes.")
            except Exception as e:
                print(f"Reminder Setup Error: {e}")
                speak("Sorry, I couldn't set that reminder.")
                
        # Advanced commands
        elif 'system info' in query or 'system information' in query:
            system_info()
            
        elif 'internet speed' in query or 'speed test' in query:
            internet_speed_test()
            
        elif 'screenshot' in query:
            take_screenshot()
            
        elif 'volume' in query:
            if 'up' in query:
                pyautogui.press('volumeup')
                speak("Volume increased")
            elif 'down' in query:
                pyautogui.press('volumedown')
                speak("Volume decreased")
            elif 'mute' in query or 'unmute' in query:
                pyautogui.press('volumemute')
                speak("Volume toggled")
            else:
                try:
                    level = ''.join(filter(str.isdigit, query))
                    if level:
                        adjust_volume(level)
                    else:
                        speak("Please specify a volume level between 0 and 100")
                except:
                    speak("Please specify a volume level between 0 and 100")
                    
        elif 'brightness' in query:
            try:
                level = ''.join(filter(str.isdigit, query))
                if level:
                    set_brightness(level)
                else:
                    speak("Please specify a brightness level between 0 and 100")
            except:
                speak("Please specify a brightness level between 0 and 100")
                
        # AI and creative commands
        elif 'chat' in query or 'ask' in query:
            prompt = query.replace("chat", "").replace("ask", "").strip()
            chat_with_ai(prompt)
            
        elif 'qr code' in query or 'qr' in query:
            speak("What data should I encode in the QR code?")
            data = take_command()
            if data.lower() != "none":
                create_qr_code(data)
                
        elif 'translate' in query:
            speak("What text should I translate?")
            text = input("Enter the text to translate: ")
            if text.lower() != "none":
                speak("To which language? For example, Hindi, Spanish, French.")
                lang = input("Enter the target language: ").lower()
                lang_codes = {
                    'hindi': 'hi',
                    'spanish': 'es',
                    'french': 'fr',
                    'german': 'de',
                    'japanese': 'ja'
                }
                target_lang = lang_codes.get(lang, 'hi')  # Default to Hindi
                translated = translate_text(text, target_lang)
                if translated:
                    print(f"Translation: {translated}")
                    speak(f"The translation is: {translated}")
                
        elif 'calendar' in query or 'calender' in query:
            check_calendar()
            
        # Productivity commands
        elif 'note' in query or 'make a note' in query:
            take_notes()
            
        elif 'copy' in query:
            speak("What should I copy to clipboard?")
            text = take_command()
            if text.lower() != "none":
                clipboard_operations('copy', text)
                
        elif 'paste' in query:
            clipboard_operations('paste')
            
        elif 'clear clipboard' in query:
            clipboard_operations('clear')
            
        # ===== NEW AI FEATURES =====
        # Sentiment Analysis
        elif AI_MODULES_AVAILABLE and ('analyze sentiment' in query or 'check sentiment' in query or 'how do i sound' in query):
            try:
                speak("What text should I analyze for sentiment?")
                text_to_analyze = take_command()
                if text_to_analyze and text_to_analyze.lower() != "none":
                    result = analyze_sentiment(text_to_analyze)
                    sentiment = result['sentiment']
                    score = result['score']
                    
                    response = f"The sentiment is {sentiment} with a score of {score:.2f}"
                    print(response)
                    speak(response)
                    
                    # Get emotion-based response
                    emotion_response = advanced_ai.sentiment_analyzer.get_emotion_response(result)
                    speak(emotion_response)
            except Exception as e:
                print(f"Sentiment analysis error: {e}")
                speak("Sorry, I couldn't analyze the sentiment.")
        
        # Text Summarization
        elif AI_MODULES_AVAILABLE and ('summarize' in query or 'summary' in query):
            try:
                speak("What text should I summarize? You can paste it or type it.")
                text_to_summarize = take_command()
                if text_to_summarize and text_to_summarize.lower() != "none" and len(text_to_summarize) > 50:
                    speak("Summarizing the text...")
                    summary = summarize_text(text_to_summarize)
                    print(f"Summary: {summary}")
                    speak(f"Here's the summary: {summary}")
                else:
                    speak("The text is too short to summarize or was not provided.")
            except Exception as e:
                print(f"Summarization error: {e}")
                speak("Sorry, I couldn't summarize the text.")
        
        # Image Analysis
        elif AI_MODULES_AVAILABLE and ('analyze image' in query or 'describe image' in query or 'what is in image' in query):
            try:
                speak("Please provide the path to the image file.")
                image_path = input("Image path: ")
                if image_path and os.path.exists(image_path):
                    speak("Analyzing the image...")
                    result = analyze_image(image_path, analysis_type='complete')
                    
                    if result.get('success') or result.get('summary'):
                        summary = result.get('summary', 'Image analyzed')
                        print(f"Analysis: {summary}")
                        speak(summary)
                        
                        # Additional details
                        if 'analyses' in result:
                            analyses = result['analyses']
                            if analyses.get('faces', {}).get('success'):
                                face_count = analyses['faces'].get('face_count', 0)
                                if face_count > 0:
                                    speak(f"I detected {face_count} face{'s' if face_count > 1 else ''} in the image")
                    else:
                        speak("I couldn't analyze the image. Please check the file path.")
                else:
                    speak("Image file not found.")
            except Exception as e:
                print(f"Image analysis error: {e}")
                speak("Sorry, I couldn't analyze the image.")
        
        # Code Generation
        elif AI_MODULES_AVAILABLE and ('generate code' in query or 'write code' in query or 'create code' in query):
            try:
                speak("What code should I generate? Describe what you want.")
                description = take_command()
                if description and description.lower() != "none":
                    speak("Which programming language? Python, JavaScript, or others?")
                    language = take_command()
                    if not language or language.lower() == "none":
                        language = "python"
                    
                    speak(f"Generating {language} code...")
                    result = generate_code(description, language.lower())
                    
                    if result.get('success'):
                        code = result.get('code', '')
                        print(f"\nGenerated Code ({language}):\n{code}\n")
                        speak(f"I've generated the {language} code. Check the console output.")
                    else:
                        speak("Sorry, I couldn't generate the code.")
            except Exception as e:
                print(f"Code generation error: {e}")
                speak("Sorry, I couldn't generate the code.")
        
        # Code Explanation
        elif AI_MODULES_AVAILABLE and ('explain code' in query or 'what does this code do' in query):
            try:
                speak("Please paste or type the code you want me to explain.")
                code_to_explain = input("Code: ")
                if code_to_explain:
                    result = explain_code(code_to_explain)
                    explanation = result.get('explanation', 'Could not explain code')
                    print(f"Explanation: {explanation}")
                    speak(explanation)
            except Exception as e:
                print(f"Code explanation error: {e}")
                speak("Sorry, I couldn't explain the code.")
        
        # Recommendations
        elif AI_MODULES_AVAILABLE and ('recommend' in query or 'suggestion' in query or 'suggest' in query):
            try:
                category = None
                if 'movie' in query or 'film' in query:
                    category = 'movies'
                elif 'book' in query:
                    category = 'books'
                elif 'music' in query or 'song' in query:
                    category = 'music'
                
                recs = recommendation_engine.get_recommendations(category=category, count=5, personalized=False)
                
                if recs:
                    speak(f"Here are some recommendations:")
                    for i, rec in enumerate(recs, 1):
                        title = rec.get('title', 'Unknown')
                        print(f"{i}. {title}")
                        if i <= 3:  # Speak first 3
                            speak(title)
                else:
                    speak("I don't have recommendations for that category.")
            except Exception as e:
                print(f"Recommendation error: {e}")
                speak("Sorry, I couldn't get recommendations.")
        
        # Conversation Context
        elif AI_MODULES_AVAILABLE and ('conversation summary' in query or 'what did we talk about' in query):
            try:
                summary = advanced_ai.get_conversation_summary()
                print(f"Conversation Summary: {summary}")
                speak(f"Here's what we discussed: {summary}")
            except Exception as e:
                print(f"Conversation summary error: {e}")
                speak("Sorry, I couldn't summarize our conversation.")
        
        # Exit command
        elif 'exit' in query or 'quit' in query or 'goodbye' in query or 'close' in query:
            farewells = [
                "Goodbye! Have a great day!",
                "See you later!",
                "Signing off. Take care!",
                "Until next time!"
            ]
            farewell = random.choice(farewells)
            print(farewell)
            speak(farewell)
            break

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nAssistant terminated by user.")
        speak("Goodbye!")
        sys.exit(0)
    except Exception as e:
        print(f"Fatal Error: {e}")
        speak("I encountered a serious error and need to shut down.")
        sys.exit(1)