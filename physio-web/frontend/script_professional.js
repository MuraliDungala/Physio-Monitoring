/* ===========================
   PROFESSIONAL PHYSIOTHERAPY UI
   Main JavaScript Controller
   ============================== */

// Global State
const appState = {
    currentUser: {
        name: 'John Doe',
        email: 'john.doe@example.com',
        avatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=user'
    },
    currentPage: 'home',
    currentCategory: null,
    sessionActive: false,
    repCount: 0,
    sessionStartTime: null
};

// Exercise Database
const exercisesData = {
    'Neck': [
        { name: 'Neck Flexion', reps: '10-15', sets: '3', rom: '45°', icon: '🧠' },
        { name: 'Neck Extension', reps: '10-15', sets: '3', rom: '45°', icon: '🧠' },
        { name: 'Cervical Rotation', reps: '15-20', sets: '3', rom: '90°', icon: '🧠' }
    ],
    'Shoulder': [
        { name: 'Shoulder Flexion', reps: '8-12', sets: '3', rom: '180°', icon: '💪' },
        { name: 'Shoulder Abduction', reps: '8-12', sets: '3', rom: '180°', icon: '💪' },
        { name: 'Internal Rotation', reps: '10-15', sets: '3', rom: '90°', icon: '💪' },
        { name: 'External Rotation', reps: '10-15', sets: '3', rom: '90°', icon: '💪' },
        { name: 'Shoulder Extension', reps: '8-12', sets: '3', rom: '60°', icon: '💪' },
        { name: 'Pendulum Swings', reps: '20-30', sets: '2', rom: '360°', icon: '💪' }
    ],
    'Elbow': [
        { name: 'Elbow Flexion', reps: '10-15', sets: '3', rom: '150°', icon: '🦾' },
        { name: 'Elbow Extension', reps: '10-15', sets: '3', rom: '150°', icon: '🦾' },
        { name: 'Pronation', reps: '15-20', sets: '3', rom: '90°', icon: '🦾' },
        { name: 'Supination', reps: '15-20', sets: '3', rom: '90°', icon: '🦾' }
    ],
    'Wrist': [
        { name: 'Wrist Flexion', reps: '15-20', sets: '3', rom: '90°', icon: '👐' },
        { name: 'Wrist Extension', reps: '15-20', sets: '3', rom: '90°', icon: '👐' },
        { name: 'Radial Deviation', reps: '15-20', sets: '3', rom: '30°', icon: '👐' },
        { name: 'Ulnar Deviation', reps: '15-20', sets: '3', rom: '50°', icon: '👐' },
        { name: 'Wrist Rotation', reps: '20-25', sets: '3', rom: '180°', icon: '👐' }
    ],
    'Hip': [
        { name: 'Hip Flexion', reps: '10-15', sets: '3', rom: '120°', icon: '🦵' },
        { name: 'Hip Extension', reps: '10-15', sets: '3', rom: '30°', icon: '🦵' },
        { name: 'Hip Abduction', reps: '12-15', sets: '3', rom: '45°', icon: '🦵' },
        { name: 'Hip Adduction', reps: '12-15', sets: '3', rom: '35°', icon: '🦵' },
        { name: 'Internal Rotation', reps: '12-15', sets: '3', rom: '45°', icon: '🦵' },
        { name: 'External Rotation', reps: '12-15', sets: '3', rom: '45°', icon: '🦵' }
    ],
    'Knee': [
        { name: 'Knee Flexion', reps: '10-15', sets: '3', rom: '135°', icon: '🦵' },
        { name: 'Knee Extension', reps: '10-15', sets: '3', rom: '0°', icon: '🦵' },
        { name: 'Quad Engagement', reps: '15-20', sets: '3', rom: '0°', icon: '🦵' },
        { name: 'Hamstring Curl', reps: '12-15', sets: '3', rom: '135°', icon: '🦵' },
        { name: 'Leg Press', reps: '8-12', sets: '3', rom: '90°', icon: '🦵' }
    ],
    'Ankle': [
        { name: 'Ankle Flexion', reps: '15-20', sets: '3', rom: '50°', icon: '🦶' },
        { name: 'Ankle Extension', reps: '15-20', sets: '3', rom: '50°', icon: '🦶' },
        { name: 'Inversion', reps: '15-20', sets: '3', rom: '30°', icon: '🦶' },
        { name: 'Eversion', reps: '15-20', sets: '3', rom: '20°', icon: '🦶' },
        { name: 'Ankle Rotation', reps: '20-25', sets: '3', rom: '360°', icon: '🦶' }
    ],
    'Squat': [
        { name: 'Bodyweight Squat', reps: '10-15', sets: '3', rom: '90°', icon: '🏋️' },
        { name: 'Assisted Squat', reps: '12-15', sets: '3', rom: '90°', icon: '🏋️' },
        { name: 'Wall Squat', reps: '20-30s', sets: '3', rom: '90°', icon: '🏋️' },
        { name: 'Split Squat', reps: '8-10', sets: '3', rom: '90°', icon: '🏋️' }
    ]
};

