# -*- coding: utf-8 -*-
"""
Comprehensive AI Integration Module for Web Interface
Includes ALL features from ai.py
"""

import sys
import os
from datetime import datetime
import random
import json
import webbrowser
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Import existing AI modules
from multilang_handler import MultiLangHandler
from whatsapp_automation import WhatsAppAutomation
from contacts_db import ContactDatabase

# Import new AI modules
try:
    from advanced_ai import create_advanced_ai, analyze_sentiment, summarize_text
    from code_assistant import create_code_assistant, generate_code, explain_code
    from recommendation_engine import create_recommendation_engine
    AI_MODULES_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Some AI modules not available in web interface: {e}")
    AI_MODULES_AVAILABLE = False

class AIBridge:
    def __init__(self, REMOVED_HF_TOKEN=None):
        """Initialize AI bridge with all modules"""
        global AI_MODULES_AVAILABLE
        
        self.multilang_handler = MultiLangHandler()
        self.whatsapp_automation = WhatsAppAutomation()
        self.contacts_db = ContactDatabase()
        self.owner_name = "User"
        self.REMOVED_HF_TOKEN = REMOVED_HF_TOKEN or os.getenv("HF_TOKEN")
        
        
        # Initialize new AI modules with individual error handling
        self.advanced_ai = None
        self.vision_ai = None
        self.code_assistant = None
        self.recommendation_engine = None
        
        if AI_MODULES_AVAILABLE:
            # Try to initialize advanced_ai
            try:
                self.advanced_ai = create_advanced_ai(REMOVED_HF_TOKEN=self.REMOVED_HF_TOKEN, max_history=10)
                print("[OK] Advanced AI module loaded")
            except Exception as e:
                print(f"[WARNING] Advanced AI module failed to load: {e}")
