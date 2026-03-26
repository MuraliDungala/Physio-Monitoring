/**
 * Voice Assistant Control Module
 * Manages voice settings and controls in the UI
 */

class VoiceController {
    constructor() {
        this.enabled = true;
        this.speed = 150;
        this.volume = 0.8;
        this.baseUrl = '';
        this.statusElement = null;
        this.initPromise = this.init();
    }

    async init() {
        try {
            // Get current voice status from server
            const response = await fetch(`${window.API_BASE || 'http://localhost:8001'}/voice/status`, {
                method: 'GET',
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
                    'Content-Type': 'application/json'
                }
            });

            if (response.ok) {
                const data = await response.json();
                const status = data.data;
                this.enabled = status.enabled;
                this.speed = status.speed;
                this.volume = status.volume;
                console.log('✅ Voice Assistant initialized:', status);
            }
        } catch (error) {
            console.warn('Voice status fetch failed (may not be authenticated):', error);
        }
    }

    async toggleVoice() {
        try {
            const response = await fetch(`${window.API_BASE || 'http://localhost:8001'}/voice/toggle`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
                    'Content-Type': 'application/json'
                }
            });

            if (response.ok) {
                const data = await response.json();
                this.enabled = data.enabled;
                this.updateUI();
                console.log('🎤 Voice', this.enabled ? 'enabled' : 'disabled');
                return this.enabled;
            }
        } catch (error) {
            console.error('Error toggling voice:', error);
        }
        return this.enabled;
    }

    async enableVoice() {
        try {
            const response = await fetch(`${window.API_BASE || 'http://localhost:8001'}/voice/enable`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
                    'Content-Type': 'application/json'
                }
            });

            if (response.ok) {
                this.enabled = true;
                this.updateUI();
                console.log('✅ Voice enabled');
            }
        } catch (error) {
            console.error('Error enabling voice:', error);
        }
    }

    async disableVoice() {
        try {
            const response = await fetch(`${window.API_BASE || 'http://localhost:8001'}/voice/disable`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
                    'Content-Type': 'application/json'
                }
            });

            if (response.ok) {
                this.enabled = false;
                this.updateUI();
                console.log('🔇 Voice disabled');
            }
        } catch (error) {
            console.error('Error disabling voice:', error);
        }
    }

    async setSpeed(speed) {
        if (speed < 50 || speed > 300) {
            console.error('Speed must be between 50 and 300 WPM');
            return;
        }

        try {
            const response = await fetch(`${window.API_BASE || 'http://localhost:8001'}/voice/speed?speed=${speed}`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
                    'Content-Type': 'application/json'
                }
            });

            if (response.ok) {
                this.speed = speed;
                this.updateUI();
                console.log(`🎤 Voice speed set to ${speed} WPM`);
            }
        } catch (error) {
            console.error('Error setting voice speed:', error);
        }
    }

    async setVolume(volume) {
        if (volume < 0 || volume > 1) {
            console.error('Volume must be between 0 and 1');
            return;
        }

        try {
            const response = await fetch(`${window.API_BASE || 'http://localhost:8001'}/voice/volume?volume=${volume}`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
                    'Content-Type': 'application/json'
                }
            });

            if (response.ok) {
                this.volume = volume;
                this.updateUI();
                console.log(`🔊 Volume set to ${(volume * 100).toFixed(0)}%`);
            }
        } catch (error) {
            console.error('Error setting voice volume:', error);
        }
    }

    updateUI() {
        // Update voice toggle button
        const voiceBtn = document.getElementById('voice-toggle-btn');
        if (voiceBtn) {
            if (this.enabled) {
                voiceBtn.classList.add('voice-enabled');
                voiceBtn.classList.remove('voice-disabled');
                voiceBtn.innerHTML = '<i class="fas fa-microphone"></i> Voice ON';
                voiceBtn.title = 'Click to disable voice assistance';
            } else {
                voiceBtn.classList.add('voice-disabled');
                voiceBtn.classList.remove('voice-enabled');
                voiceBtn.innerHTML = '<i class="fas fa-microphone-slash"></i> Voice OFF';
                voiceBtn.title = 'Click to enable voice assistance';
            }
        }

        // Update speed slider
        const speedSlider = document.getElementById('voice-speed-slider');
        if (speedSlider) {
            speedSlider.value = this.speed;
        }

        const speedLabel = document.getElementById('voice-speed-label');
        if (speedLabel) {
            speedLabel.textContent = `${this.speed} WPM`;
        }

        // Update volume slider
        const volumeSlider = document.getElementById('voice-volume-slider');
        if (volumeSlider) {
            volumeSlider.value = this.volume;
        }

        const volumeLabel = document.getElementById('voice-volume-label');
        if (volumeLabel) {
            volumeLabel.textContent = `${(this.volume * 100).toFixed(0)}%`;
        }
    }

    createControlPanel() {
        const panel = document.createElement('div');
        panel.className = 'voice-control-panel';
        panel.id = 'voice-control-panel';
        panel.innerHTML = `
            <div class="voice-control-header">
                <h4><i class="fas fa-microphone-alt"></i> Voice Assistant</h4>
                <button class="close-btn" onclick="document.getElementById('voice-control-panel').style.display='none'">
                    <i class="fas fa-times"></i>
                </button>
            </div>
            
            <div class="voice-control-content">
                <!-- Toggle Button -->
                <div class="control-group">
                    <label>Voice Status</label>
                    <button id="voice-toggle-btn" class="voice-btn voice-toggle-btn" onclick="voiceController.toggleVoice()">
                        <i class="fas fa-microphone"></i> Voice ON
                    </button>
                </div>

                <!-- Speed Control -->
                <div class="control-group">
                    <label>Speech Speed</label>
                    <div class="slider-container">
                        <span class="slider-min">50</span>
                        <input 
                            type="range" 
                            id="voice-speed-slider" 
                            class="slider" 
                            min="50" 
                            max="300" 
                            value="150"
                            step="10"
                            onchange="voiceController.setSpeed(this.value)"
                            oninput="voiceController.setSpeed(this.value)"
                        >
                        <span class="slider-max">300</span>
                    </div>
                    <p class="slider-label">Speed: <span id="voice-speed-label">150 WPM</span></p>
                </div>

                <!-- Volume Control -->
                <div class="control-group">
                    <label>Volume</label>
                    <div class="slider-container">
                        <span class="slider-min">🔇</span>
                        <input 
                            type="range" 
                            id="voice-volume-slider" 
                            class="slider" 
                            min="0" 
                            max="1" 
                            value="0.8"
                            step="0.1"
                            onchange="voiceController.setVolume(this.value)"
                            oninput="voiceController.setVolume(this.value)"
                        >
                        <span class="slider-max">🔊</span>
                    </div>
                    <p class="slider-label">Level: <span id="voice-volume-label">80%</span></p>
                </div>

                <!-- Info -->
                <div class="voice-info">
                    <p><strong>Voice Feedback:</strong> Real-time audio guidance during exercises</p>
                    <ul>
                        <li>Exercise instructions and form corrections</li>
                        <li>Repetition counts and completion announcements</li>
                        <li>Fatigue and posture alerts</li>
                        <li>Motivational feedback</li>
                    </ul>
                </div>
            </div>
        `;
        return panel;
    }

    insertControlButton() {
        // Check if button already exists
        if (document.getElementById('voice-control-floating-btn')) {
            return;
        }

        // Create floating button
        const btn = document.createElement('button');
        btn.id = 'voice-control-floating-btn';
        btn.className = 'voice-control-floating-btn';
        btn.innerHTML = '<i class="fas fa-microphone"></i>';
        btn.title = 'Open Voice Assistant Settings';
        btn.onclick = () => {
            const panel = document.getElementById('voice-control-panel');
            if (panel) {
                panel.style.display = panel.style.display === 'none' ? 'block' : 'none';
            }
        };

        document.body.appendChild(btn);
    }

    insertControlPanel() {
        // Check if panel already exists
        if (document.getElementById('voice-control-panel')) {
            return;
        }

        const panel = this.createControlPanel();
        document.body.appendChild(panel);
        this.updateUI();
        this.insertControlButton();
    }
}

// Initialize global voice controller
const voiceController = new VoiceController();

// Auto-insert UI when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        voiceController.initPromise.then(() => {
            voiceController.insertControlPanel();
        });
    });
} else {
    voiceController.initPromise.then(() => {
        voiceController.insertControlPanel();
    });
}
