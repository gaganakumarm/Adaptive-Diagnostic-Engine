# AI-Driven Adaptive Diagnostic Engine

### 1-Dimensional Adaptive Testing Prototype (IRT-Based)

A sophisticated GRE-style assessment system that dynamically adjusts question difficulty in real-time. By leveraging **Item Response Theory (IRT)** and **LLM-driven analytics**, the engine provides a mathematically grounded evaluation of student proficiency followed by a personalized pedagogical roadmap.

---

## System Overview

This prototype replaces static testing with a dynamic feedback loop. As a student interacts with the system, their latent ability ($\theta$) is recalculated after every response, ensuring the questions served are always at the "Goldilocks zone" of their current skill level.

### Key Logic Flow:

1. **Initialization**: User starts with a baseline ability score of $0.5$.
2. **The Adaptive Loop**: The engine fetches the most relevant question from MongoDB based on the current ability-to-difficulty match.
3. **IRT Update**: Upon submission, the system calculates the probability of a correct answer and shifts the user's ability score.
4. **AI Synthesis**: Post-assessment, the engine aggregates performance metadata to generate a 3-step personalized study plan via GPT-4.

---

## Tech Stack

| Component | Technology |
| --- | --- |
| **Backend** | Python 3.x, FastAPI (Asynchronous) |
| **Database** | MongoDB (NoSQL for flexible schema metadata) |
| **AI Engine** | OpenAI GPT-4 API |
| **Mathematics** | Custom IRT implementation (1-Parameter Logistic Model) |

---

## The Adaptive Algorithm

The core engine utilizes a simplified **1-Parameter Logistic (1PL) Model** to estimate student proficiency.

### 1. Probability Calculation

The probability $P$ of a student with ability $\theta$ answering a question of difficulty $\beta$ correctly is defined as:

$$P(\text{correct}) = \frac{1}{1 + e^{-(\theta - \beta)}}$$

### 2. Ability Update Rule

After each response, the ability score is updated using a step-function approach to converge on the user's true proficiency:

$$\theta_{new} = \theta_{old} + \alpha \cdot (\text{result} - P(\text{correct}))$$

* **$\alpha$ (Learning Rate):** Set to $0.3$ to balance stability and sensitivity.
* **Constraints:** Ability is clamped between $0.1$ and $1.0$ to maintain consistency with the question bank.

---

## API Documentation

| Endpoint | Method | Description |
| --- | --- | --- |
| `/start-session` | `POST` | Initializes a new `UserSession` in MongoDB. |
| `/next-question/{id}` | `GET` | Fetches the best-fit question for the current ability. |
| `/submit-answer` | `POST` | Processes answer, updates IRT score, and logs history. |
| `/generate-insights` | `GET` | Triggers LLM analysis for a 3-step study plan. |

---

## AI Integration & Development Log

### Strategic AI Usage

I utilized **AI-augmented development (Cursor/GPT-4)** to accelerate the transition from mathematical theory to functional code.

* **Boilerplate & Scaffolding**: Used LLMs to generate FastAPI Pydantic schemas and MongoDB connection boilerplate.
* **Algorithmic Refinement**: Leveraged AI to verify the edge-case behavior of the IRT update formula.
* **Data Synthesis**: Used LLM prompting to generate high-quality, tagged GRE-style questions for the initial seed.

### Challenges Overcome Manually

* **State Persistence**: Handled the logic for ensuring no duplicate questions are served within a single session.
* **API Resiliency**: Implemented a graceful fallback mechanism for the AI Insights module to handle rate-limiting or network latency without crashing the test experience.
* **Data Serialization**: Resolved specific BSON/JSON compatibility issues between MongoDB ObjectIDs and FastAPI responses.

---

## Installation & Setup

1. **Clone & Environment**:
1. **Clone and setup**:
```bash
cd "adaptive-diagnostic-engine"
pip install -r requirements.txt
```

2. **Environment Configuration**:
```bash
cp .env.example .env
# Edit .env with your API keys and MongoDB URI
```

3. **Seed Database**:
```bash
python seed/seed_questions.py
```

4. **Start Backend**:
```bash
uvicorn app.main:app --reload
```

5. **Open Application**:
Visit `http://127.0.0.1:8000` in your browser. The frontend is automatically served from the backend.

### Environment Variables
- `OPENAI_API_KEY`: Your OpenAI API key for generating insights
- `MONGO_URI`: MongoDB connection string (defaults to local instance)

## AI Log

### AI Tools Used During Development

**Primary Development Environment**: Windsurf/Cursor IDE
- Accelerated development with AI-assisted code generation
- Rapid prototyping of complex algorithms
- Intelligent error detection and fixes

**AI Tools Integration**:
- **ChatGPT**: Algorithm design consultation and documentation optimization
- **Cursor/Windsurf**: Code generation, debugging, and architectural decisions
- **Automated Testing**: AI-driven test case generation for edge scenarios

### How AI Helped

AI tools significantly accelerated development by:
1. **Algorithm Implementation**: Rapid IRT formula implementation with mathematical precision
2. **Project Scaffolding**: Generated complete project structure with proper architecture
3. **Question Generation**: Created 20 calibrated GRE-style questions across difficulty levels
4. **Error Handling**: Comprehensive edge case detection and resolution
5. **Code Quality**: Consistent coding patterns and best practices
6. **Documentation**: Professional README generation and API documentation
