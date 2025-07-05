#!/usr/bin/env python3
"""
Integrated Chat Handler for DSA Learning System with MongoDB Integration

This system:
1. Uses MongoDB for user data, chat history, and learning sessions
2. Uses real_graph_analyzer.py for gap analysis and topic suggestions
3. Integrates with Groq API for topic explanations
4. Uses YouTube API via groq_dsa_yt.py for video recommendations
5. Handles dynamic queries not in graph_data.json
6. Tracks user progress and learning sessions in MongoDB
"""

import json
import os
import sys
import requests
import time
import traceback
from typing import Dict, List, Optional, Tuple
from pathlib import Path
from datetime import datetime, timezone

# Add the current directory to path for imports
current_dir = Path(__file__).parent
sys.path.append(str(current_dir))
sys.path.append(str(current_dir / "static" / "graph"))
sys.path.append(str(current_dir / "dynamic"))
sys.path.append(str(current_dir.parent))  # Add backend directory

try:
    from real_graph_analyzer import RealGraphLearningAnalyzer
    from groq_dsa_yt import YouTubeResourceFinder
    from database.models import user_model, chat_history_model, learning_session_model
except ImportError as e:
    print(f"Import error: {e}")
    print("Trying alternative imports...")
    try:
        import sys
        sys.path.append(str(current_dir / "static" / "graph"))
        sys.path.append(str(current_dir / "dynamic"))
        sys.path.append(str(current_dir.parent))
        from real_graph_analyzer import RealGraphLearningAnalyzer
        from groq_dsa_yt import YouTubeResourceFinder
        from database.models import user_model, chat_history_model, learning_session_model
    except ImportError as e2:
        print(f"Alternative import error: {e2}")
        print("Please ensure real_graph_analyzer.py, groq_dsa_yt.py, and database models are in the correct locations")
        RealGraphLearningAnalyzer = None
        YouTubeResourceFinder = None
        user_model = None
        chat_history_model = None
        learning_session_model = None