// Initialize App
document.addEventListener('DOMContentLoaded', () => {
    initializeEventListeners();
    navigateToPage('home');
    updateNavbarUser();
    setupCharts();
});

// ========== EVENT LISTENERS ==========
function initializeEventListeners() {
    // Sidebar Navigation
    document.querySelectorAll('.nav-item').forEach(item => {
        item.addEventListener('click', (e) => {
            e.preventDefault();
            const page = item.dataset.page;
            navigateToPage(page);
        });
    });

    // Category Cards
    document.querySelectorAll('.category-card').forEach(card => {
        card.addEventListener('click', () => {
            const category = card.dataset.category;
            navigateToExerciseSubtypes(category);
        });
    });

    // Exercise Cards
    document.addEventListener('click', (e) => {
        if (e.target.closest('.exercise-card')) {
            const exerciseName = e.target.closest('.exercise-card').querySelector('.exercise-name').textContent;
            startExerciseSession(exerciseName);
        }
    });

    // Session Controls
    document.getElementById('startSessionBtn')?.addEventListener('click', startCamera);
    document.getElementById('pauseSessionBtn')?.addEventListener('click', pauseSession);
    document.getElementById('stopSessionBtn')?.addEventListener('click', exitSession);

    // Chatbot
    document.getElementById('floatingChatBtn').addEventListener('click', toggleChatbot);
    document.getElementById('closeChatBot').addEventListener('click', () => {
        document.getElementById('chatbotWidget').classList.remove('active');
    });
    document.getElementById('sendChatBtn')?.addEventListener('click', sendChatMessage);

    document.getElementById('chatbotInput')?.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            sendChatMessage();
        }
    });

    // Quick Replies
    document.querySelectorAll('.quick-reply-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            const query = btn.dataset.query;
            const input = document.getElementById('chatbotInput');
            input.value = query;
            sendChatMessage();
        });
    });

    // Voice Toggle
    document.getElementById('voiceToggle').addEventListener('click', toggleVoice);

    // Logout
    document.getElementById('logoutBtn').addEventListener('click', logout);

    // Sidebar Toggle
    document.getElementById('sidebarToggle').addEventListener('click', toggleSidebar);
    document.getElementById('menuToggle').addEventListener('click', toggleMobileMenu);

    // Week Selector for Rehab Plan
    document.querySelectorAll('.week-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            showWeekPlan(btn.dataset.week);
        });
    });

    // Settings Form
    const saveSettingsBtn = document.querySelector('.settings-footer .btn-primary');
    if (saveSettingsBtn) {
        saveSettingsBtn.addEventListener('click', saveSettings);
    }
}

