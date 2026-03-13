from pymongo import MongoClient
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import db
import os
from dotenv import load_dotenv

load_dotenv()

# 20 GRE-style questions with specified difficulty distribution
questions = [
    # Difficulty 0.1 (2 questions)
    {
        "question": "What is 15 + 23?",
        "options": ["38", "36", "40", "42"],
        "correct_answer": "38",
        "difficulty": 0.1,
        "topic": "Arithmetic",
        "tags": ["basic_addition", "mental_math"]
    },
    {
        "question": "If x = 3, what is 2x + 1?",
        "options": ["6", "7", "8", "9"],
        "correct_answer": "7",
        "difficulty": 0.1,
        "topic": "Algebra",
        "tags": ["substitution", "basic_algebra"]
    },
    
    # Difficulty 0.2 (2 questions)
    {
        "question": "What is 20% of 150?",
        "options": ["25", "30", "35", "40"],
        "correct_answer": "30",
        "difficulty": 0.2,
        "topic": "Arithmetic",
        "tags": ["percentages", "calculation"]
    },
    {
        "question": "Solve for x: 3x - 7 = 2",
        "options": ["2", "3", "4", "5"],
        "correct_answer": "3",
        "difficulty": 0.2,
        "topic": "Algebra",
        "tags": ["linear_equations", "solving"]
    },
    
    # Difficulty 0.3 (2 questions)
    {
        "question": "What is the area of a rectangle with length 8 and width 5?",
        "options": ["13", "40", "26", "30"],
        "correct_answer": "40",
        "difficulty": 0.3,
        "topic": "Geometry",
        "tags": ["area", "rectangle"]
    },
    {
        "question": "Which word is most similar to 'ephemeral'?",
        "options": ["permanent", "temporary", "strong", "weak"],
        "correct_answer": "temporary",
        "difficulty": 0.3,
        "topic": "Vocabulary",
        "tags": ["synonyms", "word_meaning"]
    },
    
    # Difficulty 0.4 (2 questions)
    {
        "question": "If a triangle has sides 3, 4, and 5, what is its area?",
        "options": ["6", "12", "15", "20"],
        "correct_answer": "6",
        "difficulty": 0.4,
        "topic": "Geometry",
        "tags": ["right_triangle", "area_calculation"]
    },
    {
        "question": "Simplify: (x²)³",
        "options": ["x⁵", "x⁶", "x⁸", "x⁹"],
        "correct_answer": "x⁶",
        "difficulty": 0.4,
        "topic": "Algebra",
        "tags": ["exponents", "simplification"]
    },
    
    # Difficulty 0.5 (2 questions)
    {
        "question": "What is the average of 12, 18, and 24?",
        "options": ["16", "18", "20", "22"],
        "correct_answer": "18",
        "difficulty": 0.5,
        "topic": "Arithmetic",
        "tags": ["average", "statistics"]
    },
    {
        "question": "Which word is most similar to 'ubiquitous'?",
        "options": ["rare", "omnipresent", "hidden", "unique"],
        "correct_answer": "omnipresent",
        "difficulty": 0.5,
        "topic": "Vocabulary",
        "tags": ["synonyms", "advanced_vocabulary"]
    },
    
    # Difficulty 0.6 (2 questions)
    {
        "question": "If f(x) = 2x² + 3x - 5, what is f(2)?",
        "options": ["9", "11", "13", "15"],
        "correct_answer": "9",
        "difficulty": 0.6,
        "topic": "Algebra",
        "tags": ["functions", "evaluation"]
    },
    {
        "question": "What is the circumference of a circle with radius 7?",
        "options": ["14π", "21π", "28π", "35π"],
        "correct_answer": "14π",
        "difficulty": 0.6,
        "topic": "Geometry",
        "tags": ["circumference", "circle"]
    },
    
    # Difficulty 0.7 (2 questions)
    {
        "question": "Solve: 2^(x+1) = 32",
        "options": ["3", "4", "5", "6"],
        "correct_answer": "4",
        "difficulty": 0.7,
        "topic": "Algebra",
        "tags": ["exponential_equations", "logarithms"]
    },
    {
        "question": "Which word is most similar to 'magnanimous'?",
        "options": ["selfish", "generous", "angry", "confused"],
        "correct_answer": "generous",
        "difficulty": 0.7,
        "topic": "Vocabulary",
        "tags": ["character_traits", "advanced_vocabulary"]
    },
    
    # Difficulty 0.8 (2 questions)
    {
        "question": "What is the sum of the interior angles of a hexagon?",
        "options": ["360°", "540°", "720°", "900°"],
        "correct_answer": "720°",
        "difficulty": 0.8,
        "topic": "Geometry",
        "tags": ["polygons", "angle_calculation"]
    },
    {
        "question": "If log₂(x) = 6, what is x?",
        "options": ["32", "64", "128", "256"],
        "correct_answer": "64",
        "difficulty": 0.8,
        "topic": "Algebra",
        "tags": ["logarithms", "exponential"]
    },
    
    # Difficulty 0.9 (2 questions)
    {
        "question": "What is the probability of drawing a red card from a standard deck?",
        "options": ["1/4", "1/3", "1/2", "2/3"],
        "correct_answer": "1/2",
        "difficulty": 0.9,
        "topic": "Arithmetic",
        "tags": ["probability", "cards"]
    },
    {
        "question": "Which word is most similar to 'precarious'?",
        "options": ["stable", "dangerous", "safe", "certain"],
        "correct_answer": "dangerous",
        "difficulty": 0.9,
        "topic": "Vocabulary",
        "tags": ["risk", "advanced_vocabulary"]
    },
    
    # Difficulty 1.0 (2 questions)
    {
        "question": "What is the derivative of f(x) = x³ + 2x² - 5x + 3?",
        "options": ["3x² + 4x - 5", "3x² + 2x - 5", "3x² + 4x + 5", "3x² - 4x - 5"],
        "correct_answer": "3x² + 4x - 5",
        "difficulty": 1.0,
        "topic": "Algebra",
        "tags": ["calculus", "derivatives"]
    },
    {
        "question": "Which word is most similar to 'perspicacious'?",
        "options": ["confused", "insightful", "ignorant", "slow"],
        "correct_answer": "insightful",
        "difficulty": 1.0,
        "topic": "Vocabulary",
        "tags": ["intelligence", "advanced_vocabulary"]
    }
]

def seed_database():
    """Seed the database with questions"""
    try:
        questions_collection = db.get_collection("questions")
        
        # Clear existing questions
        questions_collection.delete_many({})
        
        # Insert new questions
        result = questions_collection.insert_many(questions)
        
        print("Questions seeded successfully!")
        print(f"Successfully seeded {len(result.inserted_ids)} questions")
        print(f"Difficulty distribution:")
        
        # Count questions by difficulty
        for difficulty in [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]:
            count = questions_collection.count_documents({"difficulty": difficulty})
            print(f"   Difficulty {difficulty}: {count} questions")
            
    except Exception as e:
        print(f"Error seeding database: {e}")

if __name__ == "__main__":
    # Connect to database first
    db.connect()
    seed_database()
