"""
Advanced AI Module for Axon AI
Provides: Conversation Context, Sentiment Analysis, Text Summarization
Uses: Free Hugging Face API, TextBlob, NLTK
"""

import requests
import json
from datetime import datetime
from collections import deque
import re
from textblob import TextBlob
try:
    from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
    VADER_AVAILABLE = True
except ImportError:
    VADER_AVAILABLE = False
    print("VADER not available. Install with: pip install vaderSentiment")

class ConversationMemory:
    """Manages conversation context and history"""
    
    def __init__(self, max_history=10):
        self.max_history = max_history
        self.conversation_history = deque(maxlen=max_history)
        self.user_preferences = {}
        self.session_start = datetime.now()
        
    def add_interaction(self, user_input, assistant_response, metadata=None):
        """Add an interaction to conversation history"""
        interaction = {
            'timestamp': datetime.now().isoformat(),
            'user': user_input,
            'assistant': assistant_response,
            'metadata': metadata or {}
        }
        self.conversation_history.append(interaction)
        
    def get_context(self, last_n=5):
        """Get recent conversation context"""
        recent = list(self.conversation_history)[-last_n:]
        context = []
        for interaction in recent:
            context.append(f"User: {interaction['user']}")
            context.append(f"Assistant: {interaction['assistant']}")
        return "\n".join(context)
    
    def get_full_history(self):
        """Get complete conversation history"""
        return list(self.conversation_history)
    
    def clear_history(self):
        """Clear conversation history"""
        self.conversation_history.clear()
        
    def save_preference(self, key, value):
        """Save user preference"""
        self.user_preferences[key] = value
        
    def get_preference(self, key, default=None):
        """Get user preference"""
        return self.user_preferences.get(key, default)


class SentimentAnalyzer:
    """Analyzes sentiment and emotions from text"""
    
    def __init__(self):
        self.vader = SentimentIntensityAnalyzer() if VADER_AVAILABLE else None
        
    def analyze_sentiment(self, text):
        """
        Analyze sentiment of text
        Returns: dict with sentiment scores and label
        """
        result = {
            'text': text,
            'sentiment': 'neutral',
            'score': 0.0,
            'confidence': 0.0,
            'emotions': {}
        }
        
        try:
            # Use VADER if available (better for social media/informal text)
            if self.vader:
                scores = self.vader.polarity_scores(text)
                compound = scores['compound']
                
                result['score'] = compound
                result['emotions'] = {
                    'positive': scores['pos'],
                    'negative': scores['neg'],
                    'neutral': scores['neu']
                }
                
                # Classify sentiment
                if compound >= 0.05:
                    result['sentiment'] = 'positive'
                    result['confidence'] = compound
                elif compound <= -0.05:
                    result['sentiment'] = 'negative'
                    result['confidence'] = abs(compound)
                else:
                    result['sentiment'] = 'neutral'
                    result['confidence'] = 1 - abs(compound)
            else:
                # Fallback to TextBlob
                blob = TextBlob(text)
                polarity = blob.sentiment.polarity
                
                result['score'] = polarity
                
                if polarity > 0.1:
                    result['sentiment'] = 'positive'
                    result['confidence'] = polarity
                elif polarity < -0.1:
                    result['sentiment'] = 'negative'
                    result['confidence'] = abs(polarity)
                else:
                    result['sentiment'] = 'neutral'
                    result['confidence'] = 1 - abs(polarity)
                    
        except Exception as e:
            print(f"Sentiment analysis error: {e}")
            
        return result
    
    def get_emotion_response(self, sentiment_result):
        """Get appropriate response based on sentiment"""
        sentiment = sentiment_result['sentiment']
        
        responses = {
            'positive': [
                "I'm glad you're feeling positive!",
                "That's great to hear!",
                "Your enthusiasm is wonderful!",
                "I'm happy to help with your positive energy!"
            ],
            'negative': [
                "I understand you might be frustrated. Let me help.",
                "I'm here to assist you with that.",
                "I'll do my best to help resolve this.",
                "Let me see what I can do to help."
            ],
            'neutral': [
                "I'm here to help.",
                "Let me assist you with that.",
                "I'll help you with this.",
                "How can I help you further?"
            ]
        }
        
        import random
        return random.choice(responses.get(sentiment, responses['neutral']))