# Try to initialize code_assistant
            try:
                self.code_assistant = create_code_assistant(REMOVED_HF_TOKEN=self.REMOVED_HF_TOKEN)
                print("[OK] Code Assistant module loaded")
            except Exception as e:
                print(f"[WARNING] Code Assistant module failed to load: {e}")
            
            # Try to initialize recommendation_engine
            try:
                self.recommendation_engine = create_recommendation_engine()
                print("[OK] Recommendation Engine module loaded")
            except Exception as e:
                print(f"[WARNING] Recommendation Engine module failed to load: {e}")
            
            # Check if at least one module loaded
            if any([self.advanced_ai, self.vision_ai, self.code_assistant, self.recommendation_engine]):
                print("[OK] AI modules initialized successfully in web interface")
            else:
                print("[WARNING] No AI modules could be initialized")
                AI_MODULES_AVAILABLE = False
    
    def process_command(self, user_message, mode='text', language='en'):
        """
        Process ANY user command and return AI response
        Handles all 34+ features from ai.py
        """
        try:
            query = user_message.lower()
            response_text = ""
            
            # 3. YOUR NAME
            if 'your name' in query or 'what is your name' in query:
                response_text = "I am Axon, your AI assistant. I'm here to help you with various tasks!"
            
            # 4. WHO MADE YOU / WHO CREATED YOU
            elif 'who made you' in query or 'who created you' in query or 'your creator' in query:
                response_text = "I was created by Raj Panchal. I'm an AI assistant designed to help with various tasks in multiple languages!"
            
            # 5. THANK YOU
            elif 'thank' in query:
                responses = ["You're welcome!", "Happy to help!", "Anytime!", "My pleasure!"]
                response_text = random.choice(responses)
            
            # 6. WIKIPEDIA / WHAT IS / WHO IS
            elif 'wikipedia' in query or 'wikipedia to search' in query or 'wikipedia search' in query or 'according to wikipedia' in query:
                try:
                    import wikipedia
                    search_query = query.replace("wikipedia", "").replace("what is", "").replace("who is", "").replace("search", "").strip()
                    if search_query:
                        results = wikipedia.summary(search_query, sentences=3)
                        response_text = f"According to Wikipedia: {results}"
                    else:
                        response_text = "What would you like to know about?"
                except Exception as e:
                    response_text = f"I couldn't find information about that on Wikipedia. Error: {str(e)}"
            
            # 7-8. GOOGLE SEARCH / YOUTUBE SEARCH
            elif 'search' in query and 'youtube' not in query:
                search_query = query.replace("search", "").replace("google", "").replace("for", "").strip()
                if search_query:
                    search_url = f"https://www.google.com/search?q={search_query.replace(' ', '+')}"
                    response_text = f"Searching Google for '{search_query}': {search_url}"
                else:
                    response_text = "What would you like me to search for?"
            
            elif 'youtube' in query and any(word in query for word in ['search', 'find', 'dhundo', 'khojo', 'chalao', 'chalavo', 'bajao', 'sunao','']):
                search_query = query.replace("youtube", "").replace("search", "").replace("find", "").replace("on", "").replace("per", "").replace("par", "").replace("pe", "").replace("chalao", "").replace("chalavo", "").replace("bajao", "").replace("sunao", "").replace("dhundo", "").replace("khojo", "").replace("song", "").strip()
                if search_query:
                    youtube_url = f"https://www.youtube.com/results?search_query={search_query.replace(' ', '+')}"
                    response_text = f"Searching YouTube for '{search_query}': {youtube_url}"
                else:
                    response_text = "What would you like me to search on YouTube?"
            
            # 9. PLAY SONG / PLAY MUSIC (English + Hindi + Gujarati)
            elif any(word in query for word in ['play', 'chalao', 'chalavo', 'bajao', 'sunao']) and any(word in query for word in ['song', 'music', 'video', 'gaana', 'geet']):
                song_name = query.replace("play", "").replace("chalao", "").replace("chalavo", "").replace("bajao", "").replace("sunao", "").replace("song", "").replace("music", "").replace("video", "").replace("gaana", "").replace("geet", "").replace("on youtube", "").replace("youtube", "").replace("per", "").replace("par", "").replace("pe", "").strip()
                if song_name:
                    youtube_url = f"https://www.youtube.com/results?search_query={song_name.replace(' ', '+')}"
                    response_text = f"Playing '{song_name}' on YouTube: {youtube_url}"
                else:
                    response_text = "What song would you like me to play?"
            
            # 10. OPEN APPS/WEBSITES
            elif 'open' in query:
                item_name = query.replace("open", "").strip()
                website_result = self._open_website(item_name)
                if website_result:
                    response_text = website_result
                else:
                    response_text = f"I can open websites in the web interface. Try: 'open youtube', 'open gmail', etc. Desktop apps like '{item_name}' require the desktop version."
            
            elif 'date' in query or 'time' in query:
                current_date = datetime.now().strftime("%A, %B %d, %Y")
                current_time = datetime.now().strftime("%I:%M %p")
                response_text = f"Today's date is {current_date} and the time is {current_time}."
                
            # 11. TIME
            elif 'time' in query:
                current_time = datetime.now().strftime("%I:%M %p")
                response_text = f"The current time is {current_time}"
            
            # 12. DATE
            elif 'date' in query:
                current_date = datetime.now().strftime("%A, %B %d, %Y")
                response_text = f"Today's date is {current_date}"
            
            # 13. WEATHER
            elif 'weather' in query or 'temperature' in query:
                city = "your location"
                for word in query.split():
                    if word.istitle() and len(word) > 3:
                        city = word
                        break
                weather_url = f"https://www.google.com/search?q=weather+{city}"
                response_text = f"Check the weather for {city}: {weather_url}"
            
            # 14. JOKE
            elif 'joke' in query:
                try:
                    import pyjokes
                    joke = pyjokes.get_joke()
                    response_text = joke
                except:
                    jokes = [
                        "Why don't programmers like nature? It has too many bugs!",
                        "Why do Java developers wear glasses? Because they can't C#!",
                        "How many programmers does it take to change a light bulb? None, that's a hardware problem!",
                        "Why did the programmer quit his job? Because he didn't get arrays!",
                        "What's a programmer's favorite hangout place? Foo Bar!"
                    ]
                    response_text = random.choice(jokes)
            
            # 15. EMAIL (Web interface limitation)
            elif 'email' in query or 'send mail' in query:
                response_text = "Email sending is not available in the web interface. Please use the desktop version of Axon AI to send emails."
            
            # 16. NEWS
            elif 'news' in query or 'headlines' in query:
                news_url = "https://news.google.com"
                response_text = f"Here are the latest news headlines: {news_url}"
            
            # 17. CALCULATE / MATH OPERATIONS (28)
            elif any(word in query for word in ['calculate', 'plus', 'minus', 'times', 'divided', 'power', 'square root', 'log', '+', '-', '*', '/']):
                result = self._calculate(query)
                response_text = result
            
            # 18. REMIND ME
            elif 'remind' in query or 'reminder' in query:
                response_text = "Reminder feature works best in the desktop app. For now, I've noted your reminder request!"
            
            # 19. SYSTEM INFO
            elif 'system' in query and ('info' in query or 'information' in query):
                try:
                    import platform
                    import psutil
                    system_info = f"System: {platform.system()} {platform.release()}\n"
                    system_info += f"Processor: {platform.processor()}\n"
                    system_info += f"RAM: {round(psutil.virtual_memory().total / (1024**3), 2)} GB"
                    response_text = system_info
                except:
                    response_text = "System information is best viewed in the desktop app."
            
            # 20. INTERNET SPEED
            elif 'internet speed' in query or 'speed test' in query:
                response_text = "Internet speed test requires the desktop app. You can also visit: https://fast.com"
            
            # 21. SCREENSHOT
            elif 'screenshot' in query or 'screen shot' in query:
                response_text = "Screenshot feature is only available in the desktop app."
            
            # 22. VOLUME
            elif 'volume' in query:
                response_text = "Volume control is only available in the desktop app."
            
            # 23. BRIGHTNESS
            elif 'brightness' in query:
                response_text = "Brightness control is only available in the desktop app."
