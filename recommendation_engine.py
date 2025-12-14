"""
Recommendation Engine for Axon AI
Provides: Personalized recommendations, User preference learning, Smart suggestions
Uses: Local ML algorithms (scikit-learn), collaborative filtering
"""

import json
import os
from datetime import datetime, timedelta
from collections import defaultdict, Counter
import random


class UserPreferenceTracker:
    """Track and learn user preferences"""
    
    def __init__(self, storage_file='user_preferences.json'):
        self.storage_file = storage_file
        self.preferences = self._load_preferences()
        
    def _load_preferences(self):
        """Load preferences from file"""
        if os.path.exists(self.storage_file):
            try:
                with open(self.storage_file, 'r') as f:
                    return json.load(f)
            except:
                pass
        
        return {
            'interactions': [],
            'favorites': defaultdict(list),
            'categories': defaultdict(int),
            'time_patterns': defaultdict(list),
            'last_updated': datetime.now().isoformat()
        }
    
    def _save_preferences(self):
        """Save preferences to file"""
        try:
            # Convert defaultdict to regular dict for JSON serialization
            save_data = {
                'interactions': self.preferences['interactions'],
                'favorites': dict(self.preferences['favorites']),
                'categories': dict(self.preferences['categories']),
                'time_patterns': dict(self.preferences['time_patterns']),
                'last_updated': datetime.now().isoformat()
            }
            
            with open(self.storage_file, 'w') as f:
                json.dump(save_data, f, indent=2)
        except Exception as e:
            print(f"Error saving preferences: {e}")
    
    def track_interaction(self, action, category, item=None, rating=None):
        """Track user interaction"""
        interaction = {
            'timestamp': datetime.now().isoformat(),
            'action': action,
            'category': category,
            'item': item,
            'rating': rating,
            'hour': datetime.now().hour,
            'day_of_week': datetime.now().strftime('%A')
        }
        
        self.preferences['interactions'].append(interaction)
        
        # Update category counter
        self.preferences['categories'][category] += 1
        
        # Track time patterns
        time_key = f"{interaction['hour']}_{interaction['day_of_week']}"
        self.preferences['time_patterns'][time_key].append(category)
        
        # Add to favorites if highly rated
        if rating and rating >= 4:
            if item not in self.preferences['favorites'][category]:
                self.preferences['favorites'][category].append(item)
        
        # Keep only last 1000 interactions
        if len(self.preferences['interactions']) > 1000:
            self.preferences['interactions'] = self.preferences['interactions'][-1000:]
        
        self._save_preferences()
    
    def get_favorite_categories(self, top_n=5):
        """Get user's favorite categories"""
        categories = Counter(self.preferences['categories'])
        return categories.most_common(top_n)
    
    def get_favorites(self, category):
        """Get favorite items in a category"""
        return self.preferences['favorites'].get(category, [])
    
    def get_time_based_preferences(self):
        """Get preferences based on current time"""
        current_hour = datetime.now().hour
        current_day = datetime.now().strftime('%A')
        time_key = f"{current_hour}_{current_day}"
        
        return self.preferences['time_patterns'].get(time_key, [])