// ========== PAGE NAVIGATION ==========
function navigateToPage(page) {
    // Hide all pages
    document.querySelectorAll('.page').forEach(p => {
        p.classList.remove('active');
    });

    // Show selected page
    const pageElement = document.getElementById(page + 'Page');
    if (pageElement) {
        pageElement.classList.add('active');
    }

    // Update sidebar active state
    document.querySelectorAll('.nav-item').forEach(item => {
        item.classList.remove('active');
        if (item.dataset.page === page) {
            item.classList.add('active');
        }
    });

    // Update breadcrumb
    updateBreadcrumb(page);

    appState.currentPage = page;

    // Refresh data for certain pages
    if (page === 'dashboard') {
        refreshDashboard();
    }
}

function navigateToExerciseSubtypes(category) {
    appState.currentCategory = category;
    document.getElementById('subtypeTitle').textContent = category + ' Exercises';
    
    const subtypesGrid = document.getElementById('subtypesGrid');
    subtypesGrid.innerHTML = '';

    if (exercisesData[category]) {
        exercisesData[category].forEach(exercise => {
            const card = createExerciseCard(exercise);
            subtypesGrid.appendChild(card);
        });
    }

    navigateToPage('exerciseSubtypes');
}

function createExerciseCard(exercise) {
    const card = document.createElement('div');
    card.className = 'exercise-card';
    card.innerHTML = `
        <div class="exercise-image">
            ${exercise.icon}
        </div>
        <div class="exercise-info">
            <div class="exercise-name">${exercise.name}</div>
            <div class="exercise-target">Range of Motion</div>
            <div class="exercise-specs">
                <span class="exercise-spec"><strong>ROM:</strong> ${exercise.rom}</span>
                <span class="exercise-spec"><strong>Reps:</strong> ${exercise.reps}</span>
            </div>
            <button class="btn btn-primary">
                <i class="fas fa-play"></i> Start
            </button>
        </div>
    `;
    
    card.addEventListener('click', () => startExerciseSession(exercise.name));
    return card;
}

// ========== EXERCISE SESSION ==========
let mediaStream = null;

function startExerciseSession(exerciseName) {
    document.getElementById('sessionExerciseName').textContent = exerciseName;
    appState.sessionStartTime = Date.now();
    appState.repCount = 0;
    navigateToPage('session');
}

async function startCamera() {
    const btn = document.getElementById('startSessionBtn');
    btn.disabled = true;
    
    try {
        mediaStream = await navigator.mediaDevices.getUserMedia({
            video: {
                width: { ideal: 1280 },
                height: { ideal: 720 },
                facingMode: 'user'
            }
        });

        const videoElement = document.getElementById('videoElement');
        videoElement.srcObject = mediaStream;
        
        document.getElementById('cameraPlaceholder').style.display = 'none';
        videoElement.style.display = 'block';
        
        // Show pause button
        document.getElementById('pauseSessionBtn').style.display = 'flex';
        
        // Start session timer
        startSessionTimer();
        
        // Simulate pose detection
        simulatePoseDetection();

        appState.sessionActive = true;
        
        showNotification('Camera started successfully');
    } catch (error) {
        console.error('Error accessing camera:', error);
        showNotification('Error accessing camera', 'error');
        btn.disabled = false;
    }
}

function startSessionTimer() {
    const timerElement = document.querySelector('.session-timer');
    let seconds = 0;

    const timer = setInterval(() => {
        if (!appState.sessionActive) {
            clearInterval(timer);
            return;
        }

        seconds++;
        const mins = Math.floor(seconds / 60);
        const secs = seconds % 60;
        timerElement.textContent = 
            String(mins).padStart(2, '0') + ':' + 
            String(secs).padStart(2, '0');
    }, 1000);
}

