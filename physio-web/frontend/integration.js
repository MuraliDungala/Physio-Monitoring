/**
 * ============================================================================
 * INTEGRATION MODULE - Physio Monitoring System
 * ============================================================================
 * Initializes all new feature modules and sets up event listeners
 * Runs after all module scripts are loaded
 * ============================================================================
 */

console.log('🔄 Loading Integration Module...');

document.addEventListener('DOMContentLoaded', function() {
    console.log('✅ DOM Ready - Initializing Features...');
    
    // ========== LANGUAGE SYSTEM INITIALIZATION (Must be first!) ==========
    // Initialize language system and update UI
    if (typeof i18n !== 'undefined' && i18n.updateUI) {
        console.log('🌍 Initializing language system and updating UI...');
        i18n.updateUI();
    }
    
    // ========== LANGUAGE FEATURE INITIALIZATION ==========
    initializeLanguageSystem();
    
    // ========== VOICE SYSTEM INITIALIZATION ==========
    initializeVoiceSystem();
    
    // ========== LOADING MANAGER INITIALIZATION ==========
    initializeLoadingManager();
    
    // ========== THERAPIST DASHBOARD INITIALIZATION ==========
    initializeTherapistDashboard();
    
    console.log('✅ All Features Initialized Successfully!');
});

/**
 * Initialize Language Toggle System
 */
function initializeLanguageSystem() {
    console.log('🌍 Initializing Language System...');
    
    try {
        // Wait for i18n to be available
        if (typeof i18n === 'undefined') {
            console.error('❌ i18n module not defined - check if i18n.js loaded');
            return;
        }
        
        console.log('✅ i18n module found:', typeof i18n);
        console.log('✅ English-only mode: Language switching disabled');
        
        // Initialize i18n with English only
        const currentLang = i18n.getLanguage();
        console.log('📍 Current language:', currentLang);
        console.log('✅ Language System Initialized Successfully (English Only)');
    } catch (error) {
        console.error('❌ Error initializing language system:', error);
    }
}

/**
 * Initialize Voice Assistant System
 */
function initializeVoiceSystem() {
    console.log('Initializing Voice System...');
    
    try {
        if (typeof voiceAssistant === 'undefined') {
            console.warn('⚠️  Voice Assistant not available');
            return;
        }
        
        const voiceBtn = document.getElementById('voiceToggleBtn');
        
        if (!voiceBtn) {
            console.warn('⚠️  Voice toggle button not found');
            return;
        }
        
        // Check initial state from localStorage
        const voiceEnabled = localStorage.getItem('voiceEnabled') !== 'false';
        if (!voiceEnabled) {
            voiceAssistant.disable();
        }
        
        // Toggle voice assistant
        voiceBtn.addEventListener('click', () => {
            const isEnabled = voiceAssistant.toggle();
            
            // Update button state
            voiceBtn.classList.toggle('voice-active', isEnabled);
            
            // Save state
            localStorage.setItem('voiceEnabled', isEnabled);
            
            // Provide feedback
            if (isEnabled) {
                console.log('🔊 Voice Assistant Enabled');
                voiceAssistant.trigger('start');
            } else {
                console.log('🔇 Voice Assistant Disabled');
            }
        });
        
        // Set initial button state
        if (voiceEnabled) {
            voiceBtn.classList.add('voice-active');
        }
        
        console.log('✅ Voice System Initialized');
    } catch (error) {
        console.error('❌ Error initializing voice system:', error);
    }
}

/**
 * Initialize AI Chatbot
 */
function initializeChatbot() {
    console.log('Initializing Chatbot...');
    
    try {
        if (typeof physioChatbot === 'undefined') {
            console.warn('⚠️  Chatbot module not available');
            return;
        }
        
        // Create chatbot container if it doesn't exist
        let chatContainer = document.getElementById('chatContainer');
        if (!chatContainer) {
            chatContainer = document.createElement('div');
            chatContainer.id = 'chatContainer';
            chatContainer.className = 'chat-container';
            chatContainer.innerHTML = `
                <div class="chat-header">
                    <h3 data-i18n="aiChatbot">AI Assistant</h3>
                    <button class="close-btn">&times;</button>
                </div>
                <div class="chat-messages" id="chatMessages"></div>
                <div class="chat-input-area">
                    <input 
                        type="text" 
                        id="chatInput" 
                        placeholder="Ask a question..."
                        data-i18n="askQuestion"
                    >
                    <button id="chatSendBtn">
                        <i class="fas fa-paper-plane"></i>
                    </button>
                </div>
            `;
            document.body.appendChild(chatContainer);
        }
        
        const chatInput = document.getElementById('chatInput');
        const chatSendBtn = document.getElementById('chatSendBtn');
        const closeBtn = chatContainer.querySelector('.close-btn');
        
        if (!chatInput || !chatSendBtn) {
            console.warn('⚠️  Chat elements not found');
            return;
        }
        
        // Send message handler
        function sendMessage() {
            const message = chatInput.value.trim();
            if (!message) return;
            
            // Add user message
            physioChatbot.sendMessage(message);
            
            // Clear input
            chatInput.value = '';
            
            // Focus back
            chatInput.focus();
        }
        
        // Send on button click
        chatSendBtn.addEventListener('click', sendMessage);
        
        // Send on Enter key
        chatInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                e.preventDefault();
                sendMessage();
            }
        });
        
        // Close button
        if (closeBtn) {
            closeBtn.addEventListener('click', () => {
                chatContainer.style.display = 'none';
            });
        }
        
        console.log('✅ Chatbot Initialized');
    } catch (error) {
        console.error('❌ Error initializing chatbot:', error);
    }
}

