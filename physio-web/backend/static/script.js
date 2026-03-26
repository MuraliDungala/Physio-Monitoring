// Global variables
let currentUser = null;
let authToken = null;
let websocket = null;
let videoStream = null;
let currentExercise = null;
let exerciseData = {
    reps: 0,
    angle: 0,
    quality: 0,
    posture: 'Correct'
};

// API Configuration
const API_BASE = 'http://localhost:8000';

// Initialize app
console.log('🚀 Script.js loaded');
document.addEventListener('DOMContentLoaded', function() {
    console.log('✅ DOMContentLoaded fired - initializing app');
    initializeApp();
    setupEventListeners();
    checkAuthStatus();
    console.log('✅ App initialization complete');
});

// Global click handler for debugging
document.addEventListener('click', function(e) {
    if (e.target && e.target.tagName === 'BUTTON') {
        console.log('🖱️ Button clicked:', e.target.className, e.target.textContent, e.target.onclick);
    }
}, true);

function initializeApp() {
    // Load saved user data
    const savedUser = localStorage.getItem('currentUser');
    const savedToken = localStorage.getItem('authToken');
    
    if (savedUser && savedToken) {
        currentUser = JSON.parse(savedUser);
        authToken = savedToken;
        updateUIForAuthenticatedUser();
    }
}

function setupEventListeners() {
    // Navigation
    document.querySelectorAll('.nav-link').forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const page = this.dataset.page;
            showPage(page);
        });
    });

    // Category cards
    document.querySelectorAll('.category-card').forEach(card => {
        card.addEventListener('click', function() {
            const category = this.dataset.category;
            loadCategoryExercises(category);
        });
    });

    // Auth buttons
    document.getElementById('loginBtn').addEventListener('click', showLoginModal);
    document.getElementById('logoutBtn').addEventListener('click', logout);

    // Modal controls
    document.querySelectorAll('.modal-close').forEach(btn => {
        btn.addEventListener('click', closeModal);
    });

    document.getElementById('showRegister').addEventListener('click', function(e) {
        e.preventDefault();
        closeModal();
        showRegisterModal();
    });

    document.getElementById('showLogin').addEventListener('click', function(e) {
        e.preventDefault();
        closeModal();
        showLoginModal();
    });

    // Forms
    document.getElementById('loginForm').addEventListener('submit', handleLogin);
    document.getElementById('registerForm').addEventListener('submit', handleRegister);

    // Exercise controls
    document.getElementById('startBtn').addEventListener('click', startCamera);
    document.getElementById('pauseBtn').addEventListener('click', pauseExercise);
    document.getElementById('resetBtn').addEventListener('click', resetExercise);

    // Chatbot
    document.getElementById('sendBtn').addEventListener('click', sendChatMessage);
    document.getElementById('chatInput').addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            sendChatMessage();
        }
    });

    // Close modals on outside click
    window.addEventListener('click', function(e) {
        if (e.target.classList.contains('modal')) {
            closeModal();
        }
    });
}

// Navigation
function showPage(pageName) {
    console.log('🔄 showPage called with:', pageName);
    // Hide all pages
    document.querySelectorAll('.page').forEach(page => {
        page.classList.remove('active');
    });

    // Show selected page
    const targetPage = document.getElementById(pageName + 'Page');
    if (targetPage) {
        targetPage.classList.add('active');
        console.log('✅ Page shown:', pageName + 'Page');
    } else {
        console.warn('⚠️ Page not found:', pageName + 'Page');
    }

    // Update nav links
    document.querySelectorAll('.nav-link').forEach(link => {
        link.classList.remove('active');
    });
    const navLink = document.querySelector(`[data-page="${pageName}"]`);
    if (navLink) {
        navLink.classList.add('active');
    }

    // Load page-specific data
    if (pageName === 'dashboard' && currentUser) {
        loadDashboardData();
    }
}

// Authentication
function showLoginModal() {
    document.getElementById('loginModal').classList.add('active');
}

function showRegisterModal() {
    document.getElementById('registerModal').classList.add('active');
}

function closeModal() {
    document.querySelectorAll('.modal').forEach(modal => {
        modal.classList.remove('active');
    });
}