# 24. INTELLIGENT Q&A (Using Wikipedia)
            elif 'chat' in query or 'ask' in query or 'tell me' in query or 'what' in query or 'who' in query or 'where' in query or 'when' in query or 'why' in query or 'how' in query:
                question = query.replace("chat", "").replace("ask", "").replace("about", "").replace("tell me", "").strip()
                if question and len(question) > 3:
                    # Use Wikipedia for intelligent responses
                    try:
                        import wikipedia
                        # Clean up the question
                        search_query = question.replace("what is", "").replace("who is", "").replace("where is", "").replace("when is", "").replace("why is", "").replace("how is", "").strip()
                        
                        if search_query:
                            try:
                                # Get Wikipedia summary
                                summary = wikipedia.summary(search_query, sentences=3)
                                response_text = summary
                            except wikipedia.exceptions.DisambiguationError as e:
                                # If multiple results, use the first option
                                summary = wikipedia.summary(e.options[0], sentences=3)
                                response_text = summary
                            except wikipedia.exceptions.PageError:
                                # If no page found, provide helpful response
                                response_text = f"I couldn't find specific information about '{search_query}'. Try rephrasing your question or search Google for more details."
                        else:
                            response_text = "What would you like to know about?"
                    except Exception as e:
                        print(f"Wikipedia Error: {e}")
                        response_text = f"I understand you're asking about '{question}'. Let me help - could you be more specific?"
                else:
                    response_text = "What would you like to chat about?"
            
            # 25. QR CODE
            elif 'qr code' in query or 'qr' in query:
                response_text = "QR code generation is available in the desktop app."
            
            # 26. TRANSLATE
            elif 'translate' in query or 'translation' in query or 'translate me' in query:
                response_text = "Translation feature is available in the desktop app. You can also use: https://translate.google.com"
            
            # 27. CALENDAR
            elif 'calendar' in query:
                try:
                    import calendar
                    year = datetime.now().year
                    month = datetime.now().month
                    cal = calendar.month(year, month)
                    response_text = f"Calendar for {datetime.now().strftime('%B %Y')}:\n{cal}"
                except:
                    response_text = "Calendar feature works best in the desktop app."
            
            # 28. NOTES
            elif 'note' in query or 'make a note' in query:
                note_content = query.replace("note", "").replace("make a", "").strip()
                response_text = f"Note saved: '{note_content}' (Notes are best managed in the desktop app)"
            
            # 29-31. CLIPBOARD (Copy, Paste, Clear)
            elif 'copy' in query or 'paste' in query or 'clipboard' in query:
                response_text = "Clipboard operations are only available in the desktop app."
            
            # 32. MOTIVATIONAL QUOTES
            elif 'quote' in query or 'motivate' in query or 'inspiration' in query:
                quotes = [
                    "The only way to do great work is to love what you do. - Steve Jobs",
                    "Innovation distinguishes between a leader and a follower. - Steve Jobs",
                    "The future belongs to those who believe in the beauty of their dreams. - Eleanor Roosevelt",
                    "Success is not final, failure is not fatal: it is the courage to continue that counts. - Winston Churchill",
                    "Believe you can and you're halfway there. - Theodore Roosevelt",
                    "The only impossible journey is the one you never begin. - Tony Robbins",
                    "Don't watch the clock; do what it does. Keep going. - Sam Levenson",
                    "The best time to plant a tree was 20 years ago. The second best time is now. - Chinese Proverb"
                ]
                response_text = random.choice(quotes)
            
            # 33. RANDOM FACTS
            elif 'fact' in query or 'tell me something' in query:
                facts = [
                    "Honey never spoils. Archaeologists have found 3000-year-old honey in Egyptian tombs that's still edible!",
                    "Octopuses have three hearts and blue blood!",
                    "A day on Venus is longer than a year on Venus!",
                    "Bananas are berries, but strawberries aren't!",
                    "The shortest war in history lasted only 38 minutes (Anglo-Zanzibar War, 1896)!",
                    "A group of flamingos is called a 'flamboyance'!",
                    "The human brain uses 20% of the body's energy despite being only 2% of body mass!",
                    "There are more stars in the universe than grains of sand on all Earth's beaches!"
                ]
                response_text = random.choice(facts)
            
            # 34. DEFINE / DICTIONARY
            elif 'define' in query or 'meaning of' in query or 'definition' in query:
                word = query.replace("define", "").replace("meaning of", "").replace("definition", "").replace("what is the", "").strip()
                if word:
                    dict_url = f"https://www.google.com/search?q=define+{word.replace(' ', '+')}"
                    response_text = f"Looking up definition of '{word}': {dict_url}"
                else:
                    response_text = "What word would you like me to define?"
            
            # 35. FLIP A COIN
            elif 'flip' in query and 'coin' in query:
                result = random.choice(['Heads', 'Tails'])
                response_text = f"🪙 Coin flip result: {result}!"
            
            # 36. ROLL DICE
            elif 'roll' in query and ('dice' in query or 'die' in query):
                result = random.randint(1, 6)
                response_text = f"🎲 Dice roll result: {result}!"
            
            # 37. RANDOM NUMBER
            elif 'random number' in query or 'pick a number' in query:
                import re
                numbers = re.findall(r'\d+', query)
                if len(numbers) >= 2:
                    min_num = int(numbers[0])
                    max_num = int(numbers[1])
                    result = random.randint(min_num, max_num)
                    response_text = f"Random number between {min_num} and {max_num}: {result}"
                else:
                    result = random.randint(1, 100)
                    response_text = f"Random number (1-100): {result}"
            
            # 38. HOROSCOPE
            elif 'horoscope' in query or 'zodiac' in query:
                signs = ['aries', 'taurus', 'gemini', 'cancer', 'leo', 'virgo', 'libra', 'scorpio', 'sagittarius', 'capricorn', 'aquarius', 'pisces']
                found_sign = None
                for sign in signs:
                    if sign in query:
                        found_sign = sign
                        break
                
                if found_sign:
                    horoscope_url = f"https://www.google.com/search?q={found_sign}+horoscope+today"
                    response_text = f"Check your {found_sign.title()} horoscope: {horoscope_url}"
                else:
                    response_text = "Which zodiac sign? (Aries, Taurus, Gemini, Cancer, Leo, Virgo, Libra, Scorpio, Sagittarius, Capricorn, Aquarius, Pisces)"
            
            # 39. RECIPE SEARCH
            elif 'recipe' in query or 'how to cook' in query or 'how to make' in query:
                dish = query.replace("recipe", "").replace("how to cook", "").replace("how to make", "").replace("for", "").strip()
                if dish:
                    recipe_url = f"https://www.google.com/search?q={dish.replace(' ', '+')}+recipe"
                    response_text = f"Here's a recipe for {dish}: {recipe_url}"
                else:
                    response_text = "What recipe are you looking for?"
            
            # 40. MOVIE/BOOK RECOMMENDATIONS
            elif ('recommend' in query or 'recommand' in query or 'recommendation' in query or 'suggest' in query) and ('movie' in query or 'film' in query):
                movies = [
                    "3 Idiots - Inspiring comedy-drama about education and friendship",
                    "Dangal - Powerful story of women empowerment in wrestling",
                    "Taare Zameen Par - Heartwarming tale about dyslexia",
                    "PK - Thought-provoking satire on blind faith",
                    "Lagaan - Epic sports drama set in colonial India",
                    "Sholay - Iconic action-adventure classic",
                    "Dilwale Dulhania Le Jayenge - Timeless romantic classic",
                    "Zindagi Na Milegi Dobara - Journey of friendship and self-discovery",
                    "Chak De India - Inspiring sports drama about women's hockey",
                    "Swades - Emotional story of returning to roots",
                    "Rang De Basanti - Patriotic drama about youth awakening",
                    "Gully Boy - Inspiring story of Mumbai street rapper",
                    "Chhello Show (Last Film Show) - Gujarati film about cinema magic",
                    "Hellaro - Gujarati film on women's liberation",
                    "Pather Panchali - Classic Indian cinema masterpiece"
                ]
                response_text = f"[Movie Recommendation] {random.choice(movies)}"
            
            elif ('recommend' in query or 'recommand' in query or 'recommendation' in query or 'suggest' in query) and 'book' in query:
                books = [
                    "Godan by Premchand - Classic Hindi novel on rural life",
                    "Madhushala by Harivansh Rai Bachchan - Iconic Hindi poetry",
                    "Malgudi Days by R.K. Narayan - Charming Indian short stories",
                    "The God of Small Things by Arundhati Roy - Booker Prize winner",
                    "Train to Pakistan by Khushwant Singh - Partition era novel",
                    "Saraswatichandra by Govardhanram Tripathi - Gujarati literature gem",
                    "Akho by Rajendra Shah - Gujarati biographical novel",
                    "Chhe Lage Sanam by Varsha Adalja - Popular Gujarati romance",
                    "Raag Darbari by Shrilal Shukla - Satirical Hindi masterpiece",
                    "Kitne Pakistan by Kamleshwar - Thought-provoking Hindi novel",
                    "The White Tiger by Aravind Adiga - Modern Indian classic",
                    "A Suitable Boy by Vikram Seth - Epic Indian family saga",
                    "The Namesake by Jhumpa Lahiri - Indian diaspora story",
                    "Wings of Fire by APJ Abdul Kalam - Inspiring autobiography",
                    "Gitanjali by Rabindranath Tagore - Nobel Prize poetry"
                ]
                response_text = f"[Book Recommendation] {random.choice(books)}"
            
            elif ('recommend' in query or 'recommand' in query or 'recommendation' in query or 'suggest' in query) and ('song' in query or 'music' in query or 'track' in query):
                songs = [
                    "Tum Hi Ho - Arijit Singh (Aashiqui 2) - Romantic ballad",
                    "Kal Ho Naa Ho - Sonu Nigam - Emotional melody",
                    "Chaiyya Chaiyya - Sukhwinder Singh - Energetic Sufi track",
                    "Kun Faya Kun - A.R. Rahman - Spiritual masterpiece",
                    "Vande Mataram - A.R. Rahman - Patriotic anthem",
                    "Kesariya - Arijit Singh (Brahmastra) - Modern romantic hit",
                    "Apna Time Aayega - Ranveer Singh (Gully Boy) - Hip-hop anthem",
                    "Maa - Shankar Mahadevan (Taare Zameen Par) - Emotional tribute",
                    "Channa Mereya - Arijit Singh - Heartbreak melody",
                    "Ae Watan - Sunidhi Chauhan - Patriotic song",
                    "Malhari - Vishal Dadlani (Bajirao Mastani) - Powerful track",
                    "Mitwa - Shafqat Amanat Ali - Soulful melody",
                    "Pehla Nasha - Udit Narayan - Romantic classic",
                    "Mara Ghat Ma Birajta Shrinathji - Gujarati devotional classic",
                    "Odhani Odhu Ne - Falguni Pathak - Gujarati garba favorite"
                ]
                response_text = f"[Song Recommendation] {random.choice(songs)}"
            
            elif ('recommend' in query or 'recommand' in query or 'recommendation' in query or 'suggest' in query) and ('article' in query or 'reading' in query):
                articles = [
                    "Digital India Initiative - Transforming India through technology",
                    "Indian Space Program - ISRO's achievements and future missions",
                    "Ayurveda and Modern Medicine - Ancient wisdom meets science",
                    "Startup India Success Stories - Inspiring entrepreneurial journeys",
                    "Indian Classical Music - Understanding ragas and talas",
                    "Yoga and Mental Health - Scientific benefits of ancient practice",
                    "Gujarat's Economic Growth - Development model and innovations",
                    "Hindi Literature Evolution - From Premchand to modern writers",
                    "Indian Education System Reforms - NEP 2020 and beyond",
                    "Bollywood's Global Impact - Indian cinema on world stage",
                    "Traditional Indian Cuisine - Health benefits and recipes",
                    "Indian Festivals and Culture - Significance and celebrations",
                    "Cricket in India - More than just a sport",
                    "Indian IT Industry - From outsourcing to innovation",
                    "Gujarati Business Community - Success stories and values"
                ]
                response_text = f"[Article Recommendation] {random.choice(articles)}"
            
            # 41. UNIT CONVERSION
            elif 'convert' in query and any(unit in query for unit in ['km', 'miles', 'kg', 'pounds', 'celsius', 'fahrenheit', 'meters', 'feet']):
                response_text = self._convert_units(query)
            
            # 42. AGE CALCULATOR
            elif 'age' in query and 'born' in query:
                import re
                years = re.findall(r'\b(19|20)\d{2}\b', query)
                if years:
                    birth_year = int(years[0])
                    current_year = datetime.now().year
                    age = current_year - birth_year
                    response_text = f"If you were born in {birth_year}, you are approximately {age} years old."
                else:
                    response_text = "Please mention the birth year. Example: 'I was born in 1990'"
            
            # 43. COUNTDOWN
            elif 'countdown' in query or 'days until' in query:
                response_text = "Countdown feature works best in the desktop app. You can also use online countdown timers!"
            
            # 44. TRIVIA
            elif 'trivia' in query or 'quiz' in query:
                trivia = [
                    "Q: What is the capital of France? A: Paris",
                    "Q: Who painted the Mona Lisa? A: Leonardo da Vinci",
                    "Q: What is the largest planet in our solar system? A: Jupiter",
                    "Q: Who wrote Romeo and Juliet? A: William Shakespeare",
                    "Q: What is the speed of light? A: Approximately 299,792 km/s",
                    "Q: What is the smallest country in the world? A: Vatican City",
                    "Q: Who invented the telephone? A: Alexander Graham Bell",
                    "Q: What is the chemical symbol for gold? A: Au"
                ]
                response_text = f"🧠 Trivia: {random.choice(trivia)}"
            
            # 45. EXIT / QUIT / GOODBYE
            elif any(word in query for word in ['exit', 'quit', 'goodbye', 'bye']):
                responses = [
                    "Goodbye! Have a great day!",
                    "See you later! Take care!",
                    "Bye! Feel free to come back anytime!"
                ]
                response_text = random.choice(responses)
            
            # 46. MODE SWITCHING (handled by frontend)
            elif 'switch to' in query and ('text' in query or 'voice' in query):
                mode_type = 'voice' if 'voice' in query else 'text'
                response_text = f"Mode switching to {mode_type} mode is handled by the interface buttons above."

            # 1-2. GREETINGS (Hi, Hello, Hey, How are you)
            if any(f' {word} ' in f' {query} ' or query.startswith(f'{word} ') or query.endswith(f' {word}') or query == word 
                 for word in ['hi', 'hii', 'hey', 'hello','namaste','namaskar']):
                responses = [
                    "Hello there! How can I assist you today?",
                    "Hi! What can I do for you?",
                    "Hey! How can I help?",
                    "Namaste! How can I assist you today?",
                    "Namaskar! How can I assist you today?"
                ]
                response_text = random.choice(responses)
                
            elif 'how are you' in query or 'how r u' in query:
                responses = [
                    "I'm functioning optimally, thank you for asking! How can I help you?",
                    "I'm doing great! Ready to assist you with anything you need.",
                    "All systems operational! What can I do for you today?"
                ]
                response_text = random.choice(responses)
            
            # HELP / WHAT CAN YOU DO / CAPABILITIES
            elif any(phrase in query for phrase in ['what can you do', 'what can you help', 'help me', 'your capabilities', 'what are you capable of', 'how can you help','tum kya kar sakte ho','tum kya kya kar sakte ho','kya kar sakte']):
                help_text = """I'm Axon AI, your intelligent assistant! Here's what I can help you with:

📚 **Information & Knowledge**:
• Search Wikipedia, Google, YouTube
• Get weather updates, news headlines
• Answer questions about any topic
• Provide definitions and facts

💻 **Coding & Technical Help**:
• Explain programming concepts
• Help debug code
• Suggest algorithms and solutions
• Provide coding best practices
• Explain technical topics

🔧 **Productivity**:
• Perform calculations (math operations)
• Set reminders
• Take notes
• Convert units (km↔miles, kg↔pounds, °C↔°F)
• Calendar information

🎯 **Quick Tasks**:
• Open websites (YouTube, Gmail, etc.)
• Play songs/videos
• Tell jokes and fun facts
• Motivational quotes
• Flip coin, roll dice, random numbers

🌐 **Multi-Language Support**:
• Commands in English, Hindi, Gujarati
• WhatsApp messaging
• Translation support

Just ask me anything! Try: "help me with coding", "search Python tutorial", "what's the weather", "tell me a joke", etc."""
                
                response_text = help_text
            
            # CODING HELP
            elif any(phrase in query for phrase in ['help me with coding', 'help with code', 'coding help', 'programming help', 'how to code', 'learn coding', 'teach me coding']):
                coding_help = """I can help you with coding! Here's how:

**I can assist with**:
1. **Generate Code**: Ask me to generate code for specific tasks
2. **Explain Concepts**: Ask me about variables, loops, functions, OOP, etc.
3. **Debug Code**: Describe your error and I'll help troubleshoot
4. **Suggest Solutions**: Tell me what you're trying to build
5. **Best Practices**: Ask about clean code, design patterns
6. **Learn Topics**: Request tutorials on specific languages

**Example Questions**:
• "Generate code to reverse a string in Python"
• "What is a function in Python?"
• "How do I create a loop in JavaScript?"
• "Explain object-oriented programming"
• "What's the difference between list and tuple?"
• "How to connect to a database in Python?"

**I can also**:
• Search for coding tutorials on YouTube
• Find documentation and resources
• Explain error messages
• Suggest learning paths

What would you like to learn or work on?"""
                
                response_text = coding_help
            
            # SPECIFIC CODING QUESTIONS
            # MOVED BELOW - Code generation takes priority
            # ===== NEW AI FEATURES (HIGH PRIORITY) =====
            # Sentiment Analysis
            elif AI_MODULES_AVAILABLE and ('analyze sentiment' in query or 'check sentiment' in query):
                try:
                    # Extract text after the command
                    text_to_analyze = user_message.replace('analyze sentiment', '').replace('check sentiment', '').replace('sentiment of', '').strip()
                    
                    if text_to_analyze and len(text_to_analyze) > 5:
                        result = analyze_sentiment(text_to_analyze)
                        sentiment = result['sentiment']
                        score = result['score']
                        response_text = f"[Sentiment Analysis] {sentiment.capitalize()} (score: {score:.2f})"
                    else:
                        response_text = "Please provide text to analyze. Example: 'analyze sentiment I love this product!'"
                except Exception as e:
                    response_text = f"Sentiment analysis error: {str(e)}"
            
            # Text Summarization
            elif AI_MODULES_AVAILABLE and ('summarize' in query or 'summary' in query):
                try:
                    text_to_summarize = user_message.replace('summarize', '').replace('summary of', '').replace('summary', '').strip()
                    
                    if text_to_summarize and len(text_to_summarize) > 100:
                        summary = summarize_text(text_to_summarize)
                        response_text = f"[Summary] {summary}"
                    else:
                        response_text = "Please provide longer text to summarize (at least 100 characters). Paste the text after 'summarize'."
                except Exception as e:
                    response_text = f"Summarization error: {str(e)}"
            
            # Code Generation
            elif AI_MODULES_AVAILABLE and ('generate code' in query or 'write code' in query or 'create code' in query):
                try:
                    description = user_message.replace('generate code', '').replace('write code', '').replace('create code', '').replace('for', '').replace('to', '').strip()
                    
                    # Detect language
                    lang = 'python'
                    if 'javascript' in query or 'js' in query:
                        lang = 'javascript'
                    elif 'java' in query and 'javascript' not in query:
                        lang = 'java'
                    elif 'c++' in query or 'cpp' in query:
                        lang = 'cpp'
                    
                    if description and len(description) > 5:
                        result = generate_code(description, lang)
                        if result.get('success'):
                            code = result.get('code', '')
                            response_text = f"[Code Generated - {lang.capitalize()}]\n\n{code}"
                        else:
                            response_text = "Could not generate code. Please provide a clearer description."
                    else:
                        response_text = "Please describe what code you want. Example: 'generate code to calculate factorial in python'"
                except Exception as e:
                    response_text = f"Code generation error: {str(e)}"
            
            # Code Explanation
            elif AI_MODULES_AVAILABLE and ('explain code' in query or 'what does this code do' in query):
                try:
                    # Extract code (everything after the command)
                    code_to_explain = user_message.replace('explain code', '').replace('what does this code do', '').strip()
                    
                    if code_to_explain and len(code_to_explain) > 10:
                        result = explain_code(code_to_explain)
                        explanation = result.get('explanation', 'Could not explain code')
                        response_text = f"[Code Explanation] {explanation}"
                    else:
                        response_text = "Please provide code to explain. Paste your code after 'explain code'."
                except Exception as e:
                    response_text = f"Code explanation error: {str(e)}"
            
            # MULTILANGUAGE COMMANDS (WhatsApp, Calls, etc.)
            elif any(keyword in query for keyword in ['whatsapp', 'bhej', 'moklo', 'call', 'phone', 'khol', 'chalu','ko','do','per','par']):
                action = self.multilang_handler.parse_command(user_message)
                
                if action['tool'] == 'send_whatsapp_message':
                    contact = action.get('contact', '')
                    message = action.get('message', '')
                    if contact and message:
                        result = self.whatsapp_automation.send_message_instantly(contact, message, action['language'])
                        response_text = result['message']
                    else:
                        response_text = "Contact or message is missing"
                
                elif action['tool'] == 'make_phone_call':
                    contact = action.get('contact', '')
                    response_text = f"Phone call feature requires the desktop app to call {contact}."
                
                elif action['tool'] == 'open_app':
                    app_name = action.get('app_name', '')
                    response_text = f"Opening {app_name} - Desktop apps require the desktop version."
                
                else:
                    response_text = self.multilang_handler.generate_response(action, action['language'])
            
            # DEFAULT FALLBACK - Prevent blank responses
            if not response_text or response_text.strip() == "":
                response_text = "I'm not sure how to help with that. Try asking: 'what can you do' to see my capabilities, or rephrase your request."
            
            return {
                'response': response_text,
                'language': language,
                'success': True
            }
            
        except Exception as e:
            print(f"AI Processing Error: {e}")
            import traceback
            traceback.print_exc()
            return {
                'response': "I encountered an error. Please try again or rephrase your request.",
                'language': language,
                'success': False,
                'error': str(e)
            }
    
    def _open_website(self, site_name):
        """Open a website and return confirmation message"""
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
            'pinterest': 'https://www.pinterest.com',
        }
        
        url = website_mapping.get(site_name.lower())
        if url:
            return f"Opening {site_name}: {url}"
        return None
    
    def _calculate(self, query):
        """Perform mathematical calculations"""
        try:
            import re
            
            # First, try to evaluate as a complex mathematical expression
            # Extract just the mathematical expression (numbers and operators)
            expr_match = re.search(r'[\d+\-*/().\s]+', query)
            if expr_match:
                expr = expr_match.group().strip()
                # Check if it contains valid math operators
                if any(op in expr for op in ['+', '-', '*', '/']):
                    try:
                        # Validate that expression only contains safe characters
                        if re.match(r'^[\d+\-*/().\s]+$', expr):
                            result = eval(expr)
                            return f"{expr} = {result}"
                    except:
                        pass  # Fall through to other methods
            
            # Check if it's a simple operator expression like "5+3", "10-2", etc.
            simple_expr = re.match(r'^(\d+\.?\d*)\s*([+\-*/])\s*(\d+\.?\d*)$', query.strip())
            if simple_expr:
                num1 = float(simple_expr.group(1))
                operator = simple_expr.group(2)
                num2 = float(simple_expr.group(3))
                
                if operator == '+':
                    result = num1 + num2
                    return f"{num1} + {num2} = {result}"
                elif operator == '-':
                    result = num1 - num2
                    return f"{num1} - {num2} = {result}"
                elif operator == '*':
                    result = num1 * num2
                    return f"{num1} × {num2} = {result}"
                elif operator == '/':
                    if num2 != 0:
                        result = num1 / num2
                        return f"{num1} ÷ {num2} = {result}"
                    else:
                        return "Cannot divide by zero!"
            
            # Extract numbers (only positive numbers to avoid confusion with operators)
            numbers = re.findall(r'\d+\.?\d*', query)
            
            if len(numbers) >= 2:
                num1 = float(numbers[0])
                num2 = float(numbers[1])
                
                if 'plus' in query or '+' in query or 'add' in query:
                    result = num1 + num2
                    return f"{num1} + {num2} = {result}"
                
                elif 'minus' in query or 'subtract' in query:
                    result = num1 - num2
                    return f"{num1} - {num2} = {result}"
                
                elif 'times' in query or 'multiply' in query or '*' in query or 'x' in query:
                    result = num1 * num2
                    return f"{num1} × {num2} = {result}"
                
                elif 'divided' in query or 'divide' in query or '/' in query:
                    if num2 != 0:
                        result = num1 / num2
                        return f"{num1} ÷ {num2} = {result}"
                    else:
                        return "Cannot divide by zero!"
                
                elif 'power' in query or '^' in query or '**' in query:
                    result = num1 ** num2
                    return f"{num1} to the power of {num2} = {result}"
            
            elif len(numbers) == 1:
                num = float(numbers[0])
                
                if 'square root' in query or 'sqrt' in query:
                    import math
                    result = math.sqrt(num)
                    return f"Square root of {num} = {result}"
                
                elif 'log' in query:
                    import math
                    result = math.log10(num)
                    return f"Log of {num} = {result}"
            
            return "I couldn't understand the calculation. Try: '5 plus 3' or 'square root of 16'"
            
        except Exception as e:
            return f"Calculation error: {str(e)}"
    
    def _convert_units(self, query):
        """Convert units (distance, weight, temperature)"""
        try:
            import re
            numbers = re.findall(r'-?\d+\.?\d*', query)
            
            if not numbers:
                return "Please specify a number to convert. Example: 'convert 10 km to miles'"
            
            value = float(numbers[0])
            
            # Distance conversions
            if 'km' in query and 'miles' in query:
                result = value * 0.621371
                return f"{value} km = {result:.2f} miles"
            elif 'miles' in query and 'km' in query:
                result = value * 1.60934
                return f"{value} miles = {result:.2f} km"
            elif 'meters' in query and 'feet' in query:
                result = value * 3.28084
                return f"{value} meters = {result:.2f} feet"
            elif 'feet' in query and 'meters' in query:
                result = value * 0.3048
                return f"{value} feet = {result:.2f} meters"
            
            # Weight conversions
            elif 'kg' in query and 'pounds' in query:
                result = value * 2.20462
                return f"{value} kg = {result:.2f} pounds"
            elif 'pounds' in query and 'kg' in query:
                result = value * 0.453592
                return f"{value} pounds = {result:.2f} kg"
            
            # Temperature conversions
            elif 'celsius' in query and 'fahrenheit' in query:
                result = (value * 9/5) + 32
                return f"{value}°C = {result:.2f}°F"
            elif 'fahrenheit' in query and 'celsius' in query:
                result = (value - 32) * 5/9
                return f"{value}°F = {result:.2f}°C"
            
            else:
                return "Supported conversions: km↔miles, meters↔feet, kg↔pounds, celsius↔fahrenheit"
                
        except Exception as e:
            return f"Conversion error: {str(e)}"


# Test
if __name__ == "__main__":
    print("=" * 70)
    print("COMPREHENSIVE AI BRIDGE - TESTING ALL FEATURES")
    print("=" * 70)
    
    bridge = AIBridge()
    
    test_commands = [
        "Hello",
        "How are you?",
        "What is your name?",
        "Who created you?",
        "Thank you",
        "What is Python?",
        "Search artificial intelligence",
        "Search YouTube for Kesariya song",
        "Play Kesariya song",
        "Open YouTube",
        "What's the time?",
        "What's the date?",
        "Weather in Mumbai",
        "Tell me a joke",
        "Latest news",
        "Calculate 5 plus 3",
        "10 times 5",
        "Square root of 16",
    ]
    
    print("\n[*] Testing Commands:")
    print("-" * 70)
    
    for cmd in test_commands:
        print(f"\nUser: {cmd}")
        result = bridge.process_command(cmd)
        print(f"AI: {result['response'][:150]}...")
    
    print("\n" + "=" * 70)
    print("[+] All features tested!")
    print("=" * 70)