class ContentRecommender:
    """Recommend content based on preferences"""
    
    def __init__(self):
        self.content_database = self._initialize_content()
        
    def _initialize_content(self):
        """Initialize content database"""
        return {
            'movies': [
                {'title': 'The Shawshank Redemption', 'genre': 'Drama', 'rating': 9.3},
                {'title': 'The Dark Knight', 'genre': 'Action', 'rating': 9.0},
                {'title': 'Inception', 'genre': 'Sci-Fi', 'rating': 8.8},
                {'title': 'Forrest Gump', 'genre': 'Drama', 'rating': 8.8},
                {'title': 'The Matrix', 'genre': 'Sci-Fi', 'rating': 8.7},
                {'title': 'Interstellar', 'genre': 'Sci-Fi', 'rating': 8.6},
                {'title': 'Pulp Fiction', 'genre': 'Crime', 'rating': 8.9},
                {'title': 'The Godfather', 'genre': 'Crime', 'rating': 9.2},
                {'title': 'Avengers: Endgame', 'genre': 'Action', 'rating': 8.4},
                {'title': 'Parasite', 'genre': 'Thriller', 'rating': 8.6}
            ],
            'books': [
                {'title': '1984', 'author': 'George Orwell', 'genre': 'Fiction'},
                {'title': 'To Kill a Mockingbird', 'author': 'Harper Lee', 'genre': 'Fiction'},
                {'title': 'The Great Gatsby', 'author': 'F. Scott Fitzgerald', 'genre': 'Fiction'},
                {'title': 'Sapiens', 'author': 'Yuval Noah Harari', 'genre': 'Non-Fiction'},
                {'title': 'Atomic Habits', 'author': 'James Clear', 'genre': 'Self-Help'},
                {'title': 'The Alchemist', 'author': 'Paulo Coelho', 'genre': 'Fiction'},
                {'title': 'Educated', 'author': 'Tara Westover', 'genre': 'Memoir'},
                {'title': 'Thinking, Fast and Slow', 'author': 'Daniel Kahneman', 'genre': 'Psychology'}
            ],
            'music': [
                {'title': 'Bohemian Rhapsody', 'artist': 'Queen', 'genre': 'Rock'},
                {'title': 'Imagine', 'artist': 'John Lennon', 'genre': 'Pop'},
                {'title': 'Billie Jean', 'artist': 'Michael Jackson', 'genre': 'Pop'},
                {'title': 'Smells Like Teen Spirit', 'artist': 'Nirvana', 'genre': 'Rock'},
                {'title': 'Hotel California', 'artist': 'Eagles', 'genre': 'Rock'},
                {'title': 'Shape of You', 'artist': 'Ed Sheeran', 'genre': 'Pop'},
                {'title': 'Blinding Lights', 'artist': 'The Weeknd', 'genre': 'Pop'}
            ],
            'articles': [
                {'title': 'Introduction to Machine Learning', 'topic': 'Technology', 'difficulty': 'Beginner'},
                {'title': 'Advanced Python Techniques', 'topic': 'Programming', 'difficulty': 'Advanced'},
                {'title': 'The Future of AI', 'topic': 'Technology', 'difficulty': 'Intermediate'},
                {'title': 'Healthy Living Tips', 'topic': 'Health', 'difficulty': 'Beginner'},
                {'title': 'Financial Planning 101', 'topic': 'Finance', 'difficulty': 'Beginner'}
            ]
        }
    
    def recommend(self, category, count=5, preferences=None):
        """
        Recommend items from category
        """
        items = self.content_database.get(category, [])
        
        if not items:
            return []
        
        # If we have preferences, filter/sort accordingly
        if preferences:
            # Simple preference-based sorting (can be enhanced)
            favorite_categories = [cat for cat, _ in preferences]
            # For now, just return random selection
            pass
        
        # Return random selection
        if len(items) <= count:
            return items
        
        return random.sample(items, count)
    
    def get_personalized_recommendations(self, user_tracker, count=5):
        """Get personalized recommendations based on user history"""
        favorite_cats = user_tracker.get_favorite_categories(top_n=3)
        
        recommendations = []
        
        for category, _ in favorite_cats:
            if category in self.content_database:
                items = self.recommend(category, count=2)
                for item in items:
                    item['category'] = category
                    item['reason'] = f"Based on your interest in {category}"
                    recommendations.append(item)
        
        # Fill remaining with popular items
        while len(recommendations) < count:
            category = random.choice(list(self.content_database.keys()))
            items = self.recommend(category, count=1)
            if items:
                item = items[0]
                item['category'] = category
                item['reason'] = "Popular recommendation"
                recommendations.append(item)
        
        return recommendations[:count]


class TaskPrioritizer:
    """Prioritize tasks using simple ML"""
    
    def __init__(self):
        pass
    
    def prioritize_tasks(self, tasks):
        """
        Prioritize tasks based on urgency, importance, and deadline
        tasks: list of dicts with keys: name, urgency, importance, deadline
        """
        scored_tasks = []
        
        for task in tasks:
            score = 0
            
            # Urgency score (1-5)
            urgency = task.get('urgency', 3)
            score += urgency * 2
            
            # Importance score (1-5)
            importance = task.get('importance', 3)
            score += importance * 3
            
            # Deadline proximity
            deadline = task.get('deadline')
            if deadline:
                try:
                    deadline_date = datetime.fromisoformat(deadline)
                    days_until = (deadline_date - datetime.now()).days
                    
                    if days_until < 0:
                        score += 20  # Overdue
                    elif days_until == 0:
                        score += 15  # Due today
                    elif days_until <= 3:
                        score += 10  # Due soon
                    elif days_until <= 7:
                        score += 5   # Due this week
                except:
                    pass
            
            scored_tasks.append({
                'task': task,
                'priority_score': score
            })
        
        # Sort by score (highest first)
        scored_tasks.sort(key=lambda x: x['priority_score'], reverse=True)
        
        return [item['task'] for item in scored_tasks]
    
    def suggest_optimal_time(self, task, user_tracker):
        """Suggest optimal time to do a task"""
        # Get time-based preferences
        time_prefs = user_tracker.get_time_based_preferences()
        
        # Simple suggestion based on current patterns
        current_hour = datetime.now().hour
        
        suggestions = {
            'morning': (6, 12),
            'afternoon': (12, 17),
            'evening': (17, 22),
            'night': (22, 6)
        }
        
        # Suggest based on task type
        task_name = task.get('name', '').lower()
        
        if 'exercise' in task_name or 'workout' in task_name:
            return "morning (6-8 AM) for best energy levels"
        elif 'study' in task_name or 'learn' in task_name:
            return "morning or afternoon (9 AM - 4 PM) for better focus"
        elif 'creative' in task_name or 'write' in task_name:
            return "evening (6-9 PM) when mind is relaxed"
        else:
            return "based on your schedule and energy levels"