function simulatePoseDetection() {
    let reps = 0;
    
    const interval = setInterval(() => {
        if (!appState.sessionActive) {
            clearInterval(interval);
            return;
        }

        // Simulate rep counting
        if (Math.random() > 0.95) {
            reps++;
            appState.repCount = reps;
            document.getElementById('repCounter').textContent = reps;
            
            // Simulate quality score
            const quality = Math.floor(Math.random() * 15) + 85;
            document.getElementById('qualityScore').textContent = quality + '%';
            
            // Simulate joint angle
            const angle = Math.floor(Math.random() * 40) + 60;
            document.getElementById('jointAngle').textContent = angle + '°';
            
            // Simulate fatigue
            const fatigue = ['Low', 'Moderate', 'High'][Math.floor(reps / 5)];
            document.getElementById('fatigueLevel').textContent = fatigue || 'Low';
            
            // Update progress
            const progress = Math.min((reps / 10) * 100, 100);
            document.getElementById('progressBar').style.width = progress + '%';
            
            // AI Messages
            const messages = [
                'Great form! Keep it up.',
                'Perfect alignment detected.',
                'Breathing looks steady.',
                'Excellent range of motion!',
                'Nice controlled movement.'
            ];
            const randomMessage = messages[Math.floor(Math.random() * messages.length)];
            document.getElementById('aiMessage').textContent = randomMessage;
        }
    }, 500);
}

function pauseSession() {
    appState.sessionActive = false;
    document.getElementById('pauseSessionBtn').style.display = 'none';
    document.getElementById('startSessionBtn').style.display = 'flex';
    showNotification('Session paused');
}

function exitSession() {
    appState.sessionActive = false;
    
    if (mediaStream) {
        mediaStream.getTracks().forEach(track => track.stop());
        mediaStream = null;
    }

    document.getElementById('videoElement').style.display = 'none';
    document.getElementById('cameraPlaceholder').style.display = 'flex';
    document.getElementById('pauseSessionBtn').style.display = 'none';
    document.getElementById('startSessionBtn').style.display = 'flex';
    
    // Save session data
    saveSessionData();
    
    showNotification('Session ended. Great work!');
    navigateToPage('dashboard');
}

function saveSessionData() {
    // In a real app, this would save to backend
    console.log('Saving session:', {
        reps: appState.repCount,
        duration: Date.now() - appState.sessionStartTime,
        exercise: document.getElementById('sessionExerciseName').textContent
    });
}

// ========== DASHBOARD ==========
function refreshDashboard() {
    // Update stats with animation
    updateDashboardStats();
}

function updateDashboardStats() {
    const stats = {
        totalSessions: 24,
        totalReps: 1240,
        avgQuality: 92,
        currentStreak: 12
    };

    // Animate stat cards
    document.querySelectorAll('.stat-card').forEach(card => {
        card.style.animation = 'none';
        setTimeout(() => {
            card.style.animation = 'fadeIn 0.5s ease';
        }, 10);
    });
}

// ========== CHARTS ==========
function setupCharts() {
    createActivityChart();
    createQualityChart();
    createROMChart();
    createTimeChart();
}

function createActivityChart() {
    const canvas = document.getElementById('activityChart');
    if (!canvas) return;

    new Chart(canvas, {
        type: 'bar',
        data: {
            labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
            datasets: [{
                label: 'Sessions',
                data: [5, 6, 4, 7, 8, 3, 2],
                backgroundColor: 'rgba(30, 136, 229, 0.5)',
                borderColor: '#1E88E5',
                borderWidth: 2,
                borderRadius: 8
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    display: false
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        stepSize: 2
                    }
                }
            }
        }
    });
}

function createQualityChart() {
    const canvas = document.getElementById('qualityChart');
    if (!canvas) return;

    new Chart(canvas, {
        type: 'line',
        data: {
            labels: ['Week 1', 'Week 2', 'Week 3', 'Week 4', 'Week 5'],
            datasets: [{
                label: 'Quality %',
                data: [75, 80, 85, 88, 92],
                borderColor: '#26C6DA',
                backgroundColor: 'rgba(38, 198, 218, 0.1)',
                borderWidth: 3,
                fill: true,
                tension: 0.4,
                pointRadius: 6,
                pointBackgroundColor: '#26C6DA',
                pointBorderColor: 'white',
                pointBorderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    display: true,
                    position: 'top'
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    max: 100
                }
            }
        }
    });
}

