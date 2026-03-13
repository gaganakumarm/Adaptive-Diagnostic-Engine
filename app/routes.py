from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, Any
from app.models import Question, UserSession, AnswerSubmission, AdaptiveResponse, AnswerResult
from app.adaptive_engine import AdaptiveEngine
from app.ai_insights import AIInsights

app = FastAPI(title="Adaptive Diagnostic Engine API", version="1.0.0")

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
adaptive_engine = AdaptiveEngine()
ai_insights = AIInsights()

@app.post("/start-session", response_model=Dict[str, str])
async def start_session():
    """Create a new diagnostic session"""
    try:
        session_id = adaptive_engine.create_session()
        return {"session_id": session_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create session: {str(e)}")

@app.get("/next-question/{session_id}", response_model=Dict[str, Any])
async def get_next_question(session_id: str):
    """Get next adaptive question"""
    try:
        print(f"Getting next question for session: {session_id}")
        
        question = adaptive_engine.get_next_question(session_id)
        session = adaptive_engine.get_session(session_id)
        
        if not session:
            print(f"Session not found: {session_id}")
            raise HTTPException(status_code=404, detail="Session not found")
            
        if adaptive_engine.is_test_complete(session_id):
            print(f"Test complete for session: {session_id}")
            return {"test_complete": True, "message": "Diagnostic test completed"}
        
        if not question:
            print(f"No more questions available for session: {session_id}")
            return {"test_complete": True, "message": "No more questions available"}
        
        print(f"Returning question: {question.id if hasattr(question, 'id') else question._id}")
        return {
            "question": question.dict(),
            "question_number": session.total_questions + 1,
            "current_ability": session.ability_score
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get next question: {str(e)}")

@app.post("/submit-answer", response_model=Dict[str, Any])
async def submit_answer(submission: AnswerSubmission):
    """Submit an answer and update ability"""
    try:
        result = adaptive_engine.submit_answer(
            submission.session_id, 
            submission.question_id, 
            submission.answer
        )
        
        session = adaptive_engine.get_session(submission.session_id)
        
        return {
            "correct": result["correct"],
            "updated_ability": result["updated_ability"],
            "question_number": result["question_number"],
            "difficulty": result["difficulty"],
            "topic": result["topic"],
            "test_complete": adaptive_engine.is_test_complete(submission.session_id),
            "total_questions": session.total_questions,
            "correct_answers": session.correct_answers
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to submit answer: {str(e)}")

@app.get("/generate-insights/{session_id}", response_model=Dict[str, Any])
async def generate_insights(session_id: str):
    """Generate AI-powered diagnostic report"""
    try:
        session = adaptive_engine.get_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        if not adaptive_engine.is_test_complete(session_id):
            raise HTTPException(status_code=400, detail="Test not completed yet")
        
        report = ai_insights.generate_diagnostic_report(session)
        
        return {
            "session_id": session_id,
            "final_ability": session.ability_score,
            "accuracy": (session.correct_answers / session.total_questions * 100) if session.total_questions > 0 else 0,
            "total_questions": session.total_questions,
            "correct_answers": session.correct_answers,
            "weak_topics": session.weak_topics,
            "ability_history": session.ability_history,
            "diagnostic_report": report
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate insights: {str(e)}")

@app.get("/session/{session_id}", response_model=Dict[str, Any])
async def get_session(session_id: str):
    """Get current session status"""
    try:
        session = adaptive_engine.get_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        return {
            "session_id": session_id,
            "current_ability": session.ability_score,
            "total_questions": session.total_questions,
            "correct_answers": session.correct_answers,
            "test_complete": adaptive_engine.is_test_complete(session_id),
            "weak_topics": session.weak_topics,
            "ability_history": session.ability_history
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get session: {str(e)}")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "running"}
