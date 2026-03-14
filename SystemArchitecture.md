# System Architecture and Data Schema Documentation

## 1. System Architecture Components

### Frontend Component
- **Role**: User interface for the adaptive diagnostic test
- **Technology**: HTML5, CSS3, JavaScript (Vanilla JS)
- **Files**: frontend/index.html, frontend/quiz.js, frontend/style.css
- **Communicates with**: Backend API endpoints via HTTP requests
- **Key Features**: Question display, answer submission, progress tracking, results visualization

### Backend API Server
- **Role**: RESTful API server handling all business logic
- **Technology**: FastAPI (Python), Uvicorn server
- **Files**: app/routes.py, app/main.py
- **Communicates with**: Frontend, Adaptive Engine, Database, AI Insights
- **Port**: 8000 (default)

### Adaptive Engine
- **Role**: Core algorithm engine implementing Item Response Theory (IRT)
- **Technology**: Python class with mathematical calculations
- **File**: app/adaptive_engine.py
- **Communicates with**: Database (questions/sessions), Backend API
- **Key Functions**: 
  - calculate_probability() - IRT probability calculation
  - update_ability() - Ability score updates
  - get_next_question() - Question selection algorithm

### AI Insights Module
- **Role**: Generates personalized diagnostic reports using AI
- **Technology**: OpenAI GPT-4o-mini API with fallback to mock insights
- **File**: app/ai_insights.py
- **Communicates with**: Backend API, OpenAI API
- **Trigger**: Called when test is complete (10 questions answered)

### Database Layer
- **Role**: Data persistence with MongoDB and in-memory fallback
- **Technology**: MongoDB with InMemoryCollection fallback
- **File**: app/database.py
- **Communicates with**: All backend components
- **Collections**: questions, user_sessions

### API Endpoints
```
POST /start-session           → Creates new session
GET  /next-question/{id}      → Gets adaptive question
POST /submit-answer           → Processes answer, updates ability
GET  /generate-insights/{id}  → Generates AI diagnostic report
GET  /session/{id}            → Gets session status
GET  /health                  → Health check
```

### IRT Algorithm Location
- **Runs in**: AdaptiveEngine class (app/adaptive_engine.py)
- **Formula**: P(correct) = 1 / (1 + e^-(ability - difficulty))
- **Update Rule**: new_ability = ability + 0.3 * (result - probability)
- **Range**: Ability scores clamped between 0.1 and 1.0

## 2. Data Schema / ER Diagram Info

### MongoDB Collections

#### questions Collection
```json
{
  "_id": "ObjectId (PK)",
  "id": "question_1 (String, FK reference)",
  "question": "What is 15 + 23? (String)",
  "options": ["38", "36", "40", "42"] (Array[String]),
  "correct_answer": "38" (String),
  "difficulty": 0.1 (Float, 0.1-1.0),
  "topic": "Arithmetic" (String),
  "tags": ["basic_addition", "mental_math"] (Array[String])
}
```

#### user_sessions Collection
```json
{
  "_id": "ObjectId (PK)",
  "session_id": "uuid-string (String, Unique)",
  "ability_score": 0.5 (Float, 0.1-1.0),
  "questions_answered": ["question_1", "question_2"] (Array[String], FK references),
  "correct_answers": 5 (Integer),
  "total_questions": 10 (Integer),
  "weak_topics": {"Arithmetic": 2, "Algebra": 1} (Dict[String, Integer]),
  "ability_history": [0.5, 0.6, 0.55, 0.7] (Array[Float])
}
```

### Pydantic Models (Data Validation)

#### Question Model
- id: Optional[str] - Primary identifier
- question: str - Question text
- options: List[str] - Multiple choice options
- correct_answer: str - Right answer
- difficulty: float (0.1-1.0) - IRT difficulty parameter
- topic: str - Subject area
- tags: List[str] - Searchable tags

#### UserSession Model
- session_id: str (PK) - Unique session identifier
- ability_score: float (0.1-1.0) - Current IRT ability estimate
- questions_answered: List[str] - Array of answered question IDs
- correct_answers: int - Count of correct responses
- total_questions: int - Total questions attempted
- weak_topics: Dict[str, int] - Topic error frequencies
- ability_history: List[float] - Ability progression over time

### Relationships
- UserSession → Questions: One-to-many via questions_answered array
- Questions → UserSession: Many-to-many (questions used across sessions)
- Primary Keys: _id (MongoDB), session_id (UserSession business key)
- Foreign Keys: questions_answered contains question IDs

## 3. Data Flow / Interaction

### Complete Test Flow
```
1. Student clicks "Start Test"
   ↓
2. Frontend → POST /start-session
   ↓
3. Backend creates UserSession (ability=0.5)
   ↓
4. Frontend → GET /next-question/{session_id}
   ↓
5. AdaptiveEngine selects question (IRT matching)
   ↓
6. Frontend displays question
   ↓
7. Student selects answer → POST /submit-answer
   ↓
8. AdaptiveEngine processes response:
   - Calculate probability: P = 1/(1+e^-(ability-difficulty))
   - Update ability: new = old + 0.3*(result-P)
   - Update weak_topics if incorrect
   - Save to UserSession
   ↓
9. Repeat steps 4-8 until 10 questions
   ↓
10. Frontend → GET /generate-insights/{session_id}
    ↓
11. AIInsights generates report (OpenAI or mock)
    ↓
12. Frontend displays results with study plan
```

### Correct Answer Flow
```
Answer Submission → is_correct = True → 
Ability Update: new_ability = current + 0.3*(1 - probability) → 
Session Update: correct_answers++, total_questions++ → 
Next Question: Higher difficulty selected → 
Continue Test
```

### Incorrect Answer Flow
```
Answer Submission → is_correct = False → 
Ability Update: new_ability = current + 0.3*(0 - probability) → 
Session Update: weak_topics[topic]++, total_questions++ → 
Next Question: Lower difficulty selected → 
Continue Test
```

### AI Module Trigger
```
Test Complete (total_questions >= 10) → 
GET /generate-insights → 
AIInsights.generate_diagnostic_report() → 
- Calculate metrics (accuracy, progression, weak areas)
- Build OpenAI prompt with performance data
- Call GPT-4o-mini API OR use enhanced mock
- Return structured markdown report
```

### Database Operations
- Read: Question selection, session retrieval
- Write: Session creation, answer submission
- Update: Ability scores, weak topics, question tracking
- Fallback: In-memory storage if MongoDB unavailable

### Key Decision Points
1. Question Selection: Minimize |difficulty - ability| for optimal challenge
2. Test Completion: 10 questions OR no more appropriate questions
3. AI Fallback: Enhanced mock insights when API quota exceeded
4. Ability Clamping: Keep scores in [0.1, 1.0] range for stability
