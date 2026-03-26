/**
 * PhysioMonitor AI Chatbot
 * Features:
 * - Context-aware responses
 * - Exercise guidance
 * - Injury prevention tips
 * - Multilingual support
 */

class PhysioChatbot {
    constructor() {
        this.messages = [];
        this.isLoading = false;
        this.lastExercise = null;
        this.sessionContext = {};
        
        this.init();
    }
    
    init() {
        this.setupEventListeners();
        this.loadChatHistory();
    }
    
    setupEventListeners() {
        const sendBtn = document.getElementById('chatSendBtn');
        const inputField = document.getElementById('chatInput');
        
        if (sendBtn) {
            sendBtn.addEventListener('click', () => this.sendMessage());
        }
        
        if (inputField) {
            inputField.addEventListener('keypress', (e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    this.sendMessage();
                }
            });
        }
    }
    
    /**
     * Send message to chatbot
     */
    async sendMessage() {
        const inputField = document.getElementById('chatInput');
        const message = inputField?.value?.trim();
        
        if (!message) return;
        
        // Add user message
        this.addMessage({
            type: 'user',
            text: message,
            timestamp: new Date()
        });
        
        inputField.value = '';
        
        // Show loading state
        this.setLoading(true);
        
        try {
            const response = await fetch(API_BASE + '/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${localStorage.getItem('authToken')}`
                },
                body: JSON.stringify({
                    user_message: message,
                    exercise: this.lastExercise,
                    context: this.sessionContext
                })
            });
            
            const data = await response.json();
            
            // Add bot response
            this.addMessage({
                type: 'bot',
                text: data.response,
                timestamp: new Date()
            });
            
        } catch (error) {
            console.error('Chatbot error:', error);
            this.addMessage({
                type: 'bot',
                text: i18n.t('error'),
                isError: true,
                timestamp: new Date()
            });
        } finally {
            this.setLoading(false);
        }
    }
    
    /**
     * Add message to chat
     */
    addMessage(message) {
        this.messages.push(message);
        this.saveChatHistory();
        this.renderMessages();
        this.scrollToBottom();
    }
    
    /**
     * Render all messages
     */
    renderMessages() {
        const chatBox = document.getElementById('chatMessages');
        if (!chatBox) return;
        
        chatBox.innerHTML = this.messages.map(msg => `
            <div class="chat-message ${msg.type} ${msg.isError ? 'error' : ''}">
                <div class="message-avatar">
                    ${msg.type === 'user' ? 
                        '<i class="fas fa-user"></i>' : 
                        '<i class="fas fa-robot"></i>'}
                </div>
                <div class="message-content">
                    <p>${this.escapeHtml(msg.text)}</p>
                    <span class="message-time">${this.formatTime(msg.timestamp)}</span>
                </div>
            </div>
        `).join('');
    }
    
    /**
     * Scroll to bottom of chat
     */
    scrollToBottom() {
        const chatBox = document.getElementById('chatMessages');
        if (chatBox) {
            chatBox.scrollTop = chatBox.scrollHeight;
        }
    }
    
    /**
     * Set loading state
     */
    setLoading(isLoading) {
        this.isLoading = isLoading;
        
        const sendBtn = document.getElementById('chatSendBtn');
        if (sendBtn) {
            if (isLoading) {
                sendBtn.disabled = true;
                sendBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';
            } else {
                sendBtn.disabled = false;
                sendBtn.innerHTML = '<i class="fas fa-paper-plane"></i>';
            }
        }
    }
    
    /**
     * Set exercise context
     */
    setExerciseContext(exerciseName, metrics = {}) {
        this.lastExercise = exerciseName;
        this.sessionContext = {
            exercise: exerciseName,
            reps: metrics.reps,
            quality: metrics.quality,
            angle: metrics.angle,
            duration: metrics.duration
        };
    }
    
    /**
     * Clear chat history
     */
    clearHistory() {
        this.messages = [];
        localStorage.removeItem('chatHistory');
        this.renderMessages();
    }
    
    /**
     * Save chat history to localStorage
     */
    saveChatHistory() {
        try {
            localStorage.setItem('chatHistory', JSON.stringify(this.messages));
        } catch (e) {
            console.warn('Could not save chat history:', e);
        }
    }
    
    /**
     * Load chat history from localStorage
     */
    loadChatHistory() {
        try {
            const saved = localStorage.getItem('chatHistory');
            if (saved) {
                this.messages = JSON.parse(saved);
                this.renderMessages();
            }
        } catch (e) {
            console.warn('Could not load chat history:', e);
        }
    }
    
    /**
     * Escape HTML to prevent XSS
     */
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
    
    /**
     * Format timestamp
     */
    formatTime(date) {
        const hours = date.getHours().toString().padStart(2, '0');
        const minutes = date.getMinutes().toString().padStart(2, '0');
        return `${hours}:${minutes}`;
    }
}

// Create globally accessible instance
const physioChatbot = new PhysioChatbot();

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = physioChatbot;
}