async function handleLogin(e) {
    e.preventDefault();
    
    const formData = new FormData(e.target);
    const username = formData.get('username');
    const password = formData.get('password');

    try {
        const response = await fetch(`${API_BASE}/token`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: `username=${encodeURIComponent(username)}&password=${encodeURIComponent(password)}`
        });

        if (response.ok) {
            const data = await response.json();
            authToken = data.access_token;
            
            // Get user info
            const userResponse = await fetch(`${API_BASE}/users/me`, {
                headers: {
                    'Authorization': `Bearer ${authToken}`
                }
            });

            if (userResponse.ok) {
                currentUser = await userResponse.json();
                localStorage.setItem('currentUser', JSON.stringify(currentUser));
                localStorage.setItem('authToken', authToken);
                updateUIForAuthenticatedUser();
                closeModal();
                showNotification('Login successful!', 'success');
            }
        } else {
            showNotification('Login failed. Please check your credentials.', 'error');
        }
    } catch (error) {
        console.error('Login error:', error);
        showNotification('Login failed. Please try again.', 'error');
    }
}

async function handleRegister(e) {
    e.preventDefault();
    
    const formData = new FormData(e.target);
    const userData = {
        username: formData.get('username'),
        email: formData.get('email'),
        full_name: formData.get('full_name'),
        password: formData.get('password')
    };

    // Client-side validation
    if (!userData.username || userData.username.length < 3) {
        showNotification('Username must be at least 3 characters long', 'error');
        return;
    }
    
    if (!userData.email || !userData.email.includes('@') || !userData.email.includes('.')) {
        showNotification('Please enter a valid email address', 'error');
        return;
    }
    
    if (!userData.password || userData.password.length < 6) {
        showNotification('Password must be at least 6 characters long', 'error');
        return;
    }
    
    if (userData.password.length > 72) {
        showNotification('Password must be less than 72 characters long', 'error');
        return;
    }

    try {
        const response = await fetch(`${API_BASE}/register`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(userData)
        });

        if (response.ok) {
            const user = await response.json();
            showNotification('Registration successful! Please login.', 'success');
            closeModal();
            showLoginModal();
        } else {
            const errorData = await response.json();
            showNotification(errorData.detail || 'Registration failed. Please try again.', 'error');
        }
    } catch (error) {
        console.error('Registration error:', error);
        showNotification('Registration failed. Please try again.', 'error');
    }
}

function logout() {
    currentUser = null;
    authToken = null;
    localStorage.removeItem('currentUser');
    localStorage.removeItem('authToken');
    
    if (websocket) {
        websocket.close();
        websocket = null;
    }
    
    updateUIForLoggedOutUser();
    showPage('home');
    showNotification('Logged out successfully', 'info');
}

function checkAuthStatus() {
    if (currentUser && authToken) {
        updateUIForAuthenticatedUser();
    } else {
        updateUIForLoggedOutUser();
    }
}

function updateUIForAuthenticatedUser() {
    document.getElementById('loginBtn').style.display = 'none';
    document.getElementById('logoutBtn').style.display = 'block';
}

function updateUIForLoggedOutUser() {
    document.getElementById('loginBtn').style.display = 'block';
    document.getElementById('logoutBtn').style.display = 'none';
}

// Exercises
async function loadCategoryExercises(category) {
    try {
        const response = await fetch(`${API_BASE}/exercises/category/${category}`);
        if (response.ok) {
            const exercises = await response.json();
            displayCategoryExercises(category, exercises);
            showPage('exerciseList');
        }
    } catch (error) {
        console.error('Error loading exercises:', error);
        showNotification('Failed to load exercises', 'error');
    }
}

function displayCategoryExercises(category, exercises) {
    document.getElementById('categoryTitle').textContent = `${category} Exercises`;
    
    const exerciseList = document.getElementById('exerciseList');
    exerciseList.innerHTML = '';

    exercises.forEach(exercise => {
        const exerciseItem = document.createElement('div');
        exerciseItem.className = 'exercise-item';
        exerciseItem.innerHTML = `
            <h3>${exercise.name}</h3>
            <p>${exercise.description || 'No description available'}</p>
            <p><strong>Instructions:</strong> ${exercise.instructions || 'No instructions available'}</p>
            <button class="btn btn-primary" onclick="startExercise('${exercise.name}')">
                <i class="fas fa-play"></i> Start Exercise
            </button>
        `;
        exerciseList.appendChild(exerciseItem);
    });
}

