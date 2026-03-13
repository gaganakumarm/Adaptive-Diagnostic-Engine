class AdaptiveQuiz {
    constructor() {
        this.sessionId = null;
        this.currentQuestion = null;
        this.questionNumber = 0;
        this.currentAbility = 0.5;
        this.abilityHistory = [];
        this.chart = null;
        this.apiBase = ''; // Use relative URLs since frontend is served from same domain
        
        this.initializeEventListeners();
    }

    initializeEventListeners() {
        document.getElementById('start-test-btn').addEventListener('click', () => this.startTest());
        document.getElementById('submit-answer-btn').addEventListener('click', () => this.submitAnswer());
        document.getElementById('next-question-btn').addEventListener('click', () => this.getNextQuestion());
        document.getElementById('restart-btn').addEventListener('click', () => this.restartTest());
    }

    async startTest() {
        try {
            this.showLoading();
            const response = await fetch('/start-session', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' }
            });
            
            if (!response.ok) throw new Error('Failed to start session');
            
            const data = await response.json();
            this.sessionId = data.session_id;
            
            this.showPage('quiz-page');
            await this.getNextQuestion();
        } catch (error) {
            this.showError('Failed to start test. Please try again.');
        }
    }

    async getNextQuestion() {
        try {
            this.showLoading();
            const response = await fetch(`/next-question/${this.sessionId}`);
            
            if (!response.ok) {
                const errorData = await response.json();
                
                // Check if test is complete
                if (errorData.test_complete) {
                    console.log('Test complete detected, showing results...');
                    this.showResults();
                    return;
                }
                
                throw new Error('Failed to get next question');
            }
            
            const data = await response.json();
            
            // Check if test is complete in successful response
            if (data.test_complete) {
                console.log('Test complete detected in successful response, showing results...');
                this.showResults();
                return;
            }
            
            this.currentQuestion = data.question;
            this.currentAbility = data.current_ability;
            this.questionNumber = data.question_number;
            
            // Update question number
            document.getElementById('question-number').textContent = data.question_number;
            
            // Reset button text and behavior
            const nextBtn = document.getElementById('next-question-btn');
            nextBtn.textContent = 'Next Question';
            nextBtn.onclick = () => this.getNextQuestion();
            
            this.displayQuestion();
            this.hideLoading();
        } catch (error) {
            console.error('Failed to load next question:', error);
            console.error('Error details:', error.message);
            console.error('Session ID:', this.sessionId);
            console.error('Current question state:', this.currentQuestion);
            
            // Check if it's a test completion issue
            if (error.message && error.message.includes('404')) {
                console.log('Attempting to show results instead...');
                this.showResults();
            } else {
                // Don't show error popup - question might still load
                console.log('Question loading issue detected, but continuing...');
            }
        }
    }

    async loadNextQuestion() {
        await this.getNextQuestion();
    }

    displayQuestion() {
        console.log('Displaying question:', this.currentQuestion);
        
        // Update UI
        document.getElementById('question-number').textContent = this.questionNumber;
        document.getElementById('current-ability').textContent = this.currentAbility.toFixed(3);
        document.getElementById('question-text').textContent = this.currentQuestion.question;
        
        console.log('Question text set to:', this.currentQuestion.question);
        console.log('Question text element:', document.getElementById('question-text').textContent);
        
        // Update progress bar
        const progress = (this.questionNumber - 1) * 10;
        document.getElementById('progress-fill').style.width = `${progress}%`;
        
        // Display options
        const optionsContainer = document.getElementById('options-container');
        optionsContainer.innerHTML = '';
        
        console.log('Current question structure:', this.currentQuestion);
        console.log('Options:', this.currentQuestion.options);
        
        // Check if options exist and are in the right format
        if (!this.currentQuestion.options || !Array.isArray(this.currentQuestion.options)) {
            console.error('Question options not found or not in array format:', this.currentQuestion);
            optionsContainer.innerHTML = '<p class="error">Error: Question options not available</p>';
            return;
        }
        
        this.currentQuestion.options.forEach((option, index) => {
            const optionElement = document.createElement('div');
            optionElement.className = 'option';
            optionElement.textContent = option;
            optionElement.dataset.answer = option;
            optionElement.addEventListener('click', () => this.selectOption(optionElement));
            optionsContainer.appendChild(optionElement);
        });
        
        console.log('Options added:', this.currentQuestion.options.length);
        
        // Reset UI
        document.getElementById('question-container').classList.remove('hidden');
        document.getElementById('feedback-container').classList.add('hidden');
        // Enable submit button for new question
        document.getElementById('submit-answer-btn').disabled = false;
    }

    selectOption(optionElement) {
        // Remove previous selection
        document.querySelectorAll('.option').forEach(opt => {
            opt.classList.remove('selected');
        });
        
        // Add selection to clicked option
        optionElement.classList.add('selected');
        document.getElementById('submit-answer-btn').disabled = false;
    }

    async submitAnswer() {
        const selectedOption = document.querySelector('.option.selected');
        if (!selectedOption) {
            console.log('No option selected, cannot submit');
            return;
        }
        
        // Prevent double submission
        const submitBtn = document.getElementById('submit-answer-btn');
        if (submitBtn.disabled) {
            console.log('Submit button already disabled, ignoring submission');
            return;
        }
        
        const answer = selectedOption.dataset.answer;
        console.log('Submitting answer:', answer);
        console.log('Current question ID:', this.currentQuestion.id);
        console.log('Session ID:', this.sessionId);
        
        try {
            // Disable button immediately to prevent double clicks
            submitBtn.disabled = true;
            this.showLoading();
            
            const response = await fetch('/submit-answer', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    session_id: this.sessionId,
                    question_id: this.currentQuestion.id,
                    answer: answer
                })
            });
            
            if (!response.ok) {
                // Re-enable button if submission failed
                submitBtn.disabled = false;
                const errorText = await response.text();
                console.error('Submit answer error:', errorText);
                throw new Error(`Failed to submit answer: ${response.status}`);
            }
            
            const result = await response.json();
            
            // Update ability history
            this.abilityHistory.push(result.updated_ability);
            this.currentAbility = result.updated_ability;
            
            // Show feedback
            this.showFeedback(result);
            
            // Hide loading state
            this.hideLoading();
            
            // Update progress
            const progress = result.question_number * 10;
            document.getElementById('progress-fill').style.width = `${progress}%`;
            
            // Check if test is complete
            if (result.test_complete) {
                // Update button to show completion
                const nextBtn = document.getElementById('next-question-btn');
                nextBtn.textContent = 'Submit / View Results';
                nextBtn.onclick = () => this.showResults();
                
                // Auto-show results immediately after feedback
                setTimeout(() => {
                    this.showResults();
                }, 2000);
            } else {
                // Ensure button is reset for normal flow
                const nextBtn = document.getElementById('next-question-btn');
                nextBtn.textContent = 'Next Question';
                nextBtn.onclick = () => this.getNextQuestion();
                
                // Load next question after delay
                setTimeout(() => this.loadNextQuestion(), 2000);
            }
        } catch (error) {
            console.error('Failed to submit answer:', error);
            console.error('Error details:', error.message);
            
            // Re-enable button if submission failed
            if (submitBtn) {
                submitBtn.disabled = false;
            }
            
            this.hideLoading();
            this.showError(`Failed to submit answer. ${error.message || 'Please try again.'}`);
        }
    }

    showFeedback(result) {
        console.log('Showing feedback for result:', result);
        
        const feedbackContainer = document.getElementById('feedback-container');
        const feedbackMessage = document.getElementById('feedback-message');
        
        if (!feedbackContainer || !feedbackMessage) {
            console.error('Feedback container elements not found');
            return;
        }
        
        // Update ability display
        document.getElementById('current-ability').textContent = result.updated_ability.toFixed(3);
        
        // Show feedback message
        feedbackMessage.className = result.correct ? 'correct' : 'incorrect';
        feedbackMessage.innerHTML = `
            <h3>${result.correct ? '✅ Correct!' : '❌ Incorrect'}</h3>
            <p>Your ability score: ${result.updated_ability.toFixed(3)}</p>
            <p>Question difficulty: ${result.difficulty.toFixed(3)}</p>
            <p>Topic: ${result.topic}</p>
        `;
        
        // Highlight correct/incorrect answers
        document.querySelectorAll('.option').forEach(opt => {
            opt.style.pointerEvents = 'none';
            if (opt.dataset.answer === this.currentQuestion.correct_answer) {
                opt.classList.add('correct');
            } else if (opt.classList.contains('selected') && !result.correct) {
                opt.classList.add('incorrect');
            }
        });
        
        // Show feedback container
        document.getElementById('question-container').classList.add('hidden');
        feedbackContainer.classList.remove('hidden');
    }

    async showResults() {
        try {
            console.log('Attempting to show results...');
            this.showLoading();
            const response = await fetch(`/generate-insights/${this.sessionId}`);
            
            if (!response.ok) {
                const errorText = await response.text();
                console.error('Failed to generate insights:', errorText);
                throw new Error(`Failed to generate insights: ${response.status}`);
            }
            
            const data = await response.json();
            console.log('Results data received:', data);
            
            // Update summary metrics
            document.getElementById('final-ability').textContent = data.final_ability.toFixed(3);
            document.getElementById('accuracy').textContent = `${data.accuracy.toFixed(1)}%`;
            document.getElementById('total-answered').textContent = `${data.correct_answers}/${data.total_questions}`;
            
            // Display AI insights with Markdown rendering
            const reportContainer = document.getElementById('diagnostic-report');
            if (typeof marked !== 'undefined') {
                // Render Markdown to HTML
                let htmlContent = marked.parse(data.diagnostic_report);
                
                // Wrap sections in cards
                htmlContent = this.wrapSectionsInCards(htmlContent);
                
                reportContainer.innerHTML = htmlContent;
            } else {
                // Fallback if marked.js not loaded
                reportContainer.textContent = data.diagnostic_report;
            }
            
            // Create ability progression chart - REMOVED
            // Chart functionality disabled as requested
            
            // Show results page
            this.showPage('results-page');
        } catch (error) {
            console.error('Failed to show results:', error);
            console.error('Error details:', error.message);
            
            // Check if it's an API quota error
            if (error.message && (error.message.includes('quota') || error.message.includes('429'))) {
                this.showApiQuotaMessage();
            } else {
                this.showError(`Failed to generate results. ${error.message || 'Please try again.'}`);
            }
        } finally {
            this.hideLoading();
        }
    }

    createAbilityChart(abilityHistory) {
        try {
            const ctx = document.getElementById('ability-chart');
            if (!ctx) {
                console.error('Chart canvas not found');
                return;
            }
            
            const chartCtx = ctx.getContext('2d');
            
            if (this.chart) {
                this.chart.destroy();
            }
            
            // Fix: Ensure abilityHistory is valid
            if (!abilityHistory || !Array.isArray(abilityHistory) || abilityHistory.length === 0) {
                console.error('Invalid ability history data');
                return;
            }
            
            // Fix: Only take first 10 data points (test is 10 questions)
            const chartData = abilityHistory.slice(0, 10);
            
            // Fix: Correct labels - Baseline + After Q1, After Q2, etc.
            const labels = ['Baseline', ...chartData.slice(1).map((_, index) => `After Q${index + 1}`)];
            
            this.chart = new Chart(chartCtx, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Ability Score',
                    data: chartData,
                    borderColor: '#667eea',
                    backgroundColor: 'rgba(102, 126, 234, 0.1)',
                    borderWidth: 3,
                    tension: 0.2,
                    fill: true,
                    pointRadius: function(context) {
                        // Make final point larger and gold
                        return context.dataIndex === chartData.length - 1 ? 8 : 5;
                    },
                    pointBackgroundColor: function(context) {
                        // Gold color for final point
                        return context.dataIndex === chartData.length - 1 ? '#FFD700' : '#667eea';
                    },
                    pointBorderColor: function(context) {
                        return context.dataIndex === chartData.length - 1 ? '#FFA500' : '#fff';
                    },
                    pointBorderWidth: function(context) {
                        return context.dataIndex === chartData.length - 1 ? 3 : 2;
                    }
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    },
                    tooltip: {
                        backgroundColor: 'rgba(0, 0, 0, 0.8)',
                        padding: 12,
                        cornerRadius: 8,
                        callbacks: {
                            label: function(context) {
                                return `Ability: ${context.parsed.y.toFixed(3)}`;
                            }
                        }
                    }
                },
                scales: {
                    y: {
                        beginAtZero: false,
                        min: 0,
                        max: 1,
                        ticks: {
                            callback: function(value) {
                                return value.toFixed(1);
                            }
                        },
                        grid: {
                            color: 'rgba(0, 0, 0, 0.05)'
                        },
                        // Add proficiency zones
                        afterBuildTicks: function(scale) {
                            const ctx = scale.ctx;
                            const chartArea = scale.chart.chartArea;
                            
                            // Clear existing annotations
                            ctx.save();
                            
                            // Advanced Zone (0.8 - 1.0) - Green
                            ctx.fillStyle = 'rgba(40, 167, 69, 0.1)';
                            ctx.fillRect(chartArea.left, scale.top, chartArea.width, scale.getPixelForValue(0.8) - scale.top);
                            
                            // Intermediate Zone (0.4 - 0.7) - Yellow
                            ctx.fillStyle = 'rgba(255, 193, 7, 0.1)';
                            ctx.fillRect(chartArea.left, scale.getPixelForValue(0.8), chartArea.width, scale.getPixelForValue(0.4) - scale.getPixelForValue(0.8));
                            
                            // Beginner Zone (0.1 - 0.3) - Red
                            ctx.fillStyle = 'rgba(220, 38, 38, 0.1)';
                            ctx.fillRect(chartArea.left, scale.getPixelForValue(0.4), chartArea.width, scale.getPixelForValue(0.1) - scale.getPixelForValue(0.4));
                            
                            ctx.restore();
                        }
                    },
                    x: {
                        grid: {
                            display: false
                        },
                        ticks: {
                            maxRotation: 45,
                            minRotation: 0
                        }
                    }
                },
                // Ensure canvas doesn't overflow
                devicePixelRatio: window.devicePixelRatio || 1
            }
        });
        } catch (error) {
            console.error('Chart creation error:', error);
        }
    }

    restartTest() {
        // Reset state
        this.sessionId = null;
        this.currentQuestion = null;
        this.questionNumber = 0;
        this.currentAbility = 0.5;
        this.abilityHistory = [];
        
        if (this.chart) {
            this.chart.destroy();
            this.chart = null;
        }
        
        // Show landing page
        this.showPage('landing-page');
    }

    showPage(pageId) {
        document.querySelectorAll('.page').forEach(page => {
            page.classList.add('hidden');
        });
        document.getElementById(pageId).classList.remove('hidden');
    }

    showLoading() {
        // Could implement a loading overlay here
        console.log('Loading...');
    }

    showError(message) {
        alert(message); // Simple error display - could be enhanced with a modal
    }

    showApiQuotaMessage() {
        // Create a user-friendly quota exceeded message
        const quotaMessage = `
            <div style="text-align: center; padding: 20px; background: #fff3cd; border-radius: 8px; margin: 20px;">
                <h3 style="color: #856404; margin-bottom: 15px;">🔒 API Quota Exceeded</h3>
                <p style="color: #495057; margin-bottom: 15px; line-height: 1.5;">
                    <strong>AI insights temporarily unavailable</strong><br>
                    You've reached the OpenAI API usage limit for this billing period.
                </p>
                <div style="background: #f8f9fa; padding: 15px; border-radius: 6px; margin-top: 15px;">
                    <h4 style="color: #667eea; margin-bottom: 10px;">✅ Enhanced Mock Insights</h4>
                    <p style="color: #495057; margin-bottom: 10px;">
                        Your detailed diagnostic report has been generated using advanced analysis of your actual test performance.
                    </p>
                    <p style="color: #6c757d; font-size: 0.9rem;">
                        💡 <strong>To restore AI-powered insights:</strong> Check your OpenAI billing or wait for the quota to reset.
                    </p>
                </div>
            </div>
        `;
        
        // Create a modal overlay
        const modal = document.createElement('div');
        modal.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.8);
            z-index: 10000;
            display: flex;
            align-items: center;
            justify-content: center;
        `;
        
        const modalContent = document.createElement('div');
        modalContent.innerHTML = quotaMessage;
        modalContent.style.cssText = `
            max-width: 500px;
            background: white;
            padding: 0;
            border-radius: 12px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
            max-height: 80vh;
            overflow-y: auto;
        `;
        
        modal.appendChild(modalContent);
        document.body.appendChild(modal);
        
        // Close modal when clicking outside
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                document.body.removeChild(modal);
            }
        });
        
        // Auto-close after 10 seconds
        setTimeout(() => {
            if (document.body.contains(modal)) {
                document.body.removeChild(modal);
            }
        }, 10000);
    }

    wrapSectionsInCards(htmlContent) {
        // Split content by h2 headings and wrap each section in a card
        const sections = htmlContent.split(/(?=<h[2-3])/);
        return sections.map(section => {
            if (section.trim() && (section.includes('<h2') || section.includes('<h3'))) {
                return `<div class="report-card">${section}</div>`;
            }
            return section;
        }).join('');
    }
}

// Initialize the quiz when the page loads
document.addEventListener('DOMContentLoaded', () => {
    new AdaptiveQuiz();
});