/**
 * Initialize Loading Manager
 */
function initializeLoadingManager() {
    console.log('Initializing Loading Manager...');
    
    try {
        if (typeof loadingManager === 'undefined') {
            console.warn('⚠️  Loading Manager not available');
            return;
        }
        
        // Create loading overlay if it doesn't exist
        if (!document.getElementById('loadingOverlay')) {
            const overlay = document.createElement('div');
            overlay.id = 'loadingOverlay';
            overlay.className = 'loading-overlay';
            overlay.innerHTML = `
                <div class="loading-spinner"></div>
                <div class="loading-message" id="loadingMessage"></div>
            `;
            document.body.appendChild(overlay);
        }
        
        // Override loadingManager to use our overlay
        loadingManager.startLoading = function(message = 'Processing...') {
            const overlay = document.getElementById('loadingOverlay');
            const msgEl = document.getElementById('loadingMessage');
            if (overlay) {
                overlay.classList.add('active');
                if (msgEl) msgEl.textContent = message;
            }
        };
        
        loadingManager.stopLoading = function() {
            const overlay = document.getElementById('loadingOverlay');
            if (overlay) {
                overlay.classList.remove('active');
            }
        };
        
        console.log('✅ Loading Manager Initialized');
    } catch (error) {
        console.error('❌ Error initializing loading manager:', error);
    }
}

/**
 * Initialize Therapist Dashboard
 */
function initializeTherapistDashboard() {
    console.log('Initializing Therapist Dashboard...');
    
    try {
        if (typeof therapistDashboard === 'undefined') {
            console.warn('⚠️  Therapist Dashboard not available');
            return;
        }
        
        // Check if user is therapist
        const currentUser = JSON.parse(localStorage.getItem('currentUser') || '{}');
        
        if (currentUser.role === 'therapist') {
            console.log('✅ User is therapist - Dashboard available');
            
            // Create dashboard container if needed
            let dashboard = document.getElementById('therapistDashboard');
            if (!dashboard) {
                dashboard = document.createElement('div');
                dashboard.id = 'therapistDashboard';
                dashboard.className = 'therapist-section';
                document.body.appendChild(dashboard);
            }
            
            // Initialize dashboard
            therapistDashboard.init();
            
        } else {
            console.log('ℹ️  User is not therapist - Dashboard hidden');
        }
        
        console.log('✅ Therapist Dashboard Initialized');
    } catch (error) {
        console.error('❌ Error initializing therapist dashboard:', error);
    }
}

/**
 * Injury Risk Integration - Called during exercise
 */
window.triggerInjuryRiskAssessment = function(exerciseData) {
    try {
        if (typeof injuryPredictor === 'undefined') {
            console.warn('⚠️  Injury Predictor not available');
            return null;
        }
        
        const assessment = injuryPredictor.predictRisk({
            exerciseName: exerciseData.name,
            bodyPart: exerciseData.bodyPart,
            jointAngle: exerciseData.angle,
            qualityScore: exerciseData.quality,
            reps: exerciseData.reps,
            duration: exerciseData.duration
        });
        
        // Log risk level
        console.log(`⚠️  Injury Risk Level: ${assessment.riskLevel}`);
        
        // Trigger voice warning if high risk
        if (assessment.riskLevel === 'HIGH' && typeof voiceAssistant !== 'undefined') {
            voiceAssistant.trigger('wrongPosture');
        }
        
        return assessment;
    } catch (error) {
        console.error('❌ Error in injury risk assessment:', error);
        return null;
    }
};

/**
 * Exercise Integration - Called when exercise starts
 */
window.onExerciseStart = function(exerciseName) {
    try {
        // Trigger voice
        if (typeof voiceAssistant !== 'undefined') {
            voiceAssistant.trigger('start');
        }
        
        // Set chatbot context
        if (typeof physioChatbot !== 'undefined') {
            physioChatbot.setExerciseContext(exerciseName, {});
        }
        
        console.log(`▶️  Exercise Started: ${exerciseName}`);
    } catch (error) {
        console.error('❌ Error in exercise start:', error);
    }
};

/**
 * Rep Completion Integration - Called when rep is complete
 */
window.onRepComplete = function(repNumber) {
    try {
        if (typeof voiceAssistant !== 'undefined') {
            voiceAssistant.trigger('repComplete');
        }
        
        console.log(`✅ Rep ${repNumber} Completed`);
    } catch (error) {
        console.error('❌ Error in rep completion:', error);
    }
};

/**
 * Exercise End Integration - Called when exercise finishes
 */
window.onExerciseEnd = function(metadata) {
    try {
        if (typeof voiceAssistant !== 'undefined') {
            voiceAssistant.trigger('end');
        }
        
        // Assess injury risk
        if (typeof injuryPredictor !== 'undefined') {
            window.triggerInjuryRiskAssessment(metadata);
        }
        
        console.log(`⏹️  Exercise Ended:`, metadata);
    } catch (error) {
        console.error('❌ Error in exercise end:', error);
    }
};

/**
 * Global Error Handler for this integration
 */
window.addEventListener('error', (event) => {
    if (event.filename && event.filename.includes('integration.js')) {
        console.error('🔴 Integration Error:', event.message);
    }
});

console.log('✅ Integration Module Loaded Successfully');
