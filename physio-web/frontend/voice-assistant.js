console.log('🎤 voice-assistant.js is loading...');

// VOICE ASSISTANT MODULE - Minimal Working Version

if (typeof voiceAssistant === 'undefined') {
    console.error('voiceAssistant not found - script.js must load first');
}

function toggleVoiceAssistant() {
    voiceAssistant.enabled = !voiceAssistant.enabled;
    console.log('Voice', voiceAssistant.enabled ? 'ENABLED' : 'DISABLED');
}

function speak(text, priority) {
    if (!voiceAssistant.enabled || !voiceAssistant.synth) return;
    if (!text) return;
    
    try {
        const now = Date.now();
        if (now - voiceAssistant.lastSpokenTime < 1000 && priority !== 'high') return;
        
        const utterance = new SpeechSynthesisUtterance(text);
        utterance.rate = voiceAssistant.voiceSpeed;
        utterance.pitch = voiceAssistant.voicePitch;
        utterance.volume = voiceAssistant.volume;
        
        const voices = voiceAssistant.synth.getVoices();
        if (voices.length > 0) {
            utterance.voice = (voiceAssistant.voiceGender === 'female') ? (voices[1] || voices[0]) : voices[0];
        }
        
        utterance.onstart = () => { voiceAssistant.isSpeaking = true; };
        utterance.onend = () => { voiceAssistant.isSpeaking = false; };
        
        voiceAssistant.synth.speak(utterance);
        voiceAssistant.lastSpokenTime = now;
        
    } catch (e) {
        console.error('speak error:', e);
    }
}

function stopSpeaking() {
    if (voiceAssistant.synth) {
        voiceAssistant.synth.cancel();
        voiceAssistant.isSpeaking = false;
    }
}

function speakRepCount(num) {
    const msgs = [
        `Excellent! That's rep ${num}!`,
        `Perfect! Rep ${num} completed!`,
        `Great job! Rep ${num}!`,
        `Perfect form! Rep ${num}!`,
        `Fantastic! Rep ${num} done!`,
        `Nice work! Rep ${num}!`,
        `Outstanding! Rep ${num}!`
    ];
    speak(msgs[Math.floor(Math.random() * msgs.length)], 'high');
}

function speakFormFeedback(arr) {
    if (!arr || arr.length === 0) return;
    
    let feedbackText = arr[0];
    if (!feedbackText) return;
    
    // Remove emojis and clean text
    const cleanText = feedbackText.replace(/[^\w\s.,'!?'-]/g, '');
    
    // Map common feedback patterns to coaching messages
    let spokenMessage = '';
    
    if (cleanText.toLowerCase().includes('increase range')) {
        spokenMessage = 'Good effort. Try to increase your range of motion a bit more.';
    } else if (cleanText.toLowerCase().includes('decrease range')) {
        spokenMessage = 'Reduce the range slightly. Bring it back to the optimal angle.';
    } else if (cleanText.toLowerCase().includes('keep arms straight')) {
        spokenMessage = 'Keep your arms straight and controlled. Great form!';
    } else if (cleanText.toLowerCase().includes('align')) {
        spokenMessage = 'Keep your alignment steady. You\'re doing well.';
    } else if (cleanText.toLowerCase().includes('balance')) {
        spokenMessage = 'Balance your movements equally on both sides.';
    } else if (cleanText.toLowerCase().includes('shoulder')) {
        spokenMessage = 'Keep your shoulders level and relaxed.';
    } else if (cleanText.toLowerCase().includes('hip')) {
        spokenMessage = 'Keep your hips stable throughout the movement.';
    } else if (cleanText.toLowerCase().includes('knee')) {
        spokenMessage = 'Control your knee movement. Good form!';
    } else if (cleanText.toLowerCase().includes('elbow')) {
        spokenMessage = 'Control your elbow and arm movement.';
    } else if (cleanText.toLowerCase().includes('posture') || cleanText.toLowerCase().includes('position')) {
        spokenMessage = 'Adjust your position for better form.';
    } else {
        // Default: only speak meaningful corrections
        if (cleanText && cleanText.length > 5 && !cleanText.includes('Perfect')) {
            spokenMessage = cleanText;
        } else {
            return;  // Don't speak generic "perfect form" messages
        }
    }
    
    if (spokenMessage) {
        speak(spokenMessage, 'normal');
    }
}

function voiceDiagnostic() {
    console.clear();
    console.log('=== VOICE DIAGNOSTIC ===');
    console.log('API:', !!window.speechSynthesis);
    const voices = voiceAssistant.synth ? voiceAssistant.synth.getVoices() : [];
    console.log('Voices:', voices.length);
    console.log('Enabled:', voiceAssistant.enabled);
    console.log('Volume:', voiceAssistant.volume);
    console.log('speak function:', typeof speak);
    console.log('toggleVoiceAssistant function:', typeof toggleVoiceAssistant);
}

function initializeVoiceAssistant() {
    console.log('Voice Assistant initialized');
    return true;
}

console.log('✅ Voice Assistant module loaded - voiceDiagnostic available');



