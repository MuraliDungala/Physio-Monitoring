/**
 * PhysioMonitor Voice Assistant System
 * Features:
 * - Event-based triggering (not frame-based)
 * - English & Telugu support
 * - Cooldown to prevent repetition
 * - Non-blocking async playback
 */

class VoiceAssistant {
    constructor() {
        this.isEnabled = localStorage.getItem('voiceEnabled') !== 'false';
        this.currentLanguage = i18n.getLanguage();
        this.isSpeaking = false;
        this.lastEventTime = {};
        this.COOLDOWN_MS = 3000; // 3-second cooldown between same events
        
        // Voice messages mapping
        this.voiceMessages = {
            en: {
                start: "Start exercise",
                repComplete: "One repetition completed",
                wrongPosture: "Correct your posture",
                fatigue: "Slow down",
                end: "Exercise completed",
                qualityGood: "Good form",
                qualityBad: "Fix your form",
                warmUp: "Warm up complete",
                restPeriod: "Rest and recover",
                nextExercise: "Ready for next exercise",
            },
            te: {
                start: "వ్యాయామం ప్రారంభించండి",
                repComplete: "ఒక పునరావృతం పూర్తైంది",
                wrongPosture: "మీ భంగిమ సరిచేయండి",
                fatigue: "నెమ్మదిగా చేయండి",
                end: "వ్యాయామం పూర్తైంది",
                qualityGood: "మంచి రూపం",
                qualityBad: "మీ రూపాన్ని సరిచేయండి",
                warmUp: "వార్మ అప్ పూర్తైంది",
                restPeriod: "విశ్రాంతి మరియు కోలుకోండి",
                nextExercise: "తదుపరి వ్యాయామానికి సిద్ధమైంది",
            }
        };
        
        this.init();
    }
    
    /**
     * Initialize voice system
     */
    init() {
        // Listen for language changes
        window.addEventListener('languageChanged', (e) => {
            this.currentLanguage = e.detail.language;
        });
        
        // Update voice status in UI
        this.updateVoiceButton();
    }
    
    /**
     * Toggle voice on/off
     */
    toggle() {
        this.isEnabled = !this.isEnabled;
        localStorage.setItem('voiceEnabled', this.isEnabled);
        this.updateVoiceButton();
        console.log(`Voice Assistant: ${this.isEnabled ? 'ON' : 'OFF'}`);
        return this.isEnabled;
    }
    
    /**
     * Enable voice
     */
    enable() {
        this.isEnabled = true;
        localStorage.setItem('voiceEnabled', true);
        this.updateVoiceButton();
    }
    
    /**
     * Disable voice
     */
    disable() {
        this.isEnabled = false;
        localStorage.setItem('voiceEnabled', false);
        this.updateVoiceButton();
    }
    
    /**
     * Check if voice is enabled
     */
    isVoiceEnabled() {
        return this.isEnabled;
    }
    
    /**
     * Trigger voice event (with cooldown)
     * @param {string} eventType - Event type
     * @param {object} options - Optional config
     */
    async trigger(eventType, options = {}) {
        if (!this.isEnabled) return;
        
        // Check cooldown
        const lastTime = this.lastEventTime[eventType] || 0;
        const now = Date.now();
        
        if (now - lastTime < this.COOLDOWN_MS) {
            console.log(`Voice cooldown: ${eventType}`);
            return;
        }
        
        // Get message
        const message = this.voiceMessages[this.currentLanguage]?.[eventType] ||
                       this.voiceMessages['en'][eventType];
        
        if (message) {
            this.lastEventTime[eventType] = now;
            await this.speak(message);
        }
    }
    
    /**
     * Speak message using Web Speech API
     * @param {string} text - Text to speak
     */
    async speak(text) {
        return new Promise((resolve) => {
            try {
                // Cancel any ongoing speech
                window.speechSynthesis.cancel();
                
                const utterance = new SpeechSynthesisUtterance(text);
                
                // Set voice properties based on language
                if (this.currentLanguage === 'te') {
                    utterance.lang = 'te-IN';
                } else {
                    utterance.lang = 'en-US';
                }
                
                utterance.rate = 1.0;
                utterance.pitch = 1.0;
                utterance.volume = 1.0;
                
                utterance.onstart = () => {
                    this.isSpeaking = true;
                };
                
                utterance.onend = () => {
                    this.isSpeaking = false;
                    resolve();
                };
                
                utterance.onerror = () => {
                    this.isSpeaking = false;
                    resolve();
                };
                
                window.speechSynthesis.speak(utterance);
                
                // Timeout after 30 seconds
                setTimeout(() => {
                    if (this.isSpeaking) {
                        window.speechSynthesis.cancel();
                        this.isSpeaking = false;
                        resolve();
                    }
                }, 30000);
                
            } catch (error) {
                console.error('Voice synthesis error:', error);
                this.isSpeaking = false;
                resolve();
            }
        });
    }
    
    /**
     * Emergency stop
     */
    stop() {
        window.speechSynthesis.cancel();
        this.isSpeaking = false;
    }
    
    /**
     * Update voice button UI
     */
    updateVoiceButton() {
        const btn = document.getElementById('voiceToggleBtn');
        if (btn) {
            if (this.isEnabled) {
                btn.classList.remove('voice-off');
                btn.classList.add('voice-on');
                btn.style.color = '#10b981';
                btn.title = 'Voice ON - Click to disable';
            } else {
                btn.classList.remove('voice-on');
                btn.classList.add('voice-off');
                btn.style.color = '#666';
                btn.title = 'Voice OFF - Click to enable';
            }
        }
    }
}

// Create globally accessible instance
const voiceAssistant = new VoiceAssistant();

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = voiceAssistant;
}
