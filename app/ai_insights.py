import openai
import os
from dotenv import load_dotenv
from typing import Dict, Any
from app.models import UserSession

load_dotenv()

class AIInsights:
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.client = None
        if self.api_key and self.api_key.startswith("sk-"):
            try:
                # Method 1: Try with api_key parameter
                self.client = openai.OpenAI(api_key=self.api_key)
                print("OpenAI client initialized successfully")
            except Exception as e1:
                try:
                    # Method 2: Try without any parameters (uses environment variable)
                    self.client = openai.OpenAI()
                    print("OpenAI client initialized successfully (fallback)")
                except Exception as e2:
                    try:
                        # Method 3: Try with minimal configuration
                        import openai as openai_module
                        openai_module.api_key = self.api_key
                        self.client = openai_module.OpenAI()
                        print("OpenAI client initialized successfully (method 3)")
                    except Exception as e3:
                        print(f"  All OpenAI initialization methods failed:")
                        print(f"   Method 1: {e1}")
                        print(f"   Method 2: {e2}")
                        print(f"   Method 3: {e3}")
                        print("Using mock insights")
                        self.client = None
        else:
            print("Invalid or missing OpenAI API key - using mock insights")

    def generate_diagnostic_report(self, session: UserSession) -> str:
        """Generate AI-powered diagnostic learning report"""
        
        # If no OpenAI client, return mock insights
        if not self.client:
            return self._generate_mock_insights(session)
        
        # Calculate performance metrics
        accuracy = (session.correct_answers / session.total_questions * 100) if session.total_questions > 0 else 0
        final_ability = session.ability_score
        max_difficulty_reached = max(session.ability_history) if session.ability_history else 0.5
        ability_progression = session.ability_history[-1] - session.ability_history[0] if len(session.ability_history) > 1 else 0
        
        # Identify weakest topics
        weak_topics_sorted = sorted(session.weak_topics.items(), key=lambda x: x[1], reverse=True)
        weakest_topic = weak_topics_sorted[0][0] if weak_topics_sorted else "None"
        
        prompt = f"""
        Generate a comprehensive diagnostic learning report for a GRE-style adaptive test.

        PERFORMANCE DATA:
        - Final Ability Score: {final_ability:.3f} (scale: 0.1-1.0)
        - Accuracy: {accuracy:.1f}% ({session.correct_answers}/{session.total_questions})
        - Highest Difficulty Reached: {max_difficulty_reached:.3f}
        - Ability Progression: {ability_progression:+.3f}
        - Weak Areas: {dict(session.weak_topics)}
        - Weakest Topic: {weakest_topic}
        - Questions Answered: {session.total_questions}
        - Ability History: {[round(ability, 3) for ability in session.ability_history]}

        Generate a structured diagnostic report with the following EXACT sections:

        1. **Diagnostic Summary**
        Brief overview of performance and overall assessment.

        2. **Performance Analytics**
        Detailed breakdown of accuracy, ability progression, and difficulty handling.

        3. **Weakness Analysis**
        Specific areas needing improvement with focus on weakest topics.

        4. **3-Step Study Plan**
        EXACTLY 3 concrete, actionable steps to improve performance.

        5. **Motivation and Learning Advice**
        Encouraging advice and learning strategies.

        Format the response in clean markdown with proper headers and bullet points.
        Be encouraging but realistic about areas needing improvement.
        """

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are an expert educational diagnostician specializing in adaptive testing and learning analytics."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1000,
                temperature=0.7
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            error_msg = str(e)
            print(f"OpenAI API error: {e}")
            
            # Check if it's a quota error and provide specific guidance
            if "quota" in error_msg.lower() or "429" in error_msg:
                print("OpenAI API quota exceeded. Using enhanced mock insights.")
                return self._generate_enhanced_mock_insights(session)
            elif "rate" in error_msg.lower() or "429" in error_msg:
                print("OpenAI API rate limited. Using enhanced mock insights.")
                return self._generate_enhanced_mock_insights(session)
            else:
                print("OpenAI API unavailable. Using enhanced mock insights.")
                return self._generate_enhanced_mock_insights(session)

    def _generate_mock_insights(self, session: UserSession) -> str:
        """Generate mock insights when OpenAI is not available"""
        accuracy = (session.correct_answers / session.total_questions * 100) if session.total_questions > 0 else 0
        final_ability = session.ability_score
        
        weakest_topic = max(session.weak_topics.items(), key=lambda x: x[1])[0] if session.weak_topics else "General"
        
        # Determine performance level
        if final_ability < 0.4:
            performance_level = "beginner"
            next_steps = "focus on foundational concepts"
        elif final_ability < 0.7:
            performance_level = "intermediate"
            next_steps = "work on advanced problem-solving techniques"
        else:
            performance_level = "advanced"
            next_steps = "tackle complex multi-step problems"
        
        return f"""
### Diagnostic Summary

Your estimated ability score of {final_ability:.3f} suggests {performance_level} proficiency. You've completed the adaptive test with {accuracy:.1f}% accuracy, showing {next_steps}.

### Performance Analytics

- **Final Ability Score**: {final_ability:.3f} (scale: 0.1-1.0)
- **Overall Accuracy**: {accuracy:.1f}% ({session.correct_answers}/{session.total_questions} questions)
- **Questions Completed**: {session.total_questions}
- **Ability Progression**: {"Steady improvement" if session.ability_history[-1] > session.ability_history[0] else "Consistent performance"} throughout the test.

### Weakness Analysis

You struggled most with **{weakest_topic}**. The adaptive system identified this as your primary area for improvement based on your response patterns and error frequency.

### 3-Step Study Plan

1. **Foundation Building**: Spend 15-20 minutes daily reviewing fundamental {weakest_topic} concepts and formulas
2. **Targeted Practice**: Complete 5-10 practice problems in {weakest_topic} each day, focusing on understanding the reasoning behind each solution
3. **Progressive Difficulty**: Attempt questions around difficulty level {min(final_ability + 0.1, 1.0):.2f} to challenge yourself appropriately

### Motivation

You are {"making excellent progress and are close to the next proficiency tier" if final_ability > 0.5 else "building a solid foundation that will support advanced learning"}. Consistent, focused practice will push you to the next level.

*Note: This is a simulated diagnostic report. To get AI-powered personalized insights, please configure your OpenAI API key in the .env file.*
"""

    def _generate_enhanced_mock_insights(self, session: UserSession) -> str:
        """Generate enhanced mock insights when OpenAI API has quota/rate issues"""
        accuracy = (session.correct_answers / session.total_questions * 100) if session.total_questions > 0 else 0
        final_ability = session.ability_score
        
        weakest_topic = max(session.weak_topics.items(), key=lambda x: x[1])[0] if session.weak_topics else "General"
        
        # Determine performance level with more granular analysis
        if final_ability < 0.3:
            performance_level = "beginner"
            performance_desc = "You're building foundational skills"
            next_steps = "focus on core concepts and basic problem-solving techniques"
        elif final_ability < 0.5:
            performance_level = "developing"
            performance_desc = "You're making good progress toward intermediate level"
            next_steps = "strengthen weak areas through targeted practice"
        elif final_ability < 0.7:
            performance_level = "intermediate"
            performance_desc = "You have solid understanding of most concepts"
            next_steps = "work on advanced problem-solving strategies"
        elif final_ability < 0.85:
            performance_level = "advanced"
            performance_desc = "You demonstrate strong analytical skills"
            next_steps = "tackle complex multi-step reasoning problems"
        else:
            performance_level = "expert"
            performance_desc = "You show mastery of complex concepts"
            next_steps = "focus on speed and accuracy optimization"
        
        # Analyze ability progression
        if len(session.ability_history) > 1:
            progression = session.ability_history[-1] - session.ability_history[0]
            progression_desc = f"{'improved by' if progression > 0 else 'maintained'} {abs(progression):.3f} points"
        else:
            progression_desc = "established baseline performance"
        
        return f"""
### Diagnostic Summary

Your estimated ability score of **{final_ability:.3f}** indicates **{performance_level}** proficiency. {performance_desc}. You've completed the adaptive test with **{accuracy:.1f}% accuracy** ({session.correct_answers}/{session.total_questions} questions) and **{progression_desc}** throughout the assessment.

### Performance Analytics

- **Final Ability Score**: {final_ability:.3f} (scale: 0.1-1.0)
- **Overall Accuracy**: {accuracy:.1f}% ({session.correct_answers}/{session.total_questions} questions)
- **Questions Completed**: {session.total_questions}
- **Ability Progression**: {progression_desc}
- **Performance Classification**: {performance_level.title()} Level

### Weakness Analysis

You showed the most difficulty with **{weakest_topic}**. The adaptive algorithm identified this as your primary growth area based on response patterns and error frequency. Focused improvement here will yield the greatest score gains.

### 3-Step Study Plan

1. **Foundation Building**: Spend 15-20 minutes daily reviewing fundamental {weakest_topic} concepts and formulas
2. **Targeted Practice**: Complete 5-10 practice problems in {weakest_topic} each day, focusing on understanding the reasoning behind each solution
3. **Progressive Difficulty**: Attempt questions around difficulty level {min(final_ability + 0.1, 1.0):.2f} to challenge yourself appropriately

### Motivation

You are **{"demonstrating excellent progress and are approaching the next proficiency tier" if final_ability > 0.7 else "building a solid foundation that will support advanced learning"}. Your consistent effort and targeted practice will unlock your full potential. Keep up the great work!

---
*Note: OpenAI API is currently experiencing rate limits. This enhanced diagnostic report provides detailed analysis based on your actual test performance. Check your OpenAI plan and billing to restore AI-powered insights.*
"""