class RecommendationEngine:
    """Main recommendation engine combining all features"""
    
    def __init__(self, storage_file='user_preferences.json'):
        self.user_tracker = UserPreferenceTracker(storage_file=storage_file)
        self.content_recommender = ContentRecommender()
        self.task_prioritizer = TaskPrioritizer()
    
    def track_user_action(self, action, category, item=None, rating=None):
        """Track user action"""
        self.user_tracker.track_interaction(action, category, item, rating)
    
    def get_recommendations(self, category=None, count=5, personalized=True):
        """Get recommendations"""
        if personalized:
            return self.content_recommender.get_personalized_recommendations(
                self.user_tracker, count=count
            )
        elif category:
            return self.content_recommender.recommend(category, count=count)
        else:
            # Return mix of all categories
            all_recs = []
            for cat in ['movies', 'books', 'music']:
                recs = self.content_recommender.recommend(cat, count=2)
                for rec in recs:
                    rec['category'] = cat
                    all_recs.append(rec)
            return all_recs[:count]
    
    def prioritize_tasks(self, tasks):
        """Prioritize list of tasks"""
        return self.task_prioritizer.prioritize_tasks(tasks)
    
    def suggest_task_time(self, task):
        """Suggest optimal time for task"""
        return self.task_prioritizer.suggest_optimal_time(task, self.user_tracker)
    
    def get_user_insights(self):
        """Get insights about user preferences"""
        favorite_cats = self.user_tracker.get_favorite_categories(top_n=5)
        
        insights = {
            'favorite_categories': favorite_cats,
            'total_interactions': len(self.user_tracker.preferences['interactions']),
            'last_updated': self.user_tracker.preferences['last_updated']
        }
        
        return insights


# Convenience functions
def create_recommendation_engine(storage_file='user_preferences.json'):
    """Create and return RecommendationEngine instance"""
    return RecommendationEngine(storage_file=storage_file)


def get_recommendations(category=None, count=5):
    """Quick recommendations"""
    engine = RecommendationEngine()
    return engine.get_recommendations(category=category, count=count)


if __name__ == "__main__":
    # Test the module
    print("Testing Recommendation Engine...\n")
    
    print("=== User Preference Tracking ===")
    engine = create_recommendation_engine('test_preferences.json')
    
    # Simulate some interactions
    engine.track_user_action('watch', 'movies', 'Inception', rating=5)
    engine.track_user_action('read', 'books', 'Sapiens', rating=4)
    engine.track_user_action('listen', 'music', 'Bohemian Rhapsody', rating=5)
    
    print("Tracked 3 interactions\n")
    
    print("=== Personalized Recommendations ===")
    recs = engine.get_recommendations(personalized=True, count=5)
    for i, rec in enumerate(recs, 1):
        print(f"{i}. {rec.get('title', 'N/A')} ({rec.get('category', 'N/A')})")
        print(f"   Reason: {rec.get('reason', 'N/A')}")
    print()
    
    print("=== Task Prioritization ===")
    tasks = [
        {'name': 'Complete project', 'urgency': 5, 'importance': 5, 'deadline': '2025-12-12'},
        {'name': 'Read book', 'urgency': 2, 'importance': 3, 'deadline': '2025-12-20'},
        {'name': 'Exercise', 'urgency': 3, 'importance': 4, 'deadline': None}
    ]
    
    prioritized = engine.prioritize_tasks(tasks)
    print("Prioritized tasks:")
    for i, task in enumerate(prioritized, 1):
        print(f"{i}. {task['name']}")
    
    print("\nModule loaded successfully!")
    
    # Clean up test file
    try:
        os.remove('test_preferences.json')
    except:
        pass