class IntegratedChatHandler:
    def __init__(self):
        """Initialize the integrated chat handler with MongoDB support."""
        self.graph_data_path = current_dir / "static" / "graph" / "graph_data.json"
        
        # Initialize file paths for fallback storage
        self.unknown_queries_log = current_dir / "unknown_queries.json"
        self.learning_sessions_path = current_dir / "learning_sessions.json"
        self.frontend_public_path = current_dir / "frontend" / "public"
        
        # Initialize learning sessions storage
        self.learning_sessions = self.load_learning_sessions()
        
        # Initialize components
        try:
            if RealGraphLearningAnalyzer is not None:
                self.graph_analyzer = RealGraphLearningAnalyzer(str(self.graph_data_path))
            else:
                self.graph_analyzer = None
            
            if YouTubeResourceFinder is not None:
                self.youtube_finder = YouTubeResourceFinder()
            else:
                self.youtube_finder = None
                
            # MongoDB models
            self.user_model = user_model
            self.chat_history_model = chat_history_model
            self.learning_session_model = learning_session_model
            
        except Exception as e:
            print(f"Error initializing components: {e}")
            self.graph_analyzer = None
            self.youtube_finder = None
            self.user_model = None
            self.chat_history_model = None
            self.learning_session_model = None
        
    def load_user_profile(self, user_id: str) -> Optional[Dict]:
        """Load user profile from MongoDB. Returns None if user doesn't exist."""
        try:
            if not self.user_model:
                print("User model not available")
                return None
                
            user = self.user_model.get_user_by_id(user_id)
            if user:
                # Convert MongoDB user data to expected format
                profile = {
                    'user_id': user['_id'],
                    'email': user['email'],
                    'full_name': user['full_name'],
                    'skill_level': user['skill_level'],
                    'completed_topics': user['completed_topics'],
                    'known_concepts': user['known_concepts'],
                    'preferences': user.get('preferences', {}),
                    'statistics': user['statistics']
                }
                return profile
            
            # Return None if user not found (don't auto-create)
            return None
            
        except Exception as e:
            print(f"Error loading user profile: {e}")
            return None
    
    def create_default_user_profile(self, user_id: str = "default") -> Optional[Dict]:
        """Create a default user profile if none exists."""
        try:
            if not self.user_model:
                return None
            
            # Check if user already exists first
            existing_user = self.user_model.get_user_by_id(user_id)
            if existing_user:
                print(f"✅ User {user_id} already exists")
                return existing_user
            
            # Default user data for Ritesh Singh
            user_data = {
                "user_id": user_id,
                "email": "ritesh.singh@iitrpr.ac.in",
                "full_name": "Ritesh Singh",
                "skill_level": "intermediate",
                "completed_topics": [],
                "known_concepts": [],
                "preferences": {
                    "learning_style": "hands-on",
                    "difficulty_preference": "intermediate",
                    "time_per_session": 45,
                    "preferred_topics": ["dynamic_programming", "graph_algorithms", "system_design"]
                },
                "statistics": {
                    "total_queries": 0,
                    "topics_completed": 0,
                    "total_study_time": 0,
                    "last_active": datetime.now(timezone.utc),
                    "streak_days": 0,
                    "sessions_completed": 0
                },
                "profile_data": {
                    "university": "IIT Ropar",
                    "degree": "Computer Science",
                    "year": "3rd Year",
                    "interests": ["Machine Learning", "Data Structures", "Algorithms", "Web Development"],
                    "programming_languages": ["Python", "JavaScript", "Java", "C++"],
                    "goals": ["Master DSA", "Prepare for interviews", "Build projects"]
                },
                "learning_history": {
                    "topics_explored": [],
                    "videos_watched": [],
                    "concepts_mastered": [],
                    "time_spent": {}
                }
            }
            
            # Create user in MongoDB
            created_user_id = self.user_model.create_user(user_data)
            if created_user_id:
                print(f"✅ Created comprehensive user profile for {user_data['full_name']}")
                # Fetch the created user to return
                created_user = self.user_model.get_user_by_id(created_user_id)
                
                # Convert MongoDB format to expected format
                if created_user:
                    profile = {
                        'user_id': str(created_user['_id']),
                        'email': created_user['email'],
                        'full_name': created_user['full_name'],
                        'skill_level': created_user['skill_level'],
                        'completed_topics': created_user['completed_topics'],
                        'known_concepts': created_user['known_concepts'],
                        'preferences': created_user.get('preferences', {}),
                        'statistics': created_user['statistics'],
                        'profile_data': created_user.get('profile_data', {}),
                        'learning_history': created_user.get('learning_history', {})
                    }
                    return profile
                return created_user
            else:
                print("❌ Failed to create default user")
                return None
                
        except Exception as e:
            print(f"❌ Error creating default user profile: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def create_user_profile_with_info(self, user_id: str, email: str, full_name: str) -> Optional[Dict]:
        """Create a user profile with specific email and name information."""
        try:
            if not self.user_model:
                return None
                
            # Check if user already exists
            existing_user = self.user_model.get_user_by_id(user_id)
            if existing_user:
                print(f"✅ User {user_id} already exists")
                return existing_user
            
            # Create comprehensive user profile with provided information
            user_data = {
                "user_id": user_id,
                "email": email,
                "full_name": full_name,
                "skill_level": "beginner",
                "completed_topics": [],
                "known_concepts": [],
                "preferences": {
                    "learning_style": "visual",
                    "difficulty_preference": "beginner",
                    "time_per_session": 30,
                    "preferred_topics": ["arrays", "strings", "basic_algorithms"]
                },
                "statistics": {
                    "total_queries": 0,
                    "topics_completed": 0,
                    "total_study_time": 0,
                    "last_active": datetime.now(timezone.utc),
                    "streak_days": 0,
                    "sessions_completed": 0
                },
                "profile_data": {
                    "university": "Not specified",
                    "degree": "Not specified",
                    "year": "Not specified",
                    "interests": ["Data Structures", "Algorithms", "Programming"],
                    "programming_languages": ["Python", "JavaScript"],
                    "goals": ["Learn DSA", "Improve coding skills"]
                },
                "learning_history": {
                    "topics_explored": [],
                    "videos_watched": [],
                    "concepts_mastered": [],
                    "time_spent": {}
                }
            }
            
            # Create user in MongoDB
            created_user_id = self.user_model.create_user(user_data)
            if created_user_id:
                print(f"✅ Created user profile for {full_name} ({email})")
                # Fetch the created user to return
                created_user = self.user_model.get_user_by_id(created_user_id)
                
                # Convert MongoDB format to expected format
                if created_user:
                    profile = {
                        'user_id': str(created_user['_id']),
                        'email': created_user['email'],
                        'full_name': created_user['full_name'],
                        'skill_level': created_user['skill_level'],
                        'completed_topics': created_user['completed_topics'],
                        'known_concepts': created_user['known_concepts'],
                        'preferences': created_user.get('preferences', {}),
                        'statistics': created_user['statistics'],
                        'profile_data': created_user.get('profile_data', {}),
                        'learning_history': created_user.get('learning_history', {})
                    }
                    return profile
                return created_user
            else:
                print("❌ Failed to create user with info")
                return None
                
        except Exception as e:
            print(f"❌ Error creating user profile with info: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def analyze_user_query(self, query: str, user_profile: Dict, chat_history: List[Dict] = None) -> Dict:
        """Analyze user query and determine response strategy."""
        query_lower = query.lower()
        
        # Detect learning flow intents
        learning_intents = self.detect_learning_intents(query_lower, chat_history or [])
        
        # Check if this is small talk/general conversation
        small_talk_keywords = [
            'hello', 'hi', 'hey', 'good morning', 'good afternoon', 'good evening',
            'how are you', 'what\'s up', 'thanks', 'thank you', 'bye', 'goodbye',
            'nice', 'cool', 'awesome', 'great', 'who are you', 'what can you do'
        ]
        
        # More precise small talk detection - check for exact phrases or word boundaries
        is_small_talk = False
        for keyword in small_talk_keywords:
            if keyword in query_lower:
                # Check if it's a standalone greeting or the query is very short
                if len(query_lower.strip()) <= 20 and any(greet in query_lower for greet in ['hello', 'hi', 'hey', 'thanks', 'bye']):
                    is_small_talk = True
                    break
                elif keyword in ['how are you', 'what\'s up', 'who are you', 'what can you do']:
                    is_small_talk = True
                    break
        
        # Override small talk detection for DSA-related queries
        dsa_indicators = [
            'learn', 'algorithm', 'data structure', 'array', 'tree', 'graph', 'sort', 'search',
            'stack', 'queue', 'heap', 'hash', 'linked list', 'binary', 'dynamic programming',
            'recursion', 'complexity', 'big o', 'time complexity', 'space complexity',
            'what is', 'what are', 'how to', 'explain', 'understand', 'implement', 'code',
            'example', 'tutorial', 'difference between', 'comparison', 'vs', 'versus'
        ]
        
        if any(indicator in query_lower for indicator in dsa_indicators):
            is_small_talk = False
        
        # Extract known concepts from user profile - properly validate topic knowledge
        truly_known_topics = []
        known_subtopics = []
        
        if 'knownConcepts' in user_profile and self.graph_analyzer:
            topics_data = user_profile['knownConcepts'].get('topics', [])
            for topic_data in topics_data:
                topic_name = topic_data['name']
                user_subtopics = set([sub['name'].lower() for sub in topic_data.get('subtopics', [])])
                
                # Find this topic in the graph
                topic_node = None
                for node in self.graph_analyzer.graph_data.get('nodes', []):
                    if node['type'] == 'topic' and node['name'].lower() == topic_name.lower():
                        topic_node = node
                        break
                
                if topic_node:
                    # Get all subtopics for this topic from the graph
                    required_subtopics = set()
                    for node in self.graph_analyzer.graph_data.get('nodes', []):
                        if (node['type'] == 'subtopic' and 
                            node.get('parent_topic') == topic_node['id']):
                            required_subtopics.add(node['name'].lower())
                    
                    # Check if user knows all required subtopics
                    if required_subtopics and user_subtopics.issuperset(required_subtopics):
                        truly_known_topics.append(topic_name)
                    
                    # Add known subtopics
                    known_subtopics.extend([sub['name'] for sub in topic_data.get('subtopics', [])])
        
        # Determine if query is about a specific DSA topic/concept
        mentioned_topics = []
        mentioned_subtopics = []
        
        if self.graph_analyzer and not is_small_talk:
            # Check if query mentions any topics/subtopics from the graph
            for node in self.graph_analyzer.graph_data.get('nodes', []):
                node_name = node['name'].lower()
                node_keywords = [kw.lower() for kw in node.get('keywords', [])]
                
                # Enhanced matching logic
                query_words = query_lower.split()
                
                # Check for exact matches or keyword matches
                if (node_name in query_lower or 
                    any(keyword in query_lower for keyword in node_keywords) or
                    any(word in node_name for word in query_words if len(word) > 3) or
                    # Check for partial matches with common variations
                    any(node_name.startswith(word) or word.startswith(node_name) 
                        for word in query_words if len(word) > 4)):
                    
                    if node['type'] == 'topic':
                        mentioned_topics.append(node)
                    else:
                        mentioned_subtopics.append(node)
        
        return {
            'query': query,
            'is_small_talk': is_small_talk,
            'learning_intent': learning_intents,
            'truly_known_topics': truly_known_topics,
            'known_subtopics': known_subtopics,
            'mentioned_topics': mentioned_topics,
            'mentioned_subtopics': mentioned_subtopics,
            'is_graph_topic': len(mentioned_topics) > 0 or len(mentioned_subtopics) > 0
        }
    
    def detect_learning_intents(self, query: str, chat_history: List[Dict]) -> Dict:
        """Detect user intents related to learning flow progression."""
        intents = {
            'wants_next_topic': False,
            'confirms_understanding': False,
            'needs_more_explanation': False,
            'wants_to_complete_topic': False,
            'satisfied_with_topic': False,
            'wants_confirmation': False,
            'says_no_need_help': False
        }
        
        # Intent patterns
        next_topic_patterns = [
            'next topic', 'next step', 'what\'s next', 'continue', 'move on', 'proceed',
            'go to next', 'advance', 'ready for next', 'next lesson'
        ]
        
        understanding_patterns = [
            'yes', 'got it', 'understand', 'clear', 'makes sense', 'i know', 'learned',
            'understood', 'ok', 'okay', 'right', 'correct', 'good', 'thanks',
            'i understand this topic', 'i get it'
        ]
        
        more_explanation_patterns = [
            'no', 'don\'t understand', 'confused', 'explain more', 'not clear', 
            'can you explain', 'i don\'t get it', 'more details', 'elaborate',
            'need help', 'still confused', 'more examples', 'i need more explanation'
        ]
        
        completion_patterns = [
            'i\'m done', 'completed', 'finished', 'mastered', 'ready to move on',
            'i know this now', 'learned this', 'understand this topic'
        ]
        
        satisfaction_patterns = [
            'satisfied', 'good enough', 'ready', 'confident', 'comfortable',
            'i am satisfied', 'add to profile', 'add to my profile',
            'i am satisfied with this topic', 'ready to add it to my profile'
        ]
        
        confirmation_patterns = [
            'yes', 'yeah', 'yep', 'sure', 'of course', 'definitely', 'absolutely'
        ]
        
        no_help_patterns = [
            'no', 'nope', 'not really', 'i\'m good', 'no thanks', 'no need'
        ]
        
        # Check patterns
        for pattern in next_topic_patterns:
            if pattern in query:
                intents['wants_next_topic'] = True
                break
                
        for pattern in understanding_patterns:
            if pattern in query:
                intents['confirms_understanding'] = True
                break
                
        for pattern in more_explanation_patterns:
            if pattern in query:
                intents['needs_more_explanation'] = True
                break
                
        for pattern in completion_patterns:
            if pattern in query:
                intents['wants_to_complete_topic'] = True
                break
                
        for pattern in satisfaction_patterns:
            if pattern in query:
                intents['satisfied_with_topic'] = True
                break
        
        for pattern in confirmation_patterns:
            if pattern in query:
                intents['wants_confirmation'] = True
                break
        
        for pattern in no_help_patterns:
            if pattern in query:
                intents['says_no_need_help'] = True
                break
        
        return intents
    
    def find_learning_gaps(self, query_analysis: Dict, user_profile: Dict) -> Dict:
        """Use graph analyzer to find learning gaps and suggest learning paths."""
        if not self.graph_analyzer:
            return {'gaps': [], 'suggestions': [], 'learning_path': []}
        
        try:
            # Get user's truly known concepts (only topics where all subtopics are known)
            known_topic_names = query_analysis['truly_known_topics']
            known_subtopic_names = query_analysis['known_subtopics']
            
            # Convert to graph node IDs
            known_concept_ids = []
            
            # Add truly known topics
            for topic_name in known_topic_names:
                topic_id = self.graph_analyzer.topic_name_to_id.get(topic_name.lower())
                if topic_id:
                    known_concept_ids.append(topic_id)
            
            # Add known subtopics
            for subtopic_name in known_subtopic_names:
                subtopic_id = self.graph_analyzer.subtopic_name_to_id.get(subtopic_name.lower())
                if subtopic_id:
                    known_concept_ids.append(subtopic_id)
            
            # If query mentions specific topics, find path to those topics
            target_topics = query_analysis['mentioned_topics']
            target_subtopics = query_analysis['mentioned_subtopics']
            
            if target_topics or target_subtopics:
                # Use the first mentioned topic/subtopic as target
                target_node = target_topics[0] if target_topics else target_subtopics[0]
                target_id = target_node['id']
                
                # Use the real graph analyzer methods
                try:
                    # Find optimal learning path using the graph analyzer
                    if hasattr(self.graph_analyzer, 'find_optimal_learning_path'):
                        learning_path_result = self.graph_analyzer.find_optimal_learning_path(
                            completed_topics=known_concept_ids,
                            target_topic=target_id
                        )
                        # Extract path from result
                        learning_path = learning_path_result.get('path', []) if isinstance(learning_path_result, dict) else []
                    else:
                        learning_path = []
                    
                    # Find gaps using subtopic analysis
                    if hasattr(self.graph_analyzer, 'analyze_subtopic_learning_gaps'):
                        gaps_result = self.graph_analyzer.analyze_subtopic_learning_gaps(
                            completed_subtopics=known_concept_ids,
                            target_topic_id=target_id
                        )
                        # Extract gaps from result
                        if isinstance(gaps_result, dict):
                            gaps = gaps_result.get('missing_prerequisites', []) + gaps_result.get('recommended_subtopics', [])
                        else:
                            gaps = []
                    else:
                        gaps = []
                    
                    # Convert IDs back to names for frontend display
                    gap_names = []
                    for gap_id in gaps[:5]:  # Top 5 gaps
                        gap_node = self.graph_analyzer.all_id_to_data.get(gap_id)
                        if gap_node:
                            gap_names.append(gap_node['name'])
                    
                    path_names = []
                    for step_id in learning_path[:7]:  # Top 7 steps
                        step_node = self.graph_analyzer.all_id_to_data.get(step_id)
                        if step_node:
                            path_names.append(step_node['name'])
                    
                    return {
                        'gaps': gap_names,
                        'learning_path': path_names,
                        'target_topic': target_node,
                        'known_concepts': known_topic_names + known_subtopic_names
                    }
                    
                except Exception as method_error:
                    print(f"Error calling graph analyzer methods: {method_error}")
                    # Fallback to basic analysis
                    return {
                        'gaps': [],
                        'learning_path': [],
                        'target_topic': target_node,
                        'known_concepts': known_topic_names + known_subtopic_names
                    }
            
            # General gap analysis for comprehensive learning
            try:
                if hasattr(self.graph_analyzer, 'analyze_learning_gap_with_real_graph'):
                    # Use the comprehensive analysis method
                    known_topic_names = [self.graph_analyzer.all_id_to_data.get(id, {}).get('name', '') for id in known_concept_ids]
                    comprehensive_result = self.graph_analyzer.analyze_learning_gap_with_real_graph(
                        completed_topics_names=known_topic_names,
                        target_topic_name="General Learning"
                    )
                    
                    if isinstance(comprehensive_result, dict):
                        gap_names = comprehensive_result.get('recommended_topics', [])[:5]
                    else:
                        gap_names = []
                else:
                    gap_names = []
                
                return {
                    'gaps': gap_names,
                    'learning_path': [],
                    'suggestions': gap_names[:3],  # Top 3 suggestions
                    'known_concepts': known_topic_names + known_subtopic_names
                }
                
            except Exception as comp_error:
                print(f"Error in comprehensive gap analysis: {comp_error}")
                return {
                    'gaps': [],
                    'learning_path': [],
                    'suggestions': [],
                    'known_concepts': known_topic_names + known_subtopic_names
                }
            
        except Exception as e:
            print(f"Error in gap analysis: {e}")
            return {'gaps': [], 'suggestions': [], 'learning_path': []}
    
    def generate_mistral_response(self, query: str, context: Dict) -> str:
        """Generate response using Groq AI API instead of local Ollama."""
        try:
            # Handle small talk with direct responses
            if context.get('is_small_talk'):
                return self.generate_fallback_response(query, context)
            
            # Prepare context for Groq for DSA queries
            system_prompt = """You are an expert DSA (Data Structures and Algorithms) tutor. 
            Provide clear, concise explanations of concepts, include code examples when helpful, 
            and give practical learning advice. Keep responses focused and educational.
            Always be encouraging and supportive."""
            
            user_context = ""
            if context.get('target_topic'):
                topic = context['target_topic']
                user_context += f"\nUser is asking about: {topic['name']}"
                if topic.get('description'):
                    user_context += f"\nTopic description: {topic['description']}"
            
            if context.get('gaps') and len(context['gaps']) > 0:
                gaps = context['gaps'][:3]  # Top 3 gaps
                user_context += f"\nUser's learning gaps: {', '.join(gaps)}"
            
            if context.get('learning_path') and len(context['learning_path']) > 0:
                path = context['learning_path'][:5]  # First 5 steps
                user_context += f"\nSuggested learning path: {' → '.join(path)}"
            
            if context.get('known_concepts') and len(context['known_concepts']) > 0:
                known = context['known_concepts'][:5]
                user_context += f"\nUser already knows: {', '.join(known)}"
            
            prompt = f"{query}\n\nContext:{user_context}"
            
            # Get Groq API key from environment
            groq_api_key = os.getenv("GROQ_API_KEY")
            if not groq_api_key:
                print("❌ GROQ_API_KEY not found in environment variables")
                return self.generate_fallback_response(query, context)
            
            # Use Groq API
            headers = {
                "Authorization": f"Bearer {groq_api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": "mistral-saba-24b",
                "messages": [
                    {
                        "role": "system",
                        "content": system_prompt
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "temperature": 0.3,
                "max_tokens": 4096,
                "top_p": 0.9
            }
            
            response = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers=headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return result["choices"][0]["message"]["content"].strip()
            else:
                print(f"Groq API error: {response.status_code} - {response.text}")
                return self.generate_fallback_response(query, context)
                
        except requests.exceptions.ConnectionError:
            print("Error: Could not connect to Groq API server.")
            return self.generate_fallback_response(query, context)
        except Exception as e:
            print(f"Error generating Groq response: {e}")
            traceback.print_exc()
            return self.generate_fallback_response(query, context)
    
    def generate_fallback_response(self, query: str, context: Dict) -> str:
        """Generate a comprehensive fallback response when Mistral API is not available."""
        response_parts = []
        
        # Handle small talk
        if context.get('is_small_talk'):
            small_talk_responses = {
                'hello': "Hello! I'm your DSA learning assistant. How can I help you today?",
                'hi': "Hi there! Ready to dive into some data structures and algorithms?",
                'how are you': "I'm doing great and ready to help you learn DSA! What would you like to explore?",
                'thanks': "You're welcome! Feel free to ask me anything about data structures and algorithms.",
                'bye': "Goodbye! Keep practicing those algorithms. See you next time!",
                'who are you': "I'm your AI DSA tutor! I can help you learn data structures, algorithms, find learning gaps, and recommend resources.",
                'what can you do': "I can help you with DSA concepts, analyze your learning gaps, suggest learning paths, and find educational videos. Just ask me about any topic!",
                'help': "I'm here to help! You can ask me about specific DSA topics like arrays, trees, sorting algorithms, or ask for learning recommendations based on your profile."
            }
            
            query_lower = query.lower()
            for keyword, response in small_talk_responses.items():
                if keyword in query_lower:
                    return response
            
            return "Hello! I'm your DSA learning assistant. Feel free to ask me about any data structures or algorithms topic!"
        
        # Enhanced DSA explanations
        topic_explanations = {
            'array': "Arrays are linear data structures that store elements in contiguous memory locations. They allow random access to elements using indices and are fundamental to many algorithms. Key operations include insertion, deletion, traversal, and searching.",
            'searching': "Searching algorithms help find specific elements in data structures. Common types include linear search (O(n)) which checks each element sequentially, and binary search (O(log n)) which works on sorted arrays by repeatedly dividing the search space in half.",
            'sorting': "Sorting algorithms arrange elements in a specific order. Popular algorithms include bubble sort, insertion sort, merge sort, and quick sort. Each has different time complexities and use cases.",
            'tree': "Trees are hierarchical data structures with a root node and child nodes. They're used for efficient searching, sorting, and representing hierarchical data. Common types include binary trees, BSTs, and AVL trees.",
            'graph': "Graphs consist of vertices (nodes) and edges (connections). They model relationships between entities and are used in networking, social media, and pathfinding algorithms.",
            'stack': "Stacks follow the Last-In-First-Out (LIFO) principle. They support push (add) and pop (remove) operations. Used in function calls, expression evaluation, and undo operations.",
            'queue': "Queues follow the First-In-First-Out (FIFO) principle. They support enqueue (add) and dequeue (remove) operations. Used in scheduling, breadth-first search, and buffering.",
            'hash': "Hash tables use hash functions to map keys to values, providing O(1) average-case lookup time. They handle collisions through chaining or open addressing.",
            'linked list': "Linked lists store elements in nodes, where each node contains data and a reference to the next node. They allow dynamic size and efficient insertion/deletion.",
            'dynamic programming': "Dynamic programming solves complex problems by breaking them into simpler subproblems and storing results to avoid redundant calculations.",
            'recursion': "Recursion involves functions calling themselves with modified parameters. It's useful for problems that can be broken down into similar smaller problems.",
            'divide and conquer': "This approach divides problems into smaller subproblems, solves them independently, and combines results. Examples include merge sort and quick sort."
        }
        
        # Generate detailed explanation based on target topic
        if context.get('target_topic'):
            topic = context['target_topic']
            topic_name = topic['name'].lower()
            
            # Find matching explanation
            explanation = None
            for key, exp in topic_explanations.items():
                if key in topic_name:
                    explanation = exp
                    break
            
            if explanation:
                response_parts.append(f"📚 **{topic['name']}**: {explanation}")
            else:
                response_parts.append(f"Great question about **{topic['name']}**! This is an important concept in data structures and algorithms.")
        
        # Add learning path information
        if context.get('learning_path') and len(context['learning_path']) > 0:
            path = context['learning_path'][:5]
            response_parts.append(f"🛤️ **Suggested learning path**: {' → '.join(path)}")
        
        # Add gap analysis
        if context.get('gaps') and len(context['gaps']) > 0:
            gaps = context['gaps'][:3]
            response_parts.append(f"📋 **Focus areas for you**: {', '.join(gaps)}")
        
        # Add foundation knowledge
        if context.get('known_concepts') and len(context['known_concepts']) > 0:
            known = context['known_concepts'][:3]
            response_parts.append(f"✅ **Great foundation! You already know**: {', '.join(known)}")
        
        # Add specific tips based on query content
        query_lower = query.lower()
        if 'time complexity' in query_lower or 'big o' in query_lower:
            response_parts.append("⏱️ **Time Complexity Tip**: Always analyze the worst-case scenario and look for nested loops or recursive calls.")
        elif 'space complexity' in query_lower:
            response_parts.append("💾 **Space Complexity Tip**: Consider the extra memory used by your algorithm, including recursive call stacks.")
        elif 'interview' in query_lower:
            response_parts.append("🎯 **Interview Tip**: Practice explaining your thought process and always test with edge cases.")
        
        # Fallback based on query keywords
        if not response_parts:
            if 'sort' in query_lower:
                response_parts.append("🔄 **Sorting**: Essential for organizing data efficiently. Start with simple algorithms like bubble sort, then move to more efficient ones like merge sort and quick sort.")
            elif 'search' in query_lower:
                response_parts.append("🔍 **Searching**: Master linear search first, then binary search for sorted data. Understanding these fundamentals opens doors to more advanced algorithms.")
            elif 'array' in query_lower:
                response_parts.append("📊 **Arrays**: The foundation of many data structures. Master traversal, insertion, deletion, and searching before moving to more complex topics.")
            else:
                response_parts.append("🚀 **Let's learn together!** I'll help you understand this concept step by step with practical examples and clear explanations.")
        
        return "\n\n".join(response_parts)
    
    def get_video_recommendations(self, query: str, context: Dict) -> List[Dict]:
        """Get YouTube video recommendations using the existing YouTube finder."""
        if not self.youtube_finder:
            return []
        
        try:
            # Determine search terms based on context
            search_terms = []
            
            if context.get('target_topic'):
                search_terms.append(context['target_topic']['name'])
            
            if context.get('gaps'):
                gaps = context['gaps'][:2]  # Top 2 gaps
                for gap in gaps:
                    gap_name = self.graph_analyzer.all_id_to_data.get(gap, {}).get('name')
                    if gap_name:
                        search_terms.append(gap_name)
            
            if not search_terms:
                # Extract key terms from the query
                query_words = query.lower().split()
                dsa_keywords = ['array', 'linked list', 'stack', 'queue', 'tree', 'graph', 
                               'sorting', 'searching', 'dynamic programming', 'recursion']
                search_terms = [word for word in query_words if word in dsa_keywords]
                
                if not search_terms:
                    search_terms = [query]
            
            # Get videos for each search term
            all_videos = []
            for term in search_terms[:2]:  # Limit to 2 terms to avoid too many API calls
                videos = self.youtube_finder.get_videos(term)
                all_videos.extend(videos)
            
            # Convert to the format expected by the frontend
            formatted_videos = []
            for video in all_videos[:5]:  # Limit to 5 videos total
                formatted_videos.append({
                    'title': video.title,
                    'url': video.url,
                    'description': video.description or f"Learn about {video.title}",
                    'channel': video.channel_name,
                    'duration': video.duration,
                    'views': video.view_count
                })
            
            return formatted_videos
            
        except Exception as e:
            print(f"Error getting video recommendations: {e}")
            return []
    
    def log_unknown_query(self, query: str, timestamp: str):
        """Log queries that don't match anything in the graph for future analysis."""
        try:
            # Load existing log or create new one
            if self.unknown_queries_log.exists():
                with open(self.unknown_queries_log, 'r', encoding='utf-8') as f:
                    log_data = json.load(f)
            else:
                log_data = {'queries': []}
            
            # Add new query
            log_data['queries'].append({
                'query': query,
                'timestamp': timestamp,
                'processed': False
            })
            
            # Save updated log
            with open(self.unknown_queries_log, 'w', encoding='utf-8') as f:
                json.dump(log_data, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            print(f"Error logging unknown query: {e}")
    
    def load_learning_sessions(self) -> Dict:
        """Load learning sessions from file."""
        try:
            if self.learning_sessions_path.exists():
                with open(self.learning_sessions_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return {}
        except Exception as e:
            print(f"Error loading learning sessions: {e}")
            return {}
    
    def save_learning_sessions(self):
        """Save learning sessions to file."""
        try:
            with open(self.learning_sessions_path, 'w', encoding='utf-8') as f:
                json.dump(self.learning_sessions, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving learning sessions: {e}")
    
    def get_learning_session(self, user_id: str) -> Dict:
        """Get or create learning session for user."""
        if user_id not in self.learning_sessions:
            self.learning_sessions[user_id] = {
                'current_path': [],
                'completed_topics': [],
                'current_step_index': 0,
                'target_topic': None,
                'session_started': datetime.now().isoformat(),
                'last_updated': datetime.now().isoformat()
            }
            self.save_learning_sessions()
        return self.learning_sessions[user_id]
    
    def update_learning_session(self, user_id: str, updates: Dict):
        """Update learning session for user with MongoDB integration."""
        try:
            if self.learning_session_model:
                # Update in MongoDB
                session = self.learning_session_model.get_active_session(user_id)
                if session:
                    updates['updated_at'] = datetime.now()
                    self.learning_session_model.update_session_progress(session['_id'], updates)
                    return
            
            # Fallback to local storage
            session = self.get_learning_session(user_id)
            session.update(updates)
            session['last_updated'] = datetime.now().isoformat()
            self.save_learning_sessions()
            
        except Exception as e:
            print(f"Error updating learning session: {e}")
            # Fallback to local storage
            session = self.get_learning_session(user_id)
            session.update(updates)
            session['last_updated'] = datetime.now().isoformat()
            self.save_learning_sessions()
    
    def complete_current_topic(self, user_id: str) -> bool:
        """Mark current topic as completed and advance to next with MongoDB integration."""
        try:
            if self.learning_session_model:
                # Get session from MongoDB
                session = self.learning_session_model.get_active_session(user_id)
                if session and session.get('current_path') and session.get('current_step_index', 0) < len(session['current_path']):
                    completed_topic = session['current_path'][session['current_step_index']]
                    
                    # Update session in MongoDB
                    update_data = {
                        '$push': {
                            'completed_topics': {
                                'topic': completed_topic,
                                'completed_at': datetime.now()
                            }
                        },
                        '$inc': {'current_step_index': 1},
                        '$set': {'updated_at': datetime.now()}
                    }
                    
                    return self.learning_session_model.update_session_progress(session['_id'], update_data)
                return False
            
            # Fallback to local storage
            session = self.get_learning_session(user_id)
            if session['current_path'] and session['current_step_index'] < len(session['current_path']):
                completed_topic = session['current_path'][session['current_step_index']]
                session['completed_topics'].append({
                    'topic': completed_topic,
                    'completed_at': datetime.now().isoformat()
                })
                session['current_step_index'] += 1
                self.save_learning_sessions()
                return True
            return False
            
        except Exception as e:
            print(f"Error completing current topic: {e}")
            # Fallback to local storage
            session = self.get_learning_session(user_id)
            if session['current_path'] and session['current_step_index'] < len(session['current_path']):
                completed_topic = session['current_path'][session['current_step_index']]
                session['completed_topics'].append({
                    'topic': completed_topic,
                    'completed_at': datetime.now().isoformat()
                })
                session['current_step_index'] += 1
                self.save_learning_sessions()
                return True
            return False
    
    def add_topic_to_user_profile(self, topic_name: str, user_id: str = "default") -> bool:
        """Add completed topic to user profile with MongoDB integration."""
        try:
            if not self.user_model:
                # Fallback to local storage
                return self._add_topic_to_local_profile(topic_name)
            
            user_profile = self.load_user_profile(user_id)
            if not user_profile:
                return False
            
            # Check if topic already exists
            existing_topics = [t.lower() for t in user_profile.get('completed_topics', [])]
            if topic_name.lower() not in existing_topics:
                # Update MongoDB user document
                update_data = {
                    '$push': {'completed_topics': topic_name},
                    '$inc': {'statistics.topics_completed': 1},
                    '$set': {'updated_at': datetime.now()}
                }
                
                return self.user_model.update_user(user_id, update_data)
            
            return True  # Topic already exists
            
        except Exception as e:
            print(f"Error adding topic to user profile: {e}")
            # Fallback to local storage
            return self._add_topic_to_local_profile(topic_name)
    
    def _add_topic_to_local_profile(self, topic_name: str) -> bool:
        """Fallback method for local storage."""
        try:
            user_profile = self.load_user_profile()
            if not user_profile:
                return False
            
            # Add topic to known concepts
            if 'knownConcepts' not in user_profile:
                user_profile['knownConcepts'] = {'topics': [], 'totalTopics': 0, 'totalSubtopics': 0}
            
            # Check if topic already exists
            existing_topics = [t['name'].lower() for t in user_profile['knownConcepts']['topics']]
            if topic_name.lower() not in existing_topics:
                # Find topic details from graph
                topic_data = None
                if self.graph_analyzer:
                    for node in self.graph_analyzer.graph_data.get('nodes', []):
                        if node['type'] == 'topic' and node['name'].lower() == topic_name.lower():
                            topic_data = {
                                'id': node['id'],
                                'name': node['name'],
                                'type': 'topic',
                                'subtopics': []  # Start with empty subtopics
                            }
                            break
                
                if topic_data:
                    user_profile['knownConcepts']['topics'].append(topic_data)
                    user_profile['knownConcepts']['totalTopics'] += 1
                    
                    # Save updated profile
                    profile_files = list(self.frontend_public_path.glob("user_profile_*.json"))
                    if profile_files:
                        latest_profile = max(profile_files, key=lambda p: p.stat().st_mtime)
                        with open(latest_profile, 'w', encoding='utf-8') as f:
                            json.dump(user_profile, f, indent=2, ensure_ascii=False)
                        return True
            return False
        except Exception as e:
            print(f"Error adding topic to user profile: {e}")
            return False
    
    def create_default_user_profile(self, user_id: str) -> Optional[Dict]:
        """Create a default user profile if none exists."""
        try:
            if not self.user_model:
                # Fallback to local storage
                return self._create_default_local_profile(user_id)
            
            # Check if user already exists
            existing_user = self.user_model.get_user_by_id(user_id)
            if existing_user:
                return existing_user
            
            # Create new user with default values
            default_user_data = {
                'user_id': user_id,
                'email': f"{user_id}@default.com",
                'full_name': f"User {user_id}",
                'skill_level': 'beginner',
                'completed_topics': [],
                'known_concepts': [],
                'preferences': {
                    'learning_style': 'visual',
                    'difficulty_level': 'beginner'
                }
            }
            
            # Create user in MongoDB
            new_user_id = self.user_model.create_user(default_user_data)
            if new_user_id:
                print(f"✅ Created default user profile for: {user_id}")
                return self.user_model.get_user_by_id(new_user_id)
            else:
                print(f"❌ Failed to create default user profile for: {user_id}")
                return None
                
        except Exception as e:
            print(f"Error creating default user profile: {e}")
            # Fallback to local storage
            return self._create_default_local_profile(user_id)
    
    def _create_default_local_profile(self, user_id: str) -> Optional[Dict]:
        """Create default local user profile as fallback."""
        try:
            default_profile = {
                'user_id': user_id,
                'email': f"{user_id}@default.com",
                'full_name': f"User {user_id}",
                'skill_level': 'beginner',
                'completed_topics': [],
                'known_concepts': [],
                'preferences': {
                    'learning_style': 'visual',
                    'difficulty_level': 'beginner'
                },
                'statistics': {
                    'total_queries': 0,
                    'topics_completed': 0,
                    'total_study_time': 0,
                    'last_active': datetime.now().isoformat()
                }
            }
            
            print(f"✅ Created default local user profile for: {user_id}")
            return default_profile
            
        except Exception as e:
            print(f"Error creating default local user profile: {e}")
            return None
    
    def handle_chat_message(self, message: str, chat_history: List[Dict] = None, user_id: str = "default") -> Dict:
        """Main handler for chat messages with learning flow support and MongoDB integration."""
        timestamp = datetime.now().isoformat()
        
        try:
            # Load user profile from MongoDB
            user_profile = self.load_user_profile(user_id)
            if not user_profile:
                # Create a default user profile if none exists
                user_profile = self.create_default_user_profile(user_id)
                if not user_profile:
                    return {
                        'response': "I couldn't create your user profile. Please try again later.",
                        'videos': [],
                        'analysis': {'error': 'Failed to create user profile'}
                    }
            
            # Get or create learning session
            learning_session = self.get_or_create_learning_session(user_id)
            
            # Get recent chat context from MongoDB if chat_history is not provided
            if not chat_history and self.chat_history_model:
                chat_history = self.chat_history_model.get_recent_context(user_id, limit=5)
            
            # Analyze the query with chat history context
            query_analysis = self.analyze_user_query(message, user_profile, chat_history or [])
            
            # Generate response
            response_data = self._process_query_analysis(message, user_id, user_profile, learning_session, query_analysis, chat_history or [])
            
            # Save chat message to MongoDB
            if self.chat_history_model:
                self.chat_history_model.save_chat_message(
                    user_id=user_id,
                    message=message,
                    response=response_data['response'],
                    analysis=response_data.get('analysis', {})
                )
            
            # Update user statistics
            if self.user_model:
                self.user_model.update_user(user_id, {
                    'statistics.total_queries': user_profile['statistics']['total_queries'] + 1,
                    'statistics.last_active': datetime.now()
                })
            
            return response_data
            
        except Exception as e:
            print(f"Error in handle_chat_message: {e}")
            import traceback
            traceback.print_exc()
            return {
                'response': "I'm sorry, I encountered an error while processing your request. Please try again.",
                'videos': [],
                'analysis': {'error': str(e)}
            }
    
    def _process_query_analysis(self, message: str, user_id: str, user_profile: Dict, learning_session: Dict, query_analysis: Dict, chat_history: List[Dict]) -> Dict:
        """Process query analysis and generate appropriate response."""
        # Handle learning flow intents first
        if query_analysis.get('learning_intent', {}).get('satisfied_with_topic'):
            return self.handle_topic_completion(user_id, learning_session, query_analysis)
        
        if query_analysis.get('learning_intent', {}).get('wants_next_topic') or query_analysis.get('learning_intent', {}).get('confirms_understanding'):
            return self.handle_next_topic_request(user_id, learning_session, query_analysis)
        
        if query_analysis.get('learning_intent', {}).get('needs_more_explanation'):
            return self.handle_more_explanation_request(message, learning_session, query_analysis, chat_history)
        
        if query_analysis.get('learning_intent', {}).get('wants_to_complete_topic'):
            return self.handle_topic_completion(user_id, learning_session, query_analysis)
        
        if query_analysis.get('learning_intent', {}).get('says_no_need_help'):
            return self.handle_no_response(user_id, learning_session, query_analysis, chat_history)
        
        # Handle small talk
        if query_analysis['is_small_talk']:
            response = self.generate_mistral_response(message, {'is_small_talk': True})
            return {
                'response': response,
                'videos': [],
                'analysis': {
                    'small_talk': True,
                    'known_topics': query_analysis['truly_known_topics']
                }
            }
        
        # Check if this is a DSA topic we have in our graph
        if query_analysis['is_graph_topic']:
            # Use graph-based analysis
            gap_analysis = self.find_learning_gaps(query_analysis, user_profile)

            # Update learning session with new path
            learning_path = gap_analysis.get('learning_path', [])
            if learning_path:
                self.update_learning_session(user_id, {
                    'current_path': learning_path,
                    'current_step_index': 0,
                    'target_topic': gap_analysis.get('target_topic', {}).get('name')
                })

            # Identify the next step (first not-yet-known node in the path)
            known_concepts = set(gap_analysis.get('known_concepts', []))
            next_step = None
            for step in learning_path:
                if step not in known_concepts:
                    next_step = step
                    break

            # Prepare context for Mistral and YouTube for the next step
            next_step_context = {
                'target_topic': {'name': next_step} if next_step else gap_analysis.get('target_topic'),
                'gaps': gap_analysis.get('gaps', []),
                'learning_path': learning_path,
                'known_concepts': list(known_concepts),
                'is_small_talk': False
            }

            # Generate explanation and videos for the next step
            next_step_explanation = self.generate_mistral_response(next_step or message, next_step_context) if next_step else None
            next_step_videos = self.get_video_recommendations(next_step or message, next_step_context) if next_step else []

            # Generate concise overall response - focus on the topic and path
            target_topic = gap_analysis.get('target_topic')
            if target_topic:
                response = f"Great question about {target_topic['name']}! "
                if learning_path:
                    response += f"Here's your suggested learning path: {' → '.join(learning_path)}"
                    response += f"\n\n🎯 **Let's start with: {next_step}**" if next_step else ""
                    response += f"\n\nAfter you understand {next_step}, just say 'next topic' or 'I understand' to continue to the next step!"
                if list(known_concepts):
                    response += f"\n\nI see you already know: {', '.join(list(known_concepts)[:3])}. Great foundation!"
            else:
                response = "Let me help you with your DSA learning journey!"

            return {
                'response': response,
                'analysis': {
                    'gaps': gap_analysis.get('gaps', []),
                    'learning_path': learning_path,
                    'next_step': next_step,
                    'next_step_explanation': next_step_explanation,
                    'next_step_videos': next_step_videos,
                    'known_topics': query_analysis['truly_known_topics'],
                    'mentioned_topics': [t['name'] for t in query_analysis['mentioned_topics']],
                    'graph_based': True,
                    'learning_session_active': True,
                    'progress_tracking': True
                }
            }
        
        else:
            # Dynamic handling for topics not in our graph
            self.log_unknown_query(message, datetime.now().isoformat())
            
            # Use Mistral to generate response without graph context
            context = {
                'dynamic_query': True,
                'known_concepts': query_analysis['truly_known_topics'],
                'is_small_talk': False
            }
            response = self.generate_mistral_response(message, context)
            
            # Get video recommendations based on the query itself
            videos = self.get_video_recommendations(message, context)
            
            return {
                'response': response,
                'videos': videos,
                'analysis': {
                    'dynamic': True,
                    'logged': True,
                    'known_topics': query_analysis['truly_known_topics']
                }
            }
    
    def handle_next_topic_request(self, user_id: str, learning_session: Dict, query_analysis: Dict) -> Dict:
        """Handle user request to move to next topic in learning path."""
        current_path = learning_session.get('current_path', [])
        current_index = learning_session.get('current_step_index', 0)
        
        if not current_path:
            return {
                'response': "You don't have an active learning path. Please ask about a topic to get started!",
                'videos': [],
                'analysis': {'no_active_path': True}
            }
        
        # Mark current topic as completed and move to next
        if current_index < len(current_path):
            completed_topic = current_path[current_index]
            self.complete_current_topic(user_id)
            
            # Check if there's a next topic
            new_index = learning_session['current_step_index']
            if new_index < len(current_path):
                next_topic = current_path[new_index]
                
                # Generate explanation for next topic
                context = {
                    'target_topic': {'name': next_topic},
                    'learning_path': current_path,
                    'current_progress': f"{new_index + 1}/{len(current_path)}",
                    'is_small_talk': False
                }
                
                explanation = self.generate_mistral_response(f"Explain {next_topic} in detail", context)
                videos = self.get_video_recommendations(next_topic, context)
                
                response = f"🎉 Great! You've completed **{completed_topic}**!\n\n"
                response += f"🎯 **Next Topic: {next_topic}** (Step {new_index + 1}/{len(current_path)})\n\n"
                response += "When you're ready to continue or if you understand this topic, just say 'next topic' or 'I understand'!"
                
                return {
                    'response': response,
                    'analysis': {
                        'topic_completed': completed_topic,
                        'next_step': next_topic,
                        'next_step_explanation': explanation,
                        'next_step_videos': videos,
                        'progress': f"{new_index + 1}/{len(current_path)}",
                        'learning_path': current_path,
                        'topic_progression': True
                    }
                }
            else:
                # Path completed
                target_topic = learning_session.get('target_topic')
                self.add_topic_to_user_profile(target_topic)
                
                return {
                    'response': f"🎉 **Congratulations!** You've completed your learning path and mastered **{target_topic}**!\n\n✅ This topic has been added to your profile.\n\n🚀 What would you like to learn next?",
                    'analysis': {
                        'path_completed': True,
                        'mastered_topic': target_topic,
                        'profile_updated': True
                    }
                }
        
        return {
            'response': "There seems to be an issue with your learning progress. Let's start fresh - what would you like to learn?",
            'videos': [],
            'analysis': {'progress_error': True}
        }
    
    def handle_more_explanation_request(self, message: str, learning_session: Dict, query_analysis: Dict, chat_history: List[Dict]) -> Dict:
        """Handle user request for more explanation when they don't understand."""
        current_path = learning_session.get('current_path', [])
        current_index = learning_session.get('current_step_index', 0)
        
        if current_path and current_index < len(current_path):
            current_topic = current_path[current_index]
            
            # Check if user is asking about a specific aspect
            specific_aspects = {
                'example': ['example', 'examples', 'sample', 'demo'],
                'implementation': ['code', 'implement', 'programming', 'syntax'],
                'use_case': ['when to use', 'use case', 'application', 'practical'],
                'comparison': ['difference', 'compare', 'vs', 'versus'],
                'step_by_step': ['step', 'process', 'how', 'procedure']
            }
            
            requested_aspect = None
            for aspect, keywords in specific_aspects.items():
                if any(keyword in message.lower() for keyword in keywords):
                    requested_aspect = aspect
                    break
            
            # Generate more detailed explanation using chat history context
            context_from_history = ""
            if chat_history:
                context_from_history = f"Previous conversation context: {json.dumps(chat_history[-3:])}"
            
            if requested_aspect:
                # Provide specific type of explanation
                if requested_aspect == 'example':
                    detailed_prompt = f"Provide detailed, practical examples of {current_topic} with step-by-step walkthroughs."
                elif requested_aspect == 'implementation':
                    detailed_prompt = f"Show code implementation of {current_topic} with detailed comments and explanations."
                elif requested_aspect == 'use_case':
                    detailed_prompt = f"Explain real-world use cases and applications of {current_topic}."
                elif requested_aspect == 'comparison':
                    detailed_prompt = f"Compare {current_topic} with similar concepts, highlighting key differences."
                else:
                    detailed_prompt = f"Provide a step-by-step explanation of how {current_topic} works."
            else:
                detailed_prompt = f"""The user is learning about {current_topic} but needs more explanation. 
                User said: "{message}"
                {context_from_history}
                
                Please provide a more detailed, beginner-friendly explanation with:
                1. Simple definitions
                2. Real-world analogies
                3. Step-by-step examples
                4. Common misconceptions to avoid
                5. Practical coding examples
                
                Be encouraging and patient."""
            
            context = {
                'target_topic': {'name': current_topic},
                'needs_detailed_explanation': True,
                'user_confusion': message,
                'requested_aspect': requested_aspect,
                'is_small_talk': False
            }
            
            detailed_explanation = self.generate_mistral_response(detailed_prompt, context)
            videos = self.get_video_recommendations(f"{current_topic} tutorial beginner {requested_aspect or ''}", context)
            
            response = f"No worries! Let me explain **{current_topic}** in more detail"
            if requested_aspect:
                response += f" with focus on {requested_aspect.replace('_', ' ')}:\n\n"
            else:
                response += ":\n\n"
            
            response += "Take your time to understand this. When you're ready, let me know if you:\n"
            response += "• Want even more examples (say 'more examples')\n"
            response += "• Have specific questions (just ask!)\n"
            response += "• Feel ready to continue (say 'I understand' or 'next topic')\n"
            response += "• Want to try a different approach (say 'explain differently')"
            
            return {
                'response': response,
                'analysis': {
                    'detailed_explanation_provided': True,
                    'current_topic': current_topic,
                    'requested_aspect': requested_aspect,
                    'next_step': current_topic,
                    'next_step_explanation': detailed_explanation,
                    'next_step_videos': videos,
                    'learning_support': True,
                    'learning_session_active': True
                }
            }
        
        return {
            'response': "I'd be happy to explain more! What specific topic would you like me to clarify?",
            'videos': [],
            'analysis': {'general_help_request': True}
        }
    
    def handle_no_response(self, user_id: str, learning_session: Dict, query_analysis: Dict, chat_history: List[Dict]) -> Dict:
        """Handle when user says 'no' - ask what they want to know and explain it."""
        current_path = learning_session.get('current_path', [])
        current_index = learning_session.get('current_step_index', 0)
        
        if current_path and current_index < len(current_path):
            current_topic = current_path[current_index]
            
            response = f"No problem! I'm here to help you understand **{current_topic}**.\n\n"
            response += "What specifically would you like to know about this topic? You can ask:\n"
            response += "• 'What is it?' - Basic definition\n"
            response += "• 'Show me examples' - Practical examples\n"
            response += "• 'How does it work?' - Step-by-step explanation\n"
            response += "• 'When do I use it?' - Real-world applications\n"
            response += "• 'Show me code' - Implementation examples\n\n"
            response += "Or ask any specific question you have about this topic!"
            
            return {
                'response': response,
                'analysis': {
                    'awaiting_specific_question': True,
                    'current_topic': current_topic,
                    'user_needs_guidance': True
                }
            }
        
        return {
            'response': "That's okay! What would you like to learn about? Just ask me any question about data structures or algorithms.",
            'videos': [],
            'analysis': {'general_no_response': True}
        }
    
    def handle_topic_completion(self, user_id: str, learning_session: Dict, query_analysis: Dict) -> Dict:
        """Handle user confirmation that they want to complete/add current topic."""
        current_path = learning_session.get('current_path', [])
        current_index = learning_session.get('current_step_index', 0)
        
        if current_path and current_index < len(current_path):
            current_topic = current_path[current_index]
            
            # Check if this is a satisfaction confirmation
            if query_analysis['learning_intent']['satisfied_with_topic']:
                # Add topic to user profile
                profile_updated = self.add_topic_to_user_profile(current_topic, user_id)
                
                # Mark topic as completed and move to next
                self.complete_current_topic(user_id)
                
                # Check if there's a next topic
                new_session = self.get_or_create_learning_session(user_id)
                new_index = new_session['current_step_index']
                
                if new_index < len(current_path):
                    next_topic = current_path[new_index]
                    
                    response = f"🎉 Excellent! **{current_topic}** has been added to your profile!\n\n"
                    response += f"🎯 **Next Topic: {next_topic}** (Step {new_index + 1}/{len(current_path)})\n\n"
                    response += "Ready to continue with the next topic? Let me know when you want to proceed!"
                    
                    # Generate explanation for next topic
                    context = {
                        'target_topic': {'name': next_topic},
                        'learning_path': current_path,
                        'current_progress': f"{new_index + 1}/{len(current_path)}",
                        'is_small_talk': False
                    }
                    
                    explanation = self.generate_mistral_response(f"Explain {next_topic} in detail", context)
                    videos = self.get_video_recommendations(next_topic, context)
                    
                    return {
                        'response': response,
                        'analysis': {
                            'topic_added_to_profile': current_topic,
                            'profile_updated': profile_updated,
                            'next_step': next_topic,
                            'next_step_explanation': explanation,
                            'next_step_videos': videos,
                            'progress': f"{new_index + 1}/{len(current_path)}",
                            'learning_path': current_path,
                            'learning_session_active': True
                        }
                    }
                else:
                    # Path completed
                    target_topic = learning_session.get('target_topic')
                    
                    return {
                        'response': f"🎉 **Congratulations!** You've completed your entire learning path and mastered **{target_topic}**!\n\n✅ **{current_topic}** has been added to your profile.\n\n🚀 What would you like to learn next?",
                        'analysis': {
                            'path_completed': True,
                            'mastered_topic': target_topic,
                            'profile_updated': profile_updated,
                            'final_topic_added': current_topic
                        }
                    }
            else:
                # Ask for confirmation before adding to profile
                response = f"Great to hear you understand **{current_topic}**! 🎉\n\n"
                response += f"Are you satisfied with your understanding of **{current_topic}** and ready to add it to your profile?\n\n"
                response += "Reply with:\n"
                response += "• **'Yes'** or **'I am satisfied'** - Add to profile and continue\n"
                response += "• **'No'** - Get more practice/examples\n"
                response += "• **'Next topic'** - Continue without adding to profile"
                
                return {
                    'response': response,
                    'analysis': {
                        'awaiting_confirmation': True,
                        'current_topic': current_topic,
                        'confirmation_requested': True
                    }
                }
        
        return {
            'response': "What topic would you like to work on completing?",
            'videos': [],
            'analysis': {'no_active_topic': True}
        }
    
    def get_or_create_learning_session(self, user_id: str) -> Dict:
        """Get or create learning session for user with MongoDB integration."""
        try:
            if not self.learning_session_model:
                # Fallback to local storage if MongoDB not available
                return self.get_learning_session(user_id)
            
            # Try to get active session from MongoDB
            session = self.learning_session_model.get_active_session(user_id)
            
            if not session:
                # Create new session
                session_data = {
                    'current_path': [],
                    'current_step_index': 0,
                    'target_topic': None,
                    'completed_topics': [],
                    'session_start': datetime.now().isoformat(),
                    'last_updated': datetime.now().isoformat()
                }
                
                session_id = self.learning_session_model.create_learning_session(user_id, session_data)
                if session_id:
                    session = self.learning_session_model.get_active_session(user_id)
                else:
                    # Fallback to local storage
                    return self.get_learning_session(user_id)
            
            return session
            
        except Exception as e:
            print(f"Error in get_or_create_learning_session: {e}")
            # Fallback to local storage
            return self.get_learning_session(user_id)
        
# Example usage and testing
if __name__ == "__main__":
    handler = IntegratedChatHandler()
    
    # Test query
    test_query = "I want to learn about binary trees"
    result = handler.handle_chat_message(test_query)
    
    print("Response:", result['response'])
    print("Videos:", len(result['videos']))
    if result.get('analysis'):
        print("Analysis:", result['analysis'])