function startExercise(exerciseName) {
    currentExercise = exerciseName;
    document.getElementById('exerciseTitle').textContent = exerciseName;
    showPage('exercise');
}

// Camera and WebSocket
async function startCamera() {
    try {
        // Get camera stream
        videoStream = await navigator.mediaDevices.getUserMedia({ 
            video: { 
                width: { ideal: 640 },
                height: { ideal: 480 }
            } 
        });
        
        const video = document.getElementById('videoElement');
        video.srcObject = videoStream;
        
        // Hide placeholder, show video
        document.getElementById('cameraPlaceholder').style.display = 'none';
        video.style.display = 'block';
        
        // Connect WebSocket
        connectWebSocket();
        
        // Update UI
        document.getElementById('startBtn').style.display = 'none';
        document.getElementById('pauseBtn').style.display = 'inline-flex';
        
        // Start sending frames
        startFrameSending();
        
        // Send exercise selection
        if (currentExercise && websocket) {
            websocket.send(JSON.stringify({
                type: 'select_exercise',
                exercise_name: currentExercise
            }));
        }
        
    } catch (error) {
        console.error('Camera error:', error);
        showNotification('Failed to access camera. Please check permissions.', 'error');
    }
}

function connectWebSocket() {
    if (!currentUser || !authToken) {
        showNotification('Please login to start exercises', 'error');
        return;
    }

    const wsUrl = `ws://localhost:8000/ws/${currentUser.id}`;
    websocket = new WebSocket(wsUrl);

    websocket.onopen = function() {
        console.log('WebSocket connected');
        showNotification('Connected to exercise tracking system', 'success');
    };

    websocket.onmessage = function(event) {
        const data = JSON.parse(event.data);
        handleWebSocketMessage(data);
    };

    websocket.onerror = function(error) {
        console.error('WebSocket error:', error);
        showNotification('Connection error. Please try again.', 'error');
    };

    websocket.onclose = function() {
        console.log('WebSocket disconnected');
        websocket = null;
    };
}

function handleWebSocketMessage(data) {
    switch (data.type) {
        case 'exercise_feedback':
            updateExerciseFeedback(data);
            break;
        case 'exercise_selected':
            console.log('Exercise selected:', data.exercise);
            break;
        case 'exercise_reset':
            resetExerciseData();
            break;
        case 'error':
            showNotification(data.message, 'error');
            break;
    }
}

function updateExerciseFeedback(data) {
    // Update exercise display
    document.getElementById('currentExercise').textContent = data.exercise;
    document.getElementById('repCount').textContent = data.reps;
    document.getElementById('jointAngle').textContent = `${data.angle.toFixed(1)}°`;
    document.getElementById('qualityScore').textContent = `${data.quality_score.toFixed(1)}%`;
    
    // Update posture feedback
    const postureElement = document.getElementById('postureFeedback');
    postureElement.textContent = data.posture_message;
    postureElement.className = data.posture_message === 'Correct' ? 'posture-value' : 'posture-value incorrect';
    
    // Update skeleton display
    if (data.skeleton_image) {
        const skeletonElement = document.getElementById('skeletonDisplay');
        if (skeletonElement) {
            skeletonElement.src = `data:image/jpeg;base64,${data.skeleton_image}`;
            skeletonElement.style.display = 'block';
        }
    }
    
    // Update landmarks status
    const landmarksElement = document.getElementById('landmarksStatus');
    if (landmarksElement) {
        landmarksElement.textContent = data.landmarks_detected ? '✅ Detected' : '❌ Not Detected';
        landmarksElement.className = data.landmarks_detected ? 'landmarks-detected' : 'landmarks-not-detected';
    }
    
    // Update voice feedback
    if (data.voice_message) {
        const voiceElement = document.getElementById('voiceMessage');
        voiceElement.textContent = data.voice_message;
        
        // Add animation
        const voiceContainer = document.getElementById('voiceFeedback');
        voiceContainer.style.animation = 'pulse 0.5s';
        setTimeout(() => {
            voiceContainer.style.animation = '';
        }, 500);
    }
    
    // Store exercise data
    exerciseData = {
        reps: data.reps,
        angle: data.angle,
        quality: data.quality_score,
        posture: data.posture_message
    };
}

