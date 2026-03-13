#!/usr/bin/env python3
"""
Test script to verify the complete adaptive testing flow
"""

import requests
import json

BASE_URL = "http://127.0.0.1:8000"

def test_complete_flow():
    """Test the complete adaptive testing flow"""
    print("Testing Adaptive Diagnostic Engine Flow")
    print("=" * 50)
    
    # Test 1: Health check
    print("1. Testing health endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"   Health: {response.json()}")
    except Exception as e:
        print(f"   Health check failed: {e}")
        return
    
    # Test 2: Start session
    print("\n2. Starting new session...")
    try:
        response = requests.post(f"{BASE_URL}/start-session", json={})
        session_data = response.json()
        session_id = session_data["session_id"]
        print(f"   Session created: {session_id}")
    except Exception as e:
        print(f"   Session creation failed: {e}")
        return
    
    # Test 3: Get first question
    print("\n3. Getting first question...")
    try:
        response = requests.get(f"{BASE_URL}/next-question/{session_id}")
        question_data = response.json()
        
        if "status" in question_data:
            print(f"   No questions available: {question_data}")
            return
            
        question = question_data["question"]
        print(f"   Question {question_data['question_number']}: {question['question'][:50]}...")
        print(f"   Current ability: {question_data['current_ability']}")
        print(f"   Difficulty: {question['difficulty']}")
        
    except Exception as e:
        print(f"   Failed to get question: {e}")
        return
    
    # Test 4: Submit answer (simulate answering correctly)
    print("\n4. Submitting answer...")
    try:
        answer_data = {
            "session_id": session_id,
            "question_id": question["id"],
            "answer": question["correct_answer"]
        }
        response = requests.post(f"{BASE_URL}/submit-answer", json=answer_data)
        result = response.json()
        
        print(f"   Answer submitted: {'Correct' if result['correct'] else 'Incorrect'}")
        print(f"   Updated ability: {result['updated_ability']}")
        print(f"   Question {result['question_number']}/10")
        
    except Exception as e:
        print(f"   Failed to submit answer: {e}")
        return
    
    # Test 5: Complete a few more questions
    print("\n5. Testing adaptive flow...")
    for i in range(3):
        try:
            response = requests.get(f"{BASE_URL}/next-question/{session_id}")
            question_data = response.json()
            
            if "status" in question_data:
                print(f"   Test complete or no more questions")
                break
                
            question = question_data["question"]
            print(f"   Question {question_data['question_number']}: Difficulty {question['difficulty']}")
            
            # Submit answer (sometimes correct, sometimes wrong)
            import random
            if random.random() > 0.5:
                answer = question["correct_answer"]
            else:
                wrong_answers = [opt for opt in question["options"] if opt != question["correct_answer"]]
                answer = wrong_answers[0] if wrong_answers else question["correct_answer"]
            
            answer_data = {
                "session_id": session_id,
                "question_id": question["id"],
                "answer": answer
            }
            response = requests.post(f"{BASE_URL}/submit-answer", json=answer_data)
            result = response.json()
            
            print(f"      {'Correct' if result['correct'] else 'Incorrect'} Answer: {result['correct']}, Ability: {result['updated_ability']:.3f}")
            
        except Exception as e:
            print(f"   Error in question {i+1}: {e}")
            break
    
    # Test 6: Generate insights (if test is complete)
    print("\n6. Testing insights generation...")
    try:
        response = requests.get(f"{BASE_URL}/generate-insights/{session_id}")
        insights = response.json()
        
        if "diagnostic_report" in insights:
            print(f"   Insights generated!")
            print(f"   Final ability: {insights['final_ability']}")
            print(f"   Accuracy: {insights['accuracy']:.1f}%")
            print(f"   Report preview: {insights['diagnostic_report'][:100]}...")
        else:
            print(f"   Test not complete yet (need 10 questions)")
            
    except Exception as e:
        print(f"   Insights generation failed: {e}")
    
    print("\n" + "=" * 50)
    print("Flow test completed!")
    print("Open http://127.0.0.1:8000 in your browser to try the full UI")

if __name__ == "__main__":
    test_complete_flow()