class TextSummarizer:
    """Summarizes long text using Hugging Face models"""
    
    def __init__(self, REMOVED_HF_TOKEN=None):
        self.REMOVED_HF_TOKEN = REMOVED_HF_TOKEN
        self.api_url = "https://api-inference.huggingface.co/models/facebook/bart-large-cnn"
        
    def summarize(self, text, max_length=130, min_length=30):
        """
        Summarize text using Hugging Face BART model
        """
        if not self.REMOVED_HF_TOKEN:
            return self._extractive_summary(text, sentences=3)
            
        try:
            headers = {"Authorization": f"Bearer {self.REMOVED_HF_TOKEN}"}
            payload = {
                "inputs": text,
                "parameters": {
                    "max_length": max_length,
                    "min_length": min_length,
                    "do_sample": False
                },
                "options": {"wait_for_model": True}
            }
            
            response = requests.post(self.api_url, headers=headers, json=payload, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                if isinstance(result, list) and len(result) > 0:
                    return result[0].get('summary_text', text)
            
            # Fallback to extractive summary
            return self._extractive_summary(text, sentences=3)
            
        except Exception as e:
            print(f"Summarization error: {e}")
            return self._extractive_summary(text, sentences=3)
    
    def _extractive_summary(self, text, sentences=3):
        """Simple extractive summarization (fallback)"""
        try:
            from textblob import TextBlob
            blob = TextBlob(text)
            sentences_list = blob.sentences[:sentences]
            return ' '.join(str(s) for s in sentences_list)
        except:
            # Ultimate fallback - just take first N sentences
            sentences_list = text.split('. ')[:sentences]
            return '. '.join(sentences_list) + '.'


class AdvancedAI:
    """Main advanced AI class combining all features"""
    
    def __init__(self, REMOVED_HF_TOKEN=None, max_history=10):
        self.memory = ConversationMemory(max_history=max_history)
        self.sentiment_analyzer = SentimentAnalyzer()
        self.summarizer = TextSummarizer(REMOVED_HF_TOKEN=REMOVED_HF_TOKEN)
        self.REMOVED_HF_TOKEN = REMOVED_HF_TOKEN
        
    def process_input(self, user_input, include_sentiment=True):
        """
        Process user input with sentiment analysis and context
        """
        result = {
            'input': user_input,
            'timestamp': datetime.now().isoformat(),
            'context': self.memory.get_context(last_n=3)
        }
        
        if include_sentiment:
            result['sentiment'] = self.sentiment_analyzer.analyze_sentiment(user_input)
            
        return result
    
    def generate_response(self, user_input, context=None):
        """
        Generate contextual response using Hugging Face
        """
        try:
            # Analyze sentiment first
            sentiment = self.sentiment_analyzer.analyze_sentiment(user_input)
            
            # Get conversation context
            if context is None:
                context = self.memory.get_context(last_n=3)
            
            # Build prompt with context
            if context:
                prompt = f"{context}\nUser: {user_input}\nAssistant:"
            else:
                prompt = f"User: {user_input}\nAssistant:"
            
            # Use Hugging Face API for response generation
            if self.REMOVED_HF_TOKEN:
                response = self._generate_with_hf(prompt)
            else:
                response = "I understand. How can I help you with that?"
            
            # Add interaction to memory
            self.memory.add_interaction(user_input, response, {'sentiment': sentiment})
            
            return {
                'response': response,
                'sentiment': sentiment,
                'context_used': bool(context)
            }
            
        except Exception as e:
            print(f"Response generation error: {e}")
            return {
                'response': "I'm here to help. Could you please rephrase that?",
                'sentiment': {'sentiment': 'neutral'},
                'context_used': False
            }
    
    def _generate_with_hf(self, prompt):
        """Generate response using Hugging Face API"""
        try:
            api_url = "https://api-inference.huggingface.co/models/facebook/blenderbot-400M-distill"
            headers = {"Authorization": f"Bearer {self.REMOVED_HF_TOKEN}"}
            payload = {
                "inputs": prompt,
                "parameters": {
                    "max_length": 100,
                    "temperature": 0.7,
                    "top_p": 0.9
                },
                "options": {"wait_for_model": True}
            }
            
            response = requests.post(api_url, headers=headers, json=payload, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                if isinstance(result, list) and len(result) > 0:
                    generated = result[0].get('generated_text', '')
                    # Extract assistant response
                    if 'Assistant:' in generated:
                        return generated.split('Assistant:')[-1].strip()
                    return generated
                    
        except Exception as e:
            print(f"HF API error: {e}")
            
        return "I understand. How can I assist you further?"
    
    def summarize_text(self, text, max_length=130):
        """Summarize long text"""
        return self.summarizer.summarize(text, max_length=max_length)
    
    def get_conversation_summary(self):
        """Get summary of current conversation"""
        history = self.memory.get_full_history()
        if not history:
            return "No conversation history yet."
        
        # Build conversation text
        conv_text = []
        for interaction in history:
            conv_text.append(f"User: {interaction['user']}")
            conv_text.append(f"Assistant: {interaction['assistant']}")
        
        full_text = ' '.join(conv_text)
        return self.summarize_text(full_text, max_length=200)
    
    def clear_memory(self):
        """Clear conversation memory"""
        self.memory.clear_history()


# Convenience functions for easy integration
def create_advanced_ai(REMOVED_HF_TOKEN=None, max_history=10):
    """Create and return AdvancedAI instance"""
    return AdvancedAI(REMOVED_HF_TOKEN=REMOVED_HF_TOKEN, max_history=max_history)


def analyze_sentiment(text):
    """Quick sentiment analysis"""
    analyzer = SentimentAnalyzer()
    return analyzer.analyze_sentiment(text)


def summarize_text(text, REMOVED_HF_TOKEN=None):
    """Quick text summarization"""
    summarizer = TextSummarizer(REMOVED_HF_TOKEN=REMOVED_HF_TOKEN)
    return summarizer.summarize(text)


if __name__ == "__main__":
    # Test the module
    print("Testing Advanced AI Module...\n")
    
    # Test sentiment analysis
    print("=== Sentiment Analysis ===")
    analyzer = SentimentAnalyzer()
    
    test_texts = [
        "I love this! It's amazing!",
        "This is terrible and frustrating.",
        "The weather is okay today."
    ]
    
    for text in test_texts:
        result = analyzer.analyze_sentiment(text)
        print(f"Text: {text}")
        print(f"Sentiment: {result['sentiment']} (score: {result['score']:.2f})")
        print()
    
    # Test conversation memory
    print("=== Conversation Memory ===")
    memory = ConversationMemory(max_history=5)
    memory.add_interaction("Hello", "Hi! How can I help?")
    memory.add_interaction("What's the weather?", "Let me check that for you.")
    print(f"Context:\n{memory.get_context()}")
    print()
    
    # Test summarization
    print("=== Text Summarization ===")
    long_text = """
    Artificial intelligence (AI) is intelligence demonstrated by machines, 
    in contrast to the natural intelligence displayed by humans and animals. 
    Leading AI textbooks define the field as the study of intelligent agents: 
    any device that perceives its environment and takes actions that maximize 
    its chance of successfully achieving its goals. Colloquially, the term 
    artificial intelligence is often used to describe machines that mimic 
    cognitive functions that humans associate with the human mind, such as 
    learning and problem solving.
    """
    summary = summarize_text(long_text.strip())
    print(f"Original length: {len(long_text)} chars")
    print(f"Summary: {summary}")
    print(f"Summary length: {len(summary)} chars")