function startFrameSending() {
    const video = document.getElementById('videoElement');
    const canvas = document.createElement('canvas');
    const ctx = canvas.getContext('2d');
    
    canvas.width = 640;
    canvas.height = 480;

    function sendFrame() {
        if (video.readyState === video.HAVE_ENOUGH_DATA && websocket && websocket.readyState === WebSocket.OPEN) {
            ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
            
            canvas.toBlob(function(blob) {
                const reader = new FileReader();
                reader.onloadend = function() {
                    const base64data = reader.result.split(',')[1];
                    
                    websocket.send(JSON.stringify({
                        type: 'frame',
                        frame_data: base64data
                    }));
                };
                reader.readAsDataURL(blob);
            }, 'image/jpeg', 0.8);
        }
        
        if (websocket && websocket.readyState === WebSocket.OPEN) {
            requestAnimationFrame(sendFrame);
        }
    }
    
    sendFrame();
}

function pauseExercise() {
    if (websocket) {
        websocket.close();
        websocket = null;
    }
    
    if (videoStream) {
        videoStream.getTracks().forEach(track => track.stop());
        videoStream = null;
    }
    
    document.getElementById('startBtn').style.display = 'inline-flex';
    document.getElementById('pauseBtn').style.display = 'none';
    
    showNotification('Exercise paused', 'info');
}

function resetExercise() {
    if (websocket) {
        websocket.send(JSON.stringify({ type: 'reset' }));
    }
    
    resetExerciseData();
    showNotification('Exercise reset', 'info');
}

function resetExerciseData() {
    exerciseData = {
        reps: 0,
        angle: 0,
        quality: 0,
        posture: 'Correct'
    };
    
    document.getElementById('currentExercise').textContent = 'Detecting';
    document.getElementById('repCount').textContent = '0';
    document.getElementById('jointAngle').textContent = '0°';
    document.getElementById('qualityScore').textContent = '0%';
    document.getElementById('postureFeedback').textContent = 'Correct';
    document.getElementById('postureFeedback').className = 'posture-value';
    document.getElementById('voiceMessage').textContent = 'Voice guidance will appear here';
}

function exitExercise() {
    pauseExercise();
    
    // Close websocket connection
    if (websocket && websocket.readyState === WebSocket.OPEN) {
        try {
            websocket.close();
            console.log('✓ WebSocket closed');
        } catch (e) {
            console.warn('Could not close websocket:', e);
        }
        websocket = null;
    }
    
    resetExerciseData();
    showPage('exercises');
}

// Dashboard
async function loadDashboardData() {
    if (!currentUser || !authToken) return;

    try {
        // Load sessions
        const sessionsResponse = await fetch(`${API_BASE}/sessions`, {
            headers: {
                'Authorization': `Bearer ${authToken}`
            }
        });

        if (sessionsResponse.ok) {
            const sessions = await sessionsResponse.json();
            updateDashboardStats(sessions);
            displayRecentSessions(sessions);
        }
    } catch (error) {
        console.error('Error loading dashboard data:', error);
    }
}

function updateDashboardStats(sessions) {
    const totalSessions = sessions.length;
    const totalReps = sessions.reduce((sum, session) => sum + session.total_reps, 0);
    const avgQuality = sessions.length > 0 ? 
        sessions.reduce((sum, session) => sum + session.quality_score, 0) / sessions.length : 0;
    
    // Calculate unique days
    const uniqueDays = new Set(sessions.map(session => 
        new Date(session.date).toDateString()
    )).size;

    document.getElementById('totalSessions').textContent = totalSessions;
    document.getElementById('totalReps').textContent = totalReps;
    document.getElementById('avgQuality').textContent = `${avgQuality.toFixed(1)}%`;
    document.getElementById('daysActive').textContent = uniqueDays;
}