function createROMChart() {
    const canvas = document.getElementById('romChart');
    if (!canvas) return;

    new Chart(canvas, {
        type: 'radar',
        data: {
            labels: ['Shoulder', 'Knee', 'Hip', 'Elbow', 'Wrist', 'Ankle'],
            datasets: [{
                label: 'ROM (°)',
                data: [160, 120, 110, 140, 85, 45],
                borderColor: '#1E88E5',
                backgroundColor: 'rgba(30, 136, 229, 0.1)',
                borderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            scales: {
                r: {
                    beginAtZero: true,
                    max: 180
                }
            }
        }
    });
}

function createTimeChart() {
    const canvas = document.getElementById('timeChart');
    if (!canvas) return;

    new Chart(canvas, {
        type: 'line',
        data: {
            labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
            datasets: [{
                label: 'Session Duration (min)',
                data: [20, 25, 18, 30, 28, 15, 10],
                borderColor: '#43A047',
                backgroundColor: 'rgba(67, 160, 71, 0.1)',
                borderWidth: 3,
                fill: true,
                tension: 0.4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    display: false
                }
            }
        }
    });
}

// ========== CHATBOT ==========
function toggleChatbot() {
    const widget = document.getElementById('chatbotWidget');
    widget.classList.toggle('active');
    
    if (widget.classList.contains('active')) {
        document.getElementById('chatbotInput').focus();
    }
}

function sendChatMessage() {
    const input = document.getElementById('chatbotInput');
    const message = input.value.trim();

    if (!message) return;

    // Add user message
    addChatMessage(message, 'user');
    input.value = '';

    // Simulate bot response
    setTimeout(() => {
        const response = generateBotResponse(message);
        addChatMessage(response, 'bot');
    }, 600);
}

function addChatMessage(message, sender) {
    const messagesContainer = document.getElementById('chatbotMessages');
    const messageEl = document.createElement('div');
    messageEl.className = `message ${sender}-message`;
    
    const icon = sender === 'bot' 
        ? '<i class="fas fa-robot"></i>' 
        : '<i class="fas fa-user"></i>';
    
    messageEl.innerHTML = `
        ${icon}
        <div class="message-content">
            <p>${escapeHtml(message)}</p>
        </div>
    `;

    messagesContainer.appendChild(messageEl);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

function generateBotResponse(query) {
    const lowerQuery = query.toLowerCase();

    if (lowerQuery.includes('exercise')) {
        return 'Great question! We support 28+ exercises across all body parts. Start with your primary injury area and gradually progress. Would you like recommendations?';
    } else if (lowerQuery.includes('pain') || lowerQuery.includes('hurt')) {
        return 'Pain is important. Please exercise within your pain-free range of motion. If you experience sharp pain, stop immediately and consult your physician.';
    } else if (lowerQuery.includes('rep') || lowerQuery.includes('repetition')) {
        return 'Reps depend on your phase of recovery. Typically: Phase 1 (Weeks 1-2): 8-10 reps, Phase 2 (Weeks 3-4): 10-15 reps, Phase 3: 15-20 reps.';
    } else if (lowerQuery.includes('form') || lowerQuery.includes('posture')) {
        return 'Perfect form is crucial! Our AI tracks your posture in real-time. Make sure you\'re in front of the camera and follow the on-screen guidance for best results.';
    } else {
        return 'That\'s a great question! Our AI therapist recommends starting with light exercises and gradually increasing intensity. Would you like to begin a session?';
    }
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// ========== VOICE GUIDANCE ==========
function toggleVoice() {
    const btn = document.getElementById('voiceToggle');
    btn.classList.toggle('active');
    
    const isActive = btn.classList.contains('active');
    if (isActive) {
        btn.style.color = '#1E88E5';
        showNotification('Voice guidance enabled');
    } else {
        btn.style.color = '';
        showNotification('Voice guidance disabled');
    }
}

// ========== REHAB PLAN ==========
function showWeekPlan(week) {
    document.querySelectorAll('.week-plan').forEach(plan => {
        plan.classList.remove('active');
    });
    
    document.getElementById('week' + week).classList.add('active');
    
    // Update week button styles
    document.querySelectorAll('.week-btn').forEach(btn => {
        if (btn.dataset.week === week) {
            btn.style.background = '#1E88E5';
            btn.style.color = 'white';
            btn.style.borderColor = '#1E88E5';
        } else {
            btn.style.background = 'white';
            btn.style.color = 'inherit';
            btn.style.borderColor = 'var(--border-color)';
        }
    });
}

// ========== SETTINGS ==========
function saveSettings() {
    showNotification('Settings saved successfully!');
}

// ========== UTILITY FUNCTIONS ==========
function updateBreadcrumb(page) {
    const breadcrumbPath = {
        'home': 'Home',
        'dashboard': 'Dashboard',
        'exercises': 'Exercises',
        'exerciseSubtypes': 'Exercise Details',
        'session': 'Live Session',
        'reports': 'Reports',
        'rehabPlan': 'Rehab Plan',
        'settings': 'Settings',
        'login': 'Login',
        'register': 'Register'
    };

    document.getElementById('breadcrumb').innerHTML = breadcrumbPath[page] || 'Home';
}

function updateNavbarUser() {
    const userBtn = document.querySelector('.user-profile');
    if (userBtn) {
        userBtn.addEventListener('click', () => {
            navigateToPage('settings');
        });
    }
}

function toggleSidebar() {
    document.getElementById('sidebar').classList.toggle('collapsed');
    document.querySelector('.main-content').classList.toggle('expanded');
    document.querySelector('.topbar').classList.toggle('expanded');
}

function toggleMobileMenu() {
    const sidebar = document.getElementById('sidebar');
    sidebar.classList.toggle('active');
}

function showNotification(message, type = 'success') {
    const notification = document.getElementById('notification');
    const text = document.getElementById('notificationText');
    
    text.textContent = message;
    notification.style.display = 'flex';
    
    const iconMap = {
        'success': 'fas fa-check-circle',
        'error': 'fas fa-exclamation-circle',
        'warning': 'fas fa-exclamation-triangle',
        'info': 'fas fa-info-circle'
    };
    
    const icon = notification.querySelector('i');
    icon.className = iconMap[type] || iconMap['success'];
    
    setTimeout(() => {
        notification.style.display = 'none';
    }, 3000);
}

function logout() {
    if (confirm('Are you sure you want to logout?')) {
        appState.currentUser = null;
        navigateToPage('login');
        showNotification('Logged out successfully');
    }
}

// ========== LOCAL STORAGE ==========
function saveUserData() {
    localStorage.setItem('physioUserData', JSON.stringify(appState));
}

function loadUserData() {
    const data = localStorage.getItem('physioUserData');
    if (data) {
        Object.assign(appState, JSON.parse(data));
    }
}

// Animation on scroll
document.addEventListener('scroll', () => {
    document.querySelectorAll('.stat-card, .feature-card, .category-card').forEach(el => {
        const rect = el.getBoundingClientRect();
        if (rect.top < window.innerHeight - 100) {
            el.style.animation = 'fadeIn 0.5s ease';
        }
    });
});

// Close mobile menu when clicking nav items
document.addEventListener('click', (e) => {
    if (!e.target.closest('.sidebar') && !e.target.closest('.menu-toggle')) {
        const sidebar = document.getElementById('sidebar');
        if (sidebar.classList.contains('active')) {
            sidebar.classList.remove('active');
        }
    }
});

// Keyboard shortcuts
document.addEventListener('keydown', (e) => {
    // Ctrl/Cmd + / to open chatbot
    if ((e.ctrlKey || e.metaKey) && e.key === '/') {
        e.preventDefault();
        toggleChatbot();
    }
    
    // Escape to close chatbot
    if (e.key === 'Escape') {
        document.getElementById('chatbotWidget').classList.remove('active');
    }
});

console.log('PhysioMonitor Professional UI initialized successfully!');
