import math
import uuid
from typing import Optional, List, Dict
from app.models import Question, UserSession
from app.database import db

class AdaptiveEngine:
    def __init__(self):
        self.questions_collection = None
        self.sessions_collection = None

    def _ensure_connected(self):
        """Ensure database collections are available"""
        if self.questions_collection is None or self.sessions_collection is None:
            self.questions_collection = db.get_collection("questions")
            self.sessions_collection = db.get_collection("user_sessions")
            
            # If using in-memory and no questions exist, seed them
            if db.use_in_memory:
                count = self.questions_collection.count_documents()
                print(f"🔍 Question count in memory: {count}")
                if count == 0:
                    self._seed_questions_in_memory()

    def _seed_questions_in_memory(self):
        """Seed questions in memory when database is empty"""
        questions = [
            # Difficulty 0.1 (2 questions)
            {"question": "What is 15 + 23?", "options": ["38", "36", "40", "42"], "correct_answer": "38", "difficulty": 0.1, "topic": "Arithmetic", "tags": ["basic_addition", "mental_math"]},
            {"question": "If x = 3, what is 2x + 1?", "options": ["6", "7", "8", "9"], "correct_answer": "7", "difficulty": 0.1, "topic": "Algebra", "tags": ["substitution", "basic_algebra"]},
            
            # Difficulty 0.2 (2 questions)
            {"question": "What is 20% of 150?", "options": ["25", "30", "35", "40"], "correct_answer": "30", "difficulty": 0.2, "topic": "Arithmetic", "tags": ["percentages", "calculation"]},
            {"question": "Solve for x: 3x - 7 = 2", "options": ["2", "3", "4", "5"], "correct_answer": "3", "difficulty": 0.2, "topic": "Algebra", "tags": ["linear_equations", "solving"]},
            
            # Difficulty 0.3 (2 questions)
            {"question": "What is the area of a rectangle with length 8 and width 5?", "options": ["13", "40", "26", "30"], "correct_answer": "40", "difficulty": 0.3, "topic": "Geometry", "tags": ["area", "rectangle"]},
            {"question": "Which word is most similar to 'ephemeral'?", "options": ["permanent", "temporary", "strong", "weak"], "correct_answer": "temporary", "difficulty": 0.3, "topic": "Vocabulary", "tags": ["synonyms", "word_meaning"]},
            
            # Difficulty 0.4 (2 questions)
            {"question": "If a triangle has sides 3, 4, and 5, what is its area?", "options": ["6", "12", "15", "20"], "correct_answer": "6", "difficulty": 0.4, "topic": "Geometry", "tags": ["right_triangle", "area_calculation"]},
            {"question": "Simplify: (x²)³", "options": ["x⁵", "x⁶", "x⁸", "x⁹"], "correct_answer": "x⁶", "difficulty": 0.4, "topic": "Algebra", "tags": ["exponents", "simplification"]},
            
            # Difficulty 0.5 (2 questions)
            {"question": "What is the average of 12, 18, and 24?", "options": ["16", "18", "20", "22"], "correct_answer": "18", "difficulty": 0.5, "topic": "Arithmetic", "tags": ["average", "statistics"]},
            {"question": "Which word is most similar to 'ubiquitous'?", "options": ["rare", "omnipresent", "hidden", "unique"], "correct_answer": "omnipresent", "difficulty": 0.5, "topic": "Vocabulary", "tags": ["synonyms", "advanced_vocabulary"]},
            
            # Difficulty 0.6 (2 questions)
            {"question": "If f(x) = 2x² + 3x - 5, what is f(2)?", "options": ["9", "11", "13", "15"], "correct_answer": "9", "difficulty": 0.6, "topic": "Algebra", "tags": ["functions", "evaluation"]},
            {"question": "What is the circumference of a circle with radius 7?", "options": ["14π", "21π", "28π", "35π"], "correct_answer": "14π", "difficulty": 0.6, "topic": "Geometry", "tags": ["circumference", "circle"]},
            
            # Difficulty 0.7 (2 questions)
            {"question": "Solve: 2^(x+1) = 32", "options": ["3", "4", "5", "6"], "correct_answer": "4", "difficulty": 0.7, "topic": "Algebra", "tags": ["exponential_equations", "logarithms"]},
            {"question": "Which word is most similar to 'magnanimous'?", "options": ["selfish", "generous", "angry", "confused"], "correct_answer": "generous", "difficulty": 0.7, "topic": "Vocabulary", "tags": ["character_traits", "advanced_vocabulary"]},
            
            # Difficulty 0.8 (2 questions)
            {"question": "What is the sum of the interior angles of a hexagon?", "options": ["360°", "540°", "720°", "900°"], "correct_answer": "720°", "difficulty": 0.8, "topic": "Geometry", "tags": ["polygons", "angle_calculation"]},
            {"question": "If log₂(x) = 6, what is x?", "options": ["32", "64", "128", "256"], "correct_answer": "64", "difficulty": 0.8, "topic": "Algebra", "tags": ["logarithms", "exponential"]},
            
            # Difficulty 0.9 (2 questions)
            {"question": "What is the probability of drawing a red card from a standard deck?", "options": ["1/4", "1/3", "1/2", "2/3"], "correct_answer": "1/2", "difficulty": 0.9, "topic": "Arithmetic", "tags": ["probability", "cards"]},
            {"question": "Which word is most similar to 'precarious'?", "options": ["stable", "dangerous", "safe", "certain"], "correct_answer": "dangerous", "difficulty": 0.9, "topic": "Vocabulary", "tags": ["risk", "advanced_vocabulary"]},
            
            # Difficulty 1.0 (2 questions)
            {"question": "What is the derivative of f(x) = x³ + 2x² - 5x + 3?", "options": ["3x² + 4x - 5", "3x² + 2x - 5", "3x² + 4x + 5", "3x² - 4x - 5"], "correct_answer": "3x² + 4x - 5", "difficulty": 1.0, "topic": "Algebra", "tags": ["calculus", "derivatives"]},
            {"question": "Which word is most similar to 'perspicacious'?", "options": ["confused", "insightful", "ignorant", "slow"], "correct_answer": "insightful", "difficulty": 1.0, "topic": "Vocabulary", "tags": ["intelligence", "advanced_vocabulary"]}
        ]
        
        # Add id field to each question
        for i, q in enumerate(questions):
            q["id"] = f"question_{i+1}"
        
        self.questions_collection.insert_many(questions)
        print(f"✅ Auto-seeded {len(questions)} questions in memory")

    def create_session(self) -> str:
        """Create a new user session with initial ability score"""
        self._ensure_connected()
        session_id = str(uuid.uuid4())
        session = UserSession(
            session_id=session_id,
            ability_score=0.5,
            ability_history=[0.5]
        )
        
        self.sessions_collection.insert_one(session.dict())
        return session_id

    def calculate_probability(self, ability: float, difficulty: float) -> float:
        """
        Calculate probability of correct answer using IRT formula
        P(correct) = 1 / (1 + e^-(ability - difficulty))
        """
        return 1.0 / (1.0 + math.exp(-(ability - difficulty)))

    def update_ability(self, current_ability: float, difficulty: float, result: int) -> float:
        """
        Update ability using simplified IRT formula
        new_ability = ability + 0.3 * (result - probability)
        """
        probability = self.calculate_probability(current_ability, difficulty)
        new_ability = current_ability + 0.3 * (result - probability)
        
        # Clamp ability between 0.1 and 1.0
        return max(0.1, min(1.0, new_ability))

    def get_next_question(self, session_id: str) -> Optional[Question]:
        """Get the next adaptive question based on current ability"""
        self._ensure_connected()
        session = self.sessions_collection.find_one({"session_id": session_id})
        if not session:
            return None

        print(f"Session state: questions_answered={len(session['questions_answered'])}, total_questions={session['total_questions']}")
        
        # Check if test is complete (10 questions)
        if session["total_questions"] >= 10:
            print(f"Test complete: {session['total_questions']} questions answered")
            return None

        current_ability = session["ability_score"]
        answered_questions = set(session["questions_answered"])
        
        print(f"Current ability: {current_ability}")
        print(f"Answered questions: {answered_questions}")

        # Find unanswered questions
        unanswered_questions = list(self.questions_collection.find())
        print(f"Total questions available: {len(unanswered_questions)}")
        
        # Clean up answered questions list - ensure all IDs are strings
        answered_questions_clean = set()
        for q_id in answered_questions:
            if q_id:
                answered_questions_clean.add(str(q_id))
        
        print(f"Answered questions (cleaned): {answered_questions_clean}")
        
        # Filter out answered questions - check both id and _id fields
        unanswered_questions = [q for q in unanswered_questions 
                              if str(q.get("id", "")) not in answered_questions_clean 
                              and str(q.get("_id", "")) not in answered_questions_clean]
        print(f"Unanswered questions (filtered): {len(unanswered_questions)}")
        
        # Debug: Show first few unanswered question IDs for clarity
        if unanswered_questions:
            sample_ids = [str(q.get("id", q.get("_id", ""))) for q in unanswered_questions[:3]]
            print(f"Sample unanswered question IDs: {sample_ids}")
        
        if not unanswered_questions:
            print("No unanswered questions available")
            return None

        # Select question with difficulty closest to current ability
        try:
            best_question = min(unanswered_questions, 
                              key=lambda q: abs(q["difficulty"] - current_ability))
            
            print(f"Selected question difficulty: {best_question['difficulty']}")
            print(f"Selected question ID: {best_question.get('id', best_question.get('_id', 'unknown'))}")

            # Convert ObjectId to string for compatibility
            if "_id" in best_question:
                best_question["_id"] = str(best_question["_id"])
            # Map _id to id for model if id doesn't exist
            if "id" not in best_question:
                best_question["id"] = best_question["_id"]
            
            return Question(**best_question)
        except Exception as e:
            print(f"Error selecting question: {e}")
            print(f"Available questions: {len(unanswered_questions)}")
            return None

    def submit_answer(self, session_id: str, question_id: str, answer: str) -> Dict:
        """Process answer submission and update ability"""
        self._ensure_connected()
        session = self.sessions_collection.find_one({"session_id": session_id})
        if not session:
            raise ValueError("Session not found")

        # Try finding by id field first (for in-memory storage)
        question = self.questions_collection.find_one({"id": question_id})
        if not question:
            # Try finding by _id field (for MongoDB)
            try:
                question = self.questions_collection.find_one({"_id": ObjectId(question_id)})
            except:
                pass
            if not question:
                raise ValueError("Question not found")

        # Check if question already answered
        print(f"Submitting answer for question_id: {question_id}")
        print(f"Current answered questions: {session['questions_answered']}")
        print(f"Question already answered check: {question_id in session['questions_answered']}")
        
        if question_id in session["questions_answered"]:
            raise ValueError("Question already answered")

        # Evaluate answer
        is_correct = answer == question["correct_answer"]
        result = 1 if is_correct else 0

        # Update ability
        new_ability = self.update_ability(
            session["ability_score"], 
            question["difficulty"], 
            result
        )

        # Update session
        update_data = {
            "$push": {
                "questions_answered": question_id,
                "ability_history": new_ability
            },
            "$set": {
                "ability_score": new_ability,
                "total_questions": session["total_questions"] + 1,
                "correct_answers": session["correct_answers"] + result
            }
        }

        # Update weak topics if incorrect
        if not is_correct:
            topic = question["topic"]
            weak_topics = session.get("weak_topics", {})
            weak_topics[topic] = weak_topics.get(topic, 0) + 1
            update_data["$set"]["weak_topics"] = weak_topics

        self.sessions_collection.update_one(
            {"session_id": session_id},
            update_data
        )

        return {
            "correct": is_correct,
            "updated_ability": new_ability,
            "question_number": session["total_questions"] + 1,
            "difficulty": question["difficulty"],
            "topic": question["topic"]
        }

    def get_session(self, session_id: str) -> Optional[UserSession]:
        """Get session data"""
        self._ensure_connected()
        session_data = self.sessions_collection.find_one({"session_id": session_id})
        if session_data:
            # Convert ObjectId to string if present
            if "_id" in session_data:
                session_data["_id"] = str(session_data["_id"])
            return UserSession(**session_data)
        return None

    def is_test_complete(self, session_id: str) -> bool:
        """Check if test is complete (10 questions)"""
        self._ensure_connected()
        session = self.sessions_collection.find_one({"session_id": session_id})
        return session and session["total_questions"] >= 10

from bson import ObjectId