function displayRecentSessions(sessions) {
    const sessionsList = document.getElementById('sessionsList');
    sessionsList.innerHTML = '';

    sessions.slice(0, 10).forEach(session => {
        const sessionItem = document.createElement('div');
        sessionItem.className = 'session-item';
        
        const date = new Date(session.date);
        const dateStr = date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
        
        sessionItem.innerHTML = `
            <div class="session-info">
                <h4>${session.exercise_name}</h4>
                <p>${dateStr}</p>
            </div>
            <div class="session-stats">
                <div class="reps">${session.total_reps} reps</div>
                <div class="quality">${session.quality_score.toFixed(1)}% quality</div>
            </div>
        `;
        
        sessionsList.appendChild(sessionItem);
    });

    if (sessions.length === 0) {
        sessionsList.innerHTML = '<p>No sessions yet. Start exercising to see your progress!</p>';
    }
}

// Chatbot
async function sendChatMessage() {
    const input = document.getElementById('chatInput');
    const message = input.value.trim();
    
    if (!message) return;

    // Add user message to chat
    addChatMessage(message, 'user');
    input.value = '';

    try {
        const response = await fetch(`${API_BASE}/chatbot`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${authToken}`
            },
            body: JSON.stringify({
                message: message,
                exercise_context: currentExercise
            })
        });

        if (response.ok) {
            const data = await response.json();
            addChatMessage(data.response, 'bot');
        } else {
            addChatMessage('Sorry, I encountered an error. Please try again.', 'bot');
        }
    } catch (error) {
        console.error('Chatbot error:', error);
        addChatMessage('Sorry, I encountered an error. Please try again.', 'bot');
    }
}

function addChatMessage(message, sender) {
    const messagesContainer = document.getElementById('chatMessages');
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${sender}-message`;
    
    const icon = sender === 'bot' ? 'fa-robot' : 'fa-user';
    
    messageDiv.innerHTML = `
        <i class="fas ${icon}"></i>
        <div class="message-content">
            <p>${message}</p>
        </div>
    `;
    
    messagesContainer.appendChild(messageDiv);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

// Quick chat actions
async function askExerciseList() {
    try {
        const response = await fetch(`${API_BASE}/chatbot/exercises`, {
            headers: {
                'Authorization': `Bearer ${authToken}`
            }
        });

        if (response.ok) {
            const data = await response.json();
            addChatMessage(data.exercises, 'bot');
        }
    } catch (error) {
        console.error('Error getting exercise list:', error);
    }
}

async function askSafetyTip() {
    try {
        const response = await fetch(`${API_BASE}/chatbot/safety-tip`, {
            headers: {
                'Authorization': `Bearer ${authToken}`
            }
        });

        if (response.ok) {
            const data = await response.json();
            addChatMessage(data.tip, 'bot');
        }
    } catch (error) {
        console.error('Error getting safety tip:', error);
    }
}

function askPostureTips() {
    addChatMessage('Maintain proper posture during exercises: Keep your back straight, shoulders relaxed, and move slowly and controlled. The system will provide real-time feedback on your posture.', 'bot');
}

// Notifications
function showNotification(message, type = 'info') {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.textContent = message;
    
    // Add to page
    document.body.appendChild(notification);
    
    // Position and show
    notification.style.position = 'fixed';
    notification.style.top = '20px';
    notification.style.right = '20px';
    notification.style.zIndex = '3000';
    notification.style.padding = '1rem 1.5rem';
    notification.style.borderRadius = '5px';
    notification.style.color = 'white';
    notification.style.fontWeight = '500';
    notification.style.boxShadow = '0 5px 15px rgba(0,0,0,0.2)';
    notification.style.animation = 'slideIn 0.3s ease';
    
    // Set background color based on type
    const colors = {
        success: '#28a745',
        error: '#dc3545',
        info: '#17a2b8',
        warning: '#ffc107'
    };
    notification.style.backgroundColor = colors[type] || colors.info;
    
    // Remove after 3 seconds
    setTimeout(() => {
        notification.style.animation = 'slideOut 0.3s ease';
        setTimeout(() => {
            document.body.removeChild(notification);
        }, 300);
    }, 3000);
}

// Add notification animations
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from {
            transform: translateX(100%);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    
    @keyframes slideOut {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(100%);
            opacity: 0;
        }
    }
    
    @keyframes pulse {
        0%, 100% {
            transform: scale(1);
        }
        50% {
            transform: scale(1.05);
        }
    }
`;
document.head.appendChild(style);
