// IMMEDIATE TEST: Verify script.js is loading
console.log('✓ script.js is LOADED');

// Global variables
let currentUser = null;
let authToken = null;
let websocket = null;
let videoStream = null;
let currentExercise = null;
let currentCategory = null; // Track current category for navigation
let previousPage = null; // Track where user came from for smart back navigation
let pose = null; // MediaPipe Pose instance
let isDetecting = false; // Pose detection flag
let allSessionsData = []; // Store all sessions for filtering
let currentFilter = 'all'; // Track current filter

let selectedExercise = null; // Track selected exercise for session saving

let exerciseData = {
    reps: 0,
    angle: 0,
    quality: 0,
    posture: 'Correct'
};

// Exercise state tracking
let exerciseState = {
    reps: 0,
    currentPhase: null,
    angles: {},
    allAngles: [],  // Track all angles for averaging
    allQualityScores: [],  // Track all quality scores for averaging
    formFeedback: [],
    visibility: true,
    lastRepCountTime: 0,
    lastSpokenFeedback: '',
    lastFeedbackSpokenTime: 0,
    lastRepPhase: null,
    avgQualityScore: 0,
    totalDuration: 0,
    startTime: null,
    feedbackCooldown: 3000,  // Only speak feedback every 3 seconds minimum
    repCountDebounce: 1000,  // Minimum milliseconds between rep counts (increased from 500)
    exerciseType: null,
    lastPoseTime: 0,
    // Full-cycle tracking: require start→end→start→end for a rep
    cycleState: 'waiting_start',  // 'waiting_start' | 'in_start' | 'waiting_end' | 'in_end'
    phaseHoldFrames: 0,         // How many consecutive frames in the current phase
    phaseHoldRequired: 3,       // Must hold phase for 3 frames (~300ms) to confirm
    lastRawPhase: null           // Raw detected phase before stabilization
};

// Voice Assistant Mode (Text-to-Speech)
let voiceAssistant = {
    enabled: false,
    isSpeaking: false,
    currentUtterance: null,
    voiceSpeed: 0.9, // 0.5-2.0
    voicePitch: 1.0, // 0.5-2.0
    volume: 0.8, // 0-1
    voiceGender: 'female', // 'male' or 'female'
    lastSpokenTime: 0,
    minIntervalBetweenUtterances: 1000, // Minimum milliseconds between voice messages
    repCountSpoken: 0,
    lastFeedbackSpoken: '',
    synth: window.speechSynthesis || null
};

// API Configuration - IMPORTANT: Update this for production deployment
// For development (localhost): Auto-detects backend on port 8000
// For production (Vercel/deployed): Set window.API_BASE_URL BEFORE this script loads
// 
// PRODUCTION SETUP:
// 1. Deploy backend to Render/Railway (get URL like: https://your-backend.onrender.com)
// 2. Add to index.html BEFORE script.js loads:
//    <script>
//      window.API_BASE_URL = 'https://your-backend.onrender.com';
//    </script>
// 3. Or set via environment variable in deployment platform

function getAPIBaseURL() {
    // If explicitly set in environment/config
    if (typeof window.API_BASE_URL !== 'undefined' && window.API_BASE_URL) {
        console.log('🔗 Using configured API_BASE_URL:', window.API_BASE_URL);
        return window.API_BASE_URL;
    }
    
    // Auto-detect based on current location
    const hostname = window.location.hostname;
    const protocol = window.location.protocol;
    
    // If running on localhost, use localhost:8000
    if (hostname === 'localhost' || hostname === '127.0.0.1') {
        const url = `${protocol}//localhost:8000`;
        console.log('🔗 Development mode - using local backend:', url);
        return url;
    }
    
    // If deployed on Vercel or other platform, must have explicit config
    // Default to same domain (user should configure environment)
    console.warn('⚠️ Production environment detected but API_BASE_URL not configured!');
    console.warn('⚠️ Please set window.API_BASE_URL in environment or config before loading this script');
    console.log('Attempted hostname:', hostname);
    
    // Fallback to same domain (may not work without proper backend)
    return `${protocol}//${hostname}`;
}

const API_BASE = getAPIBaseURL();

// Initialize app
document.addEventListener('DOMContentLoaded', function () {
    console.log('🚀 Initializing Physiotherapy Monitoring System...');

    // Check MediaPipe availability immediately
    checkMediaPipeAvailability();

    initializeApp();
    setupEventListeners();
    checkAuthStatus();
});

function initializeApp() {
    console.log('📱 Initializing application...');

    // Load saved user data
    const savedUser = localStorage.getItem('currentUser');
    const savedToken = localStorage.getItem('authToken');

    if (savedUser && savedToken) {
        try {
            currentUser = JSON.parse(savedUser);
            authToken = savedToken;
            console.log('📱 Restored auth for user:', currentUser.username);
            updateUIForAuthenticatedUser();
            
            // Validate token is still valid (async, non-blocking)
            fetch(`${API_BASE}/users/me`, {
                headers: { 'Authorization': `Bearer ${authToken}` }
            }).then(resp => {
                if (!resp.ok) {
                    console.warn('📱 Stored token is expired/invalid');
                    showNotification('Your session has expired. Please log in again.', 'warning');
                    currentUser = null;
                    authToken = null;
                    localStorage.removeItem('currentUser');
                    localStorage.removeItem('authToken');
                    updateUIForLoggedOutUser();
                } else {
                    console.log('📱 Token validated successfully');
                    // Load dashboard data for the restored user
                    loadDashboardData();
                }
            }).catch(err => {
                console.warn('📱 Could not validate token (server may be down):', err.message);
            });
        } catch (e) {
            console.error('📱 Failed to restore auth:', e);
            localStorage.removeItem('currentUser');
            localStorage.removeItem('authToken');
        }
    } else {
        console.log('📱 No saved auth found - user is Guest');
    }
}

function setupEventListeners() {
    console.log('Setting up event listeners...');
    
    try {
        // Navigation
        document.querySelectorAll('.nav-item').forEach(link => {
            link.addEventListener('click', function (e) {
                e.preventDefault();
                const page = this.dataset.page;
                showPage(page);
            });
        });

        // Category cards
        document.querySelectorAll('.category-card').forEach(card => {
            card.addEventListener('click', function () {
                const category = this.dataset.category;
                loadCategoryExercises(category);
            });
        });

        // Auth buttons
        const loginBtn = document.getElementById('loginBtn');
        const logoutBtn = document.getElementById('logoutBtn');
        if (loginBtn) {
            loginBtn.addEventListener('click', showLoginModal);
            console.log('✓ Login button listener attached');
        } else {
            console.warn('⚠️ Login button not found');
        }
        if (logoutBtn) {
            logoutBtn.addEventListener('click', logout);
            console.log('✓ Logout button listener attached');
        } else {
            console.warn('⚠️ Logout button not found');
        }

        // Modal controls
        document.querySelectorAll('.modal-close').forEach(btn => {
            btn.addEventListener('click', closeModal);
        });

        const showRegisterBtn = document.getElementById('showRegister');
        if (showRegisterBtn) {
            showRegisterBtn.addEventListener('click', function (e) {
                e.preventDefault();
                closeModal();
                showRegisterModal();
            });
        }

        const showLoginBtn = document.getElementById('showLogin');
        if (showLoginBtn) {
            showLoginBtn.addEventListener('click', function (e) {
                e.preventDefault();
                closeModal();
                showLoginModal();
            });
        }

        // Camera control buttons
        const startBtn = document.getElementById('startBtn');
        const pauseBtn = document.getElementById('pauseBtn');
        const resetBtn = document.getElementById('resetBtn');

        if (startBtn) {
            startBtn.addEventListener('click', showStartReminder);
            console.log('✓ Start button listener attached');
        } else {
            console.warn('⚠️ Start button not found');
        }
        if (pauseBtn) {
            pauseBtn.addEventListener('click', pauseCamera);
            console.log('✓ Pause button listener attached');
        } else {
            console.warn('⚠️ Pause button not found');
        }
        if (resetBtn) {
            resetBtn.addEventListener('click', resetExercise);
            console.log('✓ Reset button listener attached');
        } else {
            console.warn('⚠️ Reset button not found');
        }

        // Close modals on outside click
        window.addEventListener('click', function (e) {
            if (e.target.classList && e.target.classList.contains('modal-overlay')) {
                closeModal();
            }
        });

        // Forms
        const loginForm = document.getElementById('loginForm');
        if (loginForm) {
            loginForm.addEventListener('submit', handleLogin);
            console.log('✓ Login form listener attached');
        }
        
        const registerForm = document.getElementById('registerForm');
        if (registerForm) {
            registerForm.addEventListener('submit', handleRegister);
            console.log('✓ Register form listener attached');
        }

        // Forgot Password
        const forgotPasswordLink = document.getElementById('forgotPasswordLink');
        if (forgotPasswordLink) {
            forgotPasswordLink.addEventListener('click', function(e) {
                e.preventDefault();
                // Hide login modal, show forgot password modal
                document.getElementById('loginModal').classList.remove('active');
                document.getElementById('forgotPasswordModal').classList.add('active');
                hideModalAlert('forgotAlert');
            });
            console.log('✓ Forgot password link listener attached');
        }

        const backToLogin = document.getElementById('backToLogin');
        if (backToLogin) {
            backToLogin.addEventListener('click', function(e) {
                e.preventDefault();
                document.getElementById('forgotPasswordModal').classList.remove('active');
                document.getElementById('loginModal').classList.add('active');
            });
            console.log('✓ Back to login link listener attached');
        }

        const forgotPasswordForm = document.getElementById('forgotPasswordForm');
        if (forgotPasswordForm) {
            forgotPasswordForm.addEventListener('submit', handleForgotPassword);
            console.log('✓ Forgot password form listener attached');
        }

        // Close forgot password modal on overlay click
        const forgotModal = document.getElementById('forgotPasswordModal');
        if (forgotModal) {
            forgotModal.addEventListener('click', function(e) {
                if (e.target === forgotModal) {
                    forgotModal.classList.remove('active');
                }
            });
        }

        // Chatbot
        const sendBtn = document.getElementById('sendBtn');
        if (sendBtn) {
            sendBtn.addEventListener('click', sendChatMessage);
            console.log('✓ Send button listener attached');
        }
        
        const chatInput = document.getElementById('chatInput');
        if (chatInput) {
            chatInput.addEventListener('keypress', function (e) {
                if (e.key === 'Enter') {
                    sendChatMessage();
                }
            });
            console.log('✓ Chat input listener attached');
        }
        
        // Debug panel toggle (Ctrl+Shift+D)
        document.addEventListener('keydown', function (e) {
            if (e.ctrlKey && e.shiftKey && e.key === 'D') {
                e.preventDefault();
                const debugPanel = document.getElementById('debugPanel');
                if (debugPanel) {
                    debugPanel.style.display = debugPanel.style.display === 'none' ? 'block' : 'none';
                    console.log('Debug panel toggled');
                }
            }
        });
        
        console.log('✅ All event listeners set up successfully');
    } catch (error) {
        console.error('Error setting up event listeners:', error);
    }
}

// Navigation
function showPage(pageName) {
    console.log(`Showing page: ${pageName}`);

    // Hide all pages
    document.querySelectorAll('.page').forEach(page => {
        page.classList.remove('active');
    });

    // Show selected page
    const targetPage = document.getElementById(pageName + 'Page');
    console.log(`Target page element:`, targetPage);

    if (targetPage) {
        targetPage.classList.add('active');
        console.log(`Page ${pageName} activated`);
    } else {
        console.error(`Page ${pageName} not found!`);
    }

    // Update nav links
    document.querySelectorAll('.nav-item').forEach(link => {
        link.classList.remove('active');
    });
    const activeLink = document.querySelector(`.nav-item[data-page="${pageName}"]`);
    if (activeLink) activeLink.classList.add('active');

    // Load page-specific data
    if (pageName === 'dashboard') {
        if (currentUser && authToken) {
            loadDashboardData();
        } else {
            console.log('Dashboard: user not authenticated, showing empty state');
        }
    } else if (pageName === 'reports') {
        loadReportsData();
    } else if (pageName === 'rehabPlan') {
        loadRehabPlanData();
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
    document.querySelectorAll('.modal-overlay').forEach(modal => {
        modal.classList.remove('active');
    });
}

async function handleLogin(e) {
    e.preventDefault();

    const formData = new FormData(e.target);
    const username = formData.get('username');
    const password = formData.get('password');

    // Client-side validation
    if (!username || username.length < 3) {
        showModalAlert('loginAlert', 'Username must be at least 3 characters', 'error');
        return;
    }
    if (!password || password.length < 6) {
        showModalAlert('loginAlert', 'Password must be at least 6 characters', 'error');
        return;
    }

    // Show loading state
    const submitBtn = document.getElementById('loginSubmitBtn');
    if (submitBtn) { submitBtn.classList.add('btn-loading'); submitBtn.querySelector('i').className = 'fas fa-spinner'; }
    hideModalAlert('loginAlert');

    try {
        console.log('🔐 Attempting login with API:', API_BASE);
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
            console.log('✅ Token received');

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
                document.getElementById('loginForm').reset();
                showNotification('Welcome back, ' + (currentUser.username || 'User') + '!', 'success');
                
                // Navigate to dashboard and load this user's data
                showPage('dashboard');
            }
        } else {
            const errorData = await response.json().catch(() => ({}));
            console.error('Login error response:', response.status, errorData);
            showModalAlert('loginAlert', errorData.detail || 'Invalid username or password. Please try again.', 'error');
        }
    } catch (error) {
        console.error('Login error:', error);
        showModalAlert('loginAlert', 'Connection error. Please check if the server is running.', 'error');
    } finally {
        if (submitBtn) { submitBtn.classList.remove('btn-loading'); submitBtn.querySelector('i').className = 'fas fa-sign-in-alt'; }
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
        showModalAlert('registerAlert', 'Username must be at least 3 characters long', 'error');
        return;
    }

    if (!userData.email || !userData.email.includes('@') || !userData.email.includes('.')) {
        showModalAlert('registerAlert', 'Please enter a valid email address', 'error');
        return;
    }

    if (!userData.password || userData.password.length < 6) {
        showModalAlert('registerAlert', 'Password must be at least 6 characters long', 'error');
        return;
    }

    if (userData.password.length > 72) {
        showModalAlert('registerAlert', 'Password must be less than 72 characters long', 'error');
        return;
    }

    // Show loading state
    const submitBtn = document.getElementById('registerSubmitBtn');
    if (submitBtn) { submitBtn.classList.add('btn-loading'); submitBtn.querySelector('i').className = 'fas fa-spinner'; }
    hideModalAlert('registerAlert');

    try {
        console.log('📝 Attempting registration with API:', API_BASE);
        const response = await fetch(`${API_BASE}/register`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                username: userData.username,
                email: userData.email,
                full_name: userData.full_name,
                password: userData.password
            })
        });

        if (response.ok) {
            const user = await response.json();
            console.log('✅ Registration successful');
            
            // Store only the username (never keep password in memory)
            const registeredUsername = userData.username;
            
            // Securely clear credentials from memory
            userData.password = '';
            userData = null;
            
            // Reset registration form completely
            document.getElementById('registerForm').reset();
            
            // Show success then switch to login
            closeModal();
            showNotification('Account created successfully! Please sign in.', 'success');
            setTimeout(() => {
                showLoginModal();
                // Pre-fill ONLY the username (never the password)
                setTimeout(() => {
                    // Reset login form first to clear any autofill
                    const loginForm = document.getElementById('loginForm');
                    if (loginForm) loginForm.reset();
                    
                    const loginUsername = document.getElementById('username');
                    if (loginUsername) loginUsername.value = registeredUsername;
                    
                    // Ensure password field is empty and type=password
                    const loginPassword = document.getElementById('password');
                    if (loginPassword) {
                        loginPassword.value = '';
                        loginPassword.type = 'password';
                    }
                    
                    showModalAlert('loginAlert', 'Account created! Sign in with your credentials.', 'success');
                }, 300);
            }, 500);
        } else {
            const errorData = await response.json().catch(() => ({}));
            console.error('Registration error response:', response.status, errorData);
            showModalAlert('registerAlert', errorData.detail || 'Registration failed. Username or email may already be taken.', 'error');
        }
    } catch (error) {
        console.error('Registration error:', error);
        showModalAlert('registerAlert', 'Connection error. Please check if the server is running.', 'error');
    } finally {
        if (submitBtn) { submitBtn.classList.remove('btn-loading'); submitBtn.querySelector('i').className = 'fas fa-user-plus'; }
    }
}

// Forgot Password handler
async function handleForgotPassword(e) {
    e.preventDefault();

    const username = document.getElementById('fpUsername').value.trim();
    const email = document.getElementById('fpEmail').value.trim();
    const newPassword = document.getElementById('fpNewPassword').value;
    const confirmPassword = document.getElementById('fpConfirmPassword').value;

    // Validation
    if (!username || username.length < 3) {
        showModalAlert('forgotAlert', 'Username must be at least 3 characters', 'error');
        return;
    }
    if (!email || !email.includes('@') || !email.includes('.')) {
        showModalAlert('forgotAlert', 'Please enter a valid email address', 'error');
        return;
    }
    if (!newPassword || newPassword.length < 6) {
        showModalAlert('forgotAlert', 'New password must be at least 6 characters', 'error');
        return;
    }
    if (newPassword !== confirmPassword) {
        showModalAlert('forgotAlert', 'Passwords do not match', 'error');
        return;
    }

    const submitBtn = document.getElementById('forgotSubmitBtn');
    if (submitBtn) { submitBtn.classList.add('btn-loading'); submitBtn.disabled = true; }
    hideModalAlert('forgotAlert');

    try {
        const response = await fetch(`${API_BASE}/reset-password`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, email, new_password: newPassword })
        });

        const data = await response.json();

        if (response.ok) {
            showModalAlert('forgotAlert', data.message || 'Password reset successful!', 'success');
            // After 2 seconds, switch back to login modal with username pre-filled
            setTimeout(() => {
                document.getElementById('forgotPasswordForm').reset();
                document.getElementById('forgotPasswordModal').classList.remove('active');
                document.getElementById('loginModal').classList.add('active');
                const loginUsername = document.querySelector('#loginForm input[name="username"]');
                if (loginUsername) loginUsername.value = username;
                const loginPassword = document.querySelector('#loginForm input[name="password"]');
                if (loginPassword) { loginPassword.value = ''; loginPassword.type = 'password'; }
            }, 2000);
        } else {
            showModalAlert('forgotAlert', data.detail || 'Password reset failed. Please check your details.', 'error');
        }
    } catch (error) {
        console.error('Password reset error:', error);
        showModalAlert('forgotAlert', 'Connection error. Please check if the server is running.', 'error');
    } finally {
        if (submitBtn) { submitBtn.classList.remove('btn-loading'); submitBtn.disabled = false; }
    }
}

// Modal alert helpers
function showModalAlert(id, message, type) {
    const el = document.getElementById(id);
    if (!el) return;
    const icon = type === 'error' ? 'fa-exclamation-circle' : 'fa-check-circle';
    el.className = 'modal-alert alert-' + type;
    el.innerHTML = `<i class="fas ${icon}"></i><span>${message}</span>`;
    el.style.display = 'flex';
}

function hideModalAlert(id) {
    const el = document.getElementById(id);
    if (el) el.style.display = 'none';
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

    // Clear all user-specific data from the DOM so next user doesn't see stale data
    clearAllUserData();

    updateUIForLoggedOutUser();
    showPage('home');
    showNotification('Logged out successfully', 'info');
}

function clearAllUserData() {
    // Reset in-memory session cache
    allSessionsData = [];

    // Dashboard stats
    const dashIds = ['totalSessions','totalReps','avgQuality','daysActive','currentStreak','totalDuration'];
    dashIds.forEach(id => { const el = document.getElementById(id); if (el) el.textContent = '0'; });
    const trendIds = ['trendSessions','trendReps','trendQuality','trendDays','trendStreak','trendDuration'];
    trendIds.forEach(id => { const el = document.getElementById(id); if (el) { el.className = 'sc-trend neutral'; el.innerHTML = '<i class="fas fa-minus"></i> No data'; } });

    // Dashboard body part stats
    const bodyPartStats = document.getElementById('bodyPartStats');
    if (bodyPartStats) bodyPartStats.innerHTML = '<div class="empty-state-sm"><i class="fas fa-person"></i><p>No exercise data yet.</p></div>';

    // Dashboard session list
    const sessionsList = document.getElementById('sessionsList');
    if (sessionsList) sessionsList.innerHTML = '<div class="empty-state"><i class="fas fa-clipboard-check"></i><p>No sessions yet. Start exercising to see your progress!</p></div>';

    // Dashboard charts
    if (window._weeklyChart) { window._weeklyChart.data.datasets[0].data = [0,0,0,0,0,0,0]; window._weeklyChart.update(); }
    if (window._qualityChart) { window._qualityChart.data.labels = []; window._qualityChart.data.datasets[0].data = []; window._qualityChart.update(); }

    // AI Insights
    const aiInsights = document.getElementById('aiInsightsBody');
    if (aiInsights) aiInsights.innerHTML = '<p>Complete exercises to receive AI-generated insights.</p>';

    // Reports page
    const rptIds = { rptTotalSessions: '--', rptDaysActive: '--', rptQualityAvg: '--' };
    Object.entries(rptIds).forEach(([id, val]) => { const el = document.getElementById(id); if (el) el.textContent = val; });
    ['rptWeeklyTrend','rptActiveTrend','rptQualityTrend'].forEach(id => { const el = document.getElementById(id); if (el) { el.className = 'rpt-trend'; el.innerHTML = '<i class="fas fa-minus"></i> No data yet'; } });
    const aiReportBody = document.getElementById('aiReportBody');
    if (aiReportBody) aiReportBody.innerHTML = '<div class="air-section"><h4>Executive Summary</h4><p>No session data available yet. Complete some exercises to generate your AI recovery report.</p></div>';

    // Destroy report charts
    if (typeof _recoveryChart !== 'undefined' && _recoveryChart) { _recoveryChart.destroy(); _recoveryChart = null; }
    if (typeof _distributionChart !== 'undefined' && _distributionChart) { _distributionChart.destroy(); _distributionChart = null; }

    // Rehab plan page — reset to selector
    const rehabSelector = document.getElementById('rehabSelector');
    const rehabResult = document.getElementById('rehabPlanResult');
    if (rehabSelector) rehabSelector.style.display = 'block';
    if (rehabResult) rehabResult.style.display = 'none';

    // Exercise performance table
    const perfTable = document.getElementById('exercisePerformanceBody');
    if (perfTable) perfTable.innerHTML = '';

    // Range of motion
    const romContainer = document.getElementById('rangeOfMotionBody');
    if (romContainer) romContainer.innerHTML = '';
}

function checkAuthStatus() {
    if (currentUser && authToken) {
        updateUIForAuthenticatedUser();
    } else {
        updateUIForLoggedOutUser();
    }
}

// Try to refresh authentication using stored credentials
async function tryRefreshAuth() {
    try {
        if (!authToken) return false;
        // Try using the existing token to get user info
        const response = await fetch(`${API_BASE}/users/me`, {
            headers: { 'Authorization': `Bearer ${authToken}` }
        });
        if (response.ok) {
            currentUser = await response.json();
            return true;
        }
        // Token is invalid - clear auth
        console.warn('Token validation failed, clearing auth');
        currentUser = null;
        authToken = null;
        localStorage.removeItem('currentUser');
        localStorage.removeItem('authToken');
        return false;
    } catch (e) {
        console.error('Auth refresh failed:', e);
        return false;
    }
}

function updateUIForAuthenticatedUser() {
    const loginBtn = document.getElementById('loginBtn');
    const registerNavBtn = document.getElementById('registerNavBtn');
    const logoutBtn = document.getElementById('logoutBtn');
    const topName = document.getElementById('topbarUserName');
    const sidebarName = document.querySelector('.sidebar-user-name');
    const sidebarRole = document.querySelector('.sidebar-user-role');

    if (loginBtn) loginBtn.style.display = 'none';
    if (registerNavBtn) registerNavBtn.style.display = 'none';
    if (logoutBtn) logoutBtn.style.display = 'flex';

    const displayName = currentUser.username || currentUser.full_name || 'User';
    if (topName) topName.textContent = displayName;
    if (sidebarName) sidebarName.textContent = displayName;
    if (sidebarRole) sidebarRole.textContent = 'Patient';
}

function updateUIForLoggedOutUser() {
    const loginBtn = document.getElementById('loginBtn');
    const registerNavBtn = document.getElementById('registerNavBtn');
    const logoutBtn = document.getElementById('logoutBtn');
    const topName = document.getElementById('topbarUserName');
    const sidebarName = document.querySelector('.sidebar-user-name');
    const sidebarRole = document.querySelector('.sidebar-user-role');

    if (loginBtn) loginBtn.style.display = 'flex';
    if (registerNavBtn) registerNavBtn.style.display = 'flex';
    if (logoutBtn) logoutBtn.style.display = 'none';

    if (topName) topName.textContent = 'Guest';
    if (sidebarName) sidebarName.textContent = 'Guest';
    if (sidebarRole) sidebarRole.textContent = 'Sign in to start';
}

// Exercises
let allExercisesData = []; // Store all exercises for filtering

async function loadAllExercises() {
    try {
        console.log('Loading all exercises...');
        currentCategory = null; // Clear category when viewing all exercises
        previousPage = 'allExercises'; // Track that we're in all exercises view
        const url = `${API_BASE}/exercises`;
        console.log(`Fetching: ${url}`);
        const response = await fetch(url);
        console.log(`Response status: ${response.status}`);

        if (response.ok) {
            const exercises = await response.json();
            console.log(`Loaded all exercises:`, exercises);
            allExercisesData = exercises;
            displayAllExercises(exercises);
            showPage('allExercises');
        } else {
            const errorText = await response.text();
            console.error(`Server error: ${response.status} - ${errorText}`);
            showNotification(`Failed to load exercises: ${response.status}`, 'error');
        }
    } catch (error) {
        console.error('Error loading all exercises:', error);
        showNotification('Failed to load exercises. Check console for details.', 'error');
    }
}

function displayAllExercises(exercises) {
    console.log(`Displaying ${exercises.length} exercises`);

    const exerciseList = document.getElementById('allExercisesList');
    if (!exerciseList) {
        console.error('All exercises list element not found');
        return;
    }

    exerciseList.innerHTML = '';

    if (!exercises || exercises.length === 0) {
        exerciseList.innerHTML = '<p>No exercises found.</p>';
        return;
    }

    // Group exercises by category
    const exercisesByCategory = {};
    exercises.forEach(exercise => {
        if (!exercisesByCategory[exercise.category]) {
            exercisesByCategory[exercise.category] = [];
        }
        exercisesByCategory[exercise.category].push(exercise);
    });

    // Display exercises by category
    Object.keys(exercisesByCategory).sort().forEach(category => {
        const categorySection = document.createElement('div');
        categorySection.className = 'category-section';
        categorySection.innerHTML = `
            <h2 class="category-title">${category} Exercises</h2>
            <div class="category-exercises">
                ${exercisesByCategory[category].map(exercise => `
                    <div class="exercise-item" data-category="${exercise.category}">
                        <h3>${exercise.name}</h3>
                        <p>${exercise.description || 'No description available'}</p>
                        <p><strong>Instructions:</strong> ${exercise.instructions || 'No instructions available'}</p>
                        <div class="exercise-meta">
                            <span class="category-tag">${exercise.category}</span>
                            <span class="target-reps">Target: ${exercise.target_reps} reps</span>
                        </div>
                        <div class="exercise-actions">
                            <button class="btn btn-demo" onclick="openDemoVideo('${exercise.name}')">
                                <i class="fas fa-film"></i> Demo Video
                            </button>
                            <button class="btn btn-primary" onclick="startExercise('${exercise.name}')">
                                <i class="fas fa-play"></i> Start Exercise
                            </button>
                        </div>
                    </div>
                `).join('')}
            </div>
        `;
        exerciseList.appendChild(categorySection);
    });
}

function filterExercises(button, category) {
    console.log(`Filtering exercises by: ${category}`);
    console.log(`Available exercises:`, allExercisesData);

    // Update active filter button
    document.querySelectorAll('.filter-chip').forEach(btn => {
        btn.classList.remove('active');
    });
    if (button) {
        button.classList.add('active');
    }

    // Filter exercises
    let filteredExercises = allExercisesData;
    if (category !== 'all') {
        filteredExercises = allExercisesData.filter(exercise => exercise.category === category);
    }

    console.log(`Filtered exercises for ${category}:`, filteredExercises);
    displayAllExercises(filteredExercises);
}

async function loadCategoryExercises(category) {
    try {
        console.log(`Loading exercises for category: ${category}`);
        currentCategory = category; // Store current category
        previousPage = 'exerciseList'; // Track that we're in category list view
        const response = await fetch(`${API_BASE}/exercises/category/${category}`);
        console.log(`Response status: ${response.status}`);

        if (response.ok) {
            const exercises = await response.json();
            console.log(`Loaded exercises:`, exercises);
            displayCategoryExercises(category, exercises);
            showPage('exerciseList');
        } else {
            const errorText = await response.text();
            console.error(`Server error: ${response.status} - ${errorText}`);
            showNotification(`Failed to load exercises: ${response.status}`, 'error');
        }
    } catch (error) {
        console.error('Error loading exercises:', error);
        showNotification('Failed to load exercises. Check console for details.', 'error');
    }
}

function displayCategoryExercises(category, exercises) {
    console.log(`Displaying ${exercises.length} exercises for category: ${category}`);

    const categoryTitle = document.getElementById('categoryTitle');
    if (categoryTitle) {
        categoryTitle.textContent = `${category} Exercises`;
    }

    const exerciseList = document.getElementById('exerciseList');
    if (!exerciseList) {
        console.error('Exercise list element not found');
        return;
    }

    exerciseList.innerHTML = '';

    if (!exercises || exercises.length === 0) {
        exerciseList.innerHTML = '<p>No exercises found for this category.</p>';
        return;
    }

    exercises.forEach(exercise => {
        const exerciseItem = document.createElement('div');
        exerciseItem.className = 'exercise-item';
        exerciseItem.innerHTML = `
            <h3>${exercise.name}</h3>
            <p>${exercise.description || 'No description available'}</p>
            <p><strong>Instructions:</strong> ${exercise.instructions || 'No instructions available'}</p>
            <div class="exercise-actions">
                <button class="btn btn-demo" onclick="openDemoVideo('${exercise.name}')">
                    <i class="fas fa-film"></i> Demo Video
                </button>
                <button class="btn btn-primary" onclick="startExercise('${exercise.name}')">
                    <i class="fas fa-play"></i> Start Exercise
                </button>
            </div>
        `;
        exerciseList.appendChild(exerciseItem);
    });
}

// ============================================================================
// DEMO VIDEO FEATURE
// ============================================================================

/**
 * Maps each exercise name to its demo video filename and posture tips.
 * Videos should be placed in: /static/demo_videos/<filename>
 */
const EXERCISE_DEMO_MAP = {
    // Neck
    'Neck Flexion':                { video: 'neck_flexion.mp4',         tips: ['Keep your back straight', 'Move slowly and controlled', 'Do not force the range of motion', 'Stop if you feel sharp pain'] },
    'Neck Extension':              { video: 'neck_extension.mp4',        tips: ['Sit or stand upright', 'Tilt head gently backward', 'Keep shoulders relaxed and down', 'Hold each position for 2–3 seconds'] },
    'Neck Rotation':               { video: 'neck_rotation.mp4',         tips: ['Rotate chin toward shoulder', 'Keep chin level — do not tilt', 'Move only as far as comfortable', 'Return to center slowly'] },

    // Shoulder
    'Shoulder Flexion':            { video: 'shoulder_flexion.mp4',      tips: ['Keep elbow straight', 'Raise arm forward to shoulder height', 'Do not hunch your shoulder', 'Lower slowly — control the descent'] },
    'Shoulder Extension':          { video: 'shoulder_extension.mp4',    tips: ['Keep elbow straight', 'Move arm behind your body', 'Keep trunk stable — do not lean', 'Hold at end range for 1–2 seconds'] },
    'Shoulder Abduction':          { video: 'shoulder_abduction.mp4',    tips: ['Raise arm out to the side', 'Keep elbow straight and palm down', 'Do not raise your shoulder blade', 'Stop at shoulder height or as advised'] },
    'Shoulder Adduction':          { video: 'shoulder_adduction.mp4',    tips: ['Bring arm across your body', 'Keep elbow straight', 'Keep the opposite shoulder still', 'Move slowly through full range'] },
    'Shoulder Internal Rotation':  { video: 'shoulder_internal_rotation.mp4', tips: ['Keep elbow at 90°', 'Rotate forearm toward your belly', 'Keep upper arm against your side', 'Move in a smooth arc'] },
    'Shoulder External Rotation':  { video: 'shoulder_external_rotation.mp4', tips: ['Keep elbow at 90°', 'Rotate forearm away from body', 'Keep upper arm against your side', 'Do not twist your trunk'] },

    // Elbow
    'Elbow Flexion':               { video: 'elbow_flexion.mp4',         tips: ['Keep your upper arm still', 'Bend elbow fully — touch shoulder if able', 'Supinate (palm up) for full range', 'Lower arm slowly back down'] },
    'Elbow Extension':             { video: 'elbow_extension.mp4',       tips: ['Start with elbow bent', 'Straighten arm fully', 'Do not lock the elbow forcefully', 'Keep a steady rhythm'] },

    // Wrist
    'Wrist Flexion':               { video: 'wrist_flexion.mp4',         tips: ['Keep forearm resting on a surface', 'Bend wrist downward as far as comfortable', 'Keep fingers relaxed', 'Hold 2 seconds at end range'] },
    'Wrist Extension':             { video: 'wrist_extension.mp4',       tips: ['Keep forearm supported', 'Raise hand upward', 'Keep fingers relaxed', 'Do not hold your breath'] },
    'Wrist Rotation':              { video: 'wrist_rotation.mp4',        tips: ['Keep elbow bent at 90°', 'Rotate palm up then down', 'Keep upper arm still', 'Move through full range without pain'] },

    // Hip
    'Hip Flexion':                 { video: 'hip_flexion.mp4',           tips: ['Lie on your back or stand upright', 'Raise knee toward your chest', 'Keep lower back flat — do not arch', 'Hold briefly at top'] },
    'Hip Extension':               { video: 'hip_extension.mp4',         tips: ['Lie face down or stand', 'Lift leg behind you without arching back', 'Squeeze glutes at the top', 'Lower slowly'] },
    'Hip Abduction':               { video: 'hip_abduction.mp4',         tips: ['Lie on your side or stand', 'Lift leg out to the side', 'Keep toes pointing forward — not up', 'Do not let hips tilt'] },
    'Hip Adduction':               { video: 'hip_adduction.mp4',         tips: ['Lie on your side', 'Lift lower leg to meet upper leg', 'Keep trunk still', 'Squeeze inner thigh at top'] },

    // Knee
    'Knee Flexion':                { video: 'knee_flexion.mp4',          tips: ['Lie face down or sit on edge of surface', 'Bend knee as far as comfortable', 'Do not rotate hip', 'Straighten back down slowly'] },
    'Knee Extension':              { video: 'knee_extension.mp4',        tips: ['Sit in a chair', 'Extend leg until straight', 'Tighten quad at the top', 'Lower slowly — do not drop your foot'] },

    // Ankle
    'Ankle Dorsiflexion':          { video: 'ankle_dorsiflexion.mp4',    tips: ['Sit with foot off the floor', 'Pull toes toward your shin', 'Keep heel still', 'Hold 2 seconds at top'] },
    'Ankle Plantarflexion':        { video: 'ankle_plantarflexion.mp4',  tips: ['Point toes away from shin', 'Keep foot in mid-line', 'Use a stretch band for resistance', 'Move slowly and fully'] },
    'Ankle Inversion':             { video: 'ankle_inversion.mp4',       tips: ['Sit comfortably', 'Turn sole of foot inward', 'Move only the ankle — do not twist knee', 'Hold 1–2 seconds'] },

    // Squats / Back
    'Squat':                       { video: 'squat.mp4',                 tips: ['Stand feet shoulder-width apart', 'Keep chest up and back straight', 'Push knees out over toes', 'Lower until thighs are parallel'] },
    'Wall Squat':                  { video: 'wall_squat.mp4',            tips: ['Back flat against wall', 'Slide down until knees at 90°', 'Keep feet in front of knees', 'Hold position as prescribed'] },
    'Mini Squat':                  { video: 'mini_squat.mp4',            tips: ['Bend knees only 20–30°', 'Keep back straight', 'Do not let knees cave inward', 'Rise slowly back up'] },
    'Sit to Stand':                { video: 'sit_to_stand.mp4',          tips: ['Sit at edge of chair', 'Lean slightly forward', 'Push through heels to stand', 'Control the sit-back movement'] },
    'Step Up':                     { video: 'step_up.mp4',               tips: ['Step fully onto the step', 'Drive through heel of lead foot', 'Keep trunk upright', 'Place trailing foot down gently'] },
    'Back Extension':              { video: 'back_extension.mp4',        tips: ['Lie face down, hands by shoulders', 'Lift chest off mat keeping hips down', 'Do not hyperextend — go pain-free range', 'Lower slowly'] },
};

/**
 * Build posture tips for an exercise, using the map or a generic fallback.
 */
function getDemoTips(exerciseName) {
    const entry = EXERCISE_DEMO_MAP[exerciseName];
    if (entry && entry.tips && entry.tips.length) return entry.tips;
    return [
        'Move slowly and in a controlled manner',
        'Stop if you experience sharp or increasing pain',
        'Breathe steadily throughout the movement',
        'Maintain correct posture at all times',
    ];
}

/**
 * Returns the video URL for a given exercise, or null if none mapped.
 * Videos are served via the backend's /static mount: <backend>/static/demo_videos/<file>
 */
function getDemoVideoUrl(exerciseName) {
    const entry = EXERCISE_DEMO_MAP[exerciseName];
    if (!entry || !entry.video) return null;
    // API_BASE already points at the backend (e.g. http://localhost:8001)
    return `${API_BASE}/static/demo_videos/${entry.video}`;
}

/** Tracks whether the user has viewed a demo for the current exercise this session. */
let _demoWatchedForExercise = {};

function openDemoVideo(exerciseName) {
    const modal = document.getElementById('demoVideoModal');
    const title = document.getElementById('demoModalTitle');
    const player = document.getElementById('demoVideoPlayer');
    const source = document.getElementById('demoVideoSource');
    const placeholder = document.getElementById('demoVideoPlaceholder');
    const placeholderMsg = document.getElementById('demoPlaceholderMsg');
    const tipsList = document.getElementById('demoTipsList');

    if (!modal) return;

    // Set title
    if (title) title.textContent = exerciseName + ' — Demo';

    // Set video or show placeholder
    const videoUrl = getDemoVideoUrl(exerciseName);
    if (videoUrl) {
        source.src = videoUrl;
        player.load();
        player.style.display = 'block';
        placeholder.style.display = 'none';
    } else {
        player.style.display = 'none';
        player.pause();
        source.src = '';
        placeholder.style.display = 'flex';
        if (placeholderMsg) placeholderMsg.textContent = `Demo video for "${exerciseName}" will be available soon.`;
    }

    // Render tips
    const tips = getDemoTips(exerciseName);
    if (tipsList) {
        tipsList.innerHTML = tips.map(t =>
            `<div class="demo-tip-pill"><i class="fas fa-check-circle"></i><span>${t}</span></div>`
        ).join('');
    }

    // Track that user opened demo for this exercise
    _demoWatchedForExercise[exerciseName] = true;

    // Store which exercise this demo belongs to (for "Start Exercise Now" button)
    modal.dataset.exercise = exerciseName || '';

    modal.classList.add('active');
    document.body.style.overflow = 'hidden';
}

function closeDemoVideo() {
    const modal = document.getElementById('demoVideoModal');
    const player = document.getElementById('demoVideoPlayer');
    if (player) { player.pause(); }
    if (modal) { modal.classList.remove('active'); }
    document.body.style.overflow = '';
}

function closeDemoAndStart() {
    const modal = document.getElementById('demoVideoModal');
    const exerciseName = modal ? modal.dataset.exercise : '';
    closeDemoVideo();
    if (exerciseName) {
        startExercise(exerciseName);
    }
}

function handleDemoModalBackdrop(event) {
    if (event.target === document.getElementById('demoVideoModal')) {
        closeDemoVideo();
    }
}

// ── Smart Start Reminder ──────────────────────────────────────────────
function showStartReminder() {
    // Only show reminder if user hasn't watched the demo for this exercise yet
    if (currentExercise && _demoWatchedForExercise[currentExercise]) {
        // Already watched — start directly
        startCamera();
        return;
    }
    const modal = document.getElementById('startReminderModal');
    const nameEl = document.getElementById('reminderExerciseName');
    if (nameEl) nameEl.textContent = currentExercise || 'this exercise';
    if (modal) {
        modal.classList.add('active');
        document.body.style.overflow = 'hidden';
    }
}

function closeReminderAndOpenDemo() {
    const modal = document.getElementById('startReminderModal');
    if (modal) modal.classList.remove('active');
    document.body.style.overflow = '';
    if (currentExercise) openDemoVideo(currentExercise);
}

function closeReminderAndStart() {
    const modal = document.getElementById('startReminderModal');
    if (modal) modal.classList.remove('active');
    document.body.style.overflow = '';
    startCamera();
}

function handleReminderBackdrop(event) {
    if (event.target === document.getElementById('startReminderModal')) {
        closeReminderAndStart();
    }
}

function startExercise(exerciseName) {
    currentExercise = exerciseName;
    document.getElementById('exerciseTitle').textContent = exerciseName;
    
    // Reset exercise state when switching exercises
    exerciseState.reps = 0;
    exerciseState.currentPhase = null;  // Set to null so first detected phase initializes it
    exerciseState.angles = {};
    exerciseState.allAngles = [];  // Reset angle tracking
    exerciseState.allQualityScores = [];  // Reset quality tracking
    exerciseState.avgQualityScore = 0;
    exerciseState.formFeedback = [];
    exerciseState.visibility = true;
    exerciseState.lastRepCountTime = 0;
    exerciseState.lastSpokenFeedback = '';
    exerciseState.lastFeedbackSpokenTime = 0;
    exerciseState.startTime = Date.now();  // Record start time
    exerciseState.cycleState = 'waiting_start';
    exerciseState.phaseHoldFrames = 0;
    exerciseState.lastRawPhase = null;
    
    // Reset rep counter display
    if (document.getElementById('repCount')) {
        document.getElementById('repCount').textContent = '0';
    }
    
    // Notify backend of exercise selection
    if (websocket && websocket.readyState === WebSocket.OPEN) {
        websocket.send(JSON.stringify({
            type: 'select_exercise',
            exercise_name: exerciseName
        }));
    }
    
    console.log(`✅ Started exercise: ${exerciseName} (Phase reset to null - will initialize on first frame)`);
    
    // Warn user if not logged in
    if (!currentUser || !authToken) {
        showNotification('You are not logged in. Exercise data will NOT be saved. Please log in to track your progress.', 'warning');
    }
    
    showPage('exercise');
}

// Exercise configuration for ALL exercise types
const EXERCISE_CONFIG = {
    // Neck exercises
    'Neck Flexion': { primaryAngle: 'neckFlex', optimalRange: [20, 45], repPhases: ['extended', 'flexed'] },
    'Neck Extension': { primaryAngle: 'neckFlex', optimalRange: [20, 45], repPhases: ['flexed', 'extended'] },
    'Neck Rotation': { primaryAngle: 'neckRotate', optimalRange: [30, 80], repPhases: ['center', 'rotated'] },
    
    // Shoulder exercises - ADJUSTED to realistic physiotherapy ranges
    'Shoulder Flexion': { primaryAngle: 'shoulder', optimalRange: [30, 120], repPhases: ['down', 'up'] },
    'Shoulder Extension': { primaryAngle: 'shoulder', optimalRange: [10, 60], repPhases: ['down', 'up'] },
    'Shoulder Abduction': { primaryAngle: 'shoulder', optimalRange: [30, 120], repPhases: ['down', 'up'] },
    'Shoulder Adduction': { primaryAngle: 'shoulder', optimalRange: [10, 60], repPhases: ['down', 'up'] },
    'Shoulder Internal Rotation': { primaryAngle: 'shoulderRotate', optimalRange: [50, 85], repPhases: ['external', 'internal'] },
    'Shoulder External Rotation': { primaryAngle: 'shoulderRotate', optimalRange: [0, 50], repPhases: ['internal', 'external'] },
    
    // Elbow exercises
    'Elbow Flexion': { primaryAngle: 'elbow', optimalRange: [70, 160], repPhases: ['extended', 'flexed'] },
    'Elbow Extension': { primaryAngle: 'elbow', optimalRange: [70, 160], repPhases: ['flexed', 'extended'] },
    
    // Knee exercises
    'Knee Flexion': { primaryAngle: 'knee', optimalRange: [40, 140], repPhases: ['extended', 'flexed'] },
    'Knee Extension': { primaryAngle: 'knee', optimalRange: [140, 180], repPhases: ['flexed', 'extended'] },
    
    // Hip exercises
    'Hip Abduction': { primaryAngle: 'hip', optimalRange: [20, 60], repPhases: ['neutral', 'abducted'] },
    'Hip Flexion': { primaryAngle: 'hip', optimalRange: [45, 90], repPhases: ['extended', 'flexed'] },
    
    // Wrist exercises
    'Wrist Flexion': { primaryAngle: 'wristFlex', optimalRange: [30, 80], repPhases: ['neutral', 'flexed'] },
    'Wrist Extension': { primaryAngle: 'wristFlex', optimalRange: [30, 80], repPhases: ['flexed', 'neutral'] },
    
    // Back exercises
    'Back Extension': { primaryAngle: 'backExtend', optimalRange: [10, 45], repPhases: ['neutral', 'extended'] },
    
    // Ankle exercises (movement-based, not angle-based)
    'Ankle Dorsiflexion': { primaryAngle: 'ankleAngle', optimalRange: [80, 120], repPhases: ['neutral', 'dorsiflexed'] },
    'Ankle Plantarflexion': { primaryAngle: 'ankleAngle', optimalRange: [90, 140], repPhases: ['dorsiflexed', 'plantarflexed'] },
    'Ankle Inversion': { primaryAngle: 'ankleRotate', optimalRange: [20, 60], repPhases: ['neutral', 'inverted'] },
    'Ankle Eversion': { primaryAngle: 'ankleRotate', optimalRange: [0, 45], repPhases: ['inverted', 'everted'] },
    'Ankle Circles': { primaryAngle: 'ankleRotate', optimalRange: [0, 360], repPhases: ['start', 'rotating'] },
    
    // Squat exercises
    'Body Weight Squat': { primaryAngle: 'knee', optimalRange: [60, 110], repPhases: ['up', 'down'] },
    'Wall Sit': { primaryAngle: 'knee', optimalRange: [80, 110], repPhases: ['standing', 'sitting'] },
    'Sumo Squat': { primaryAngle: 'knee', optimalRange: [60, 110], repPhases: ['up', 'down'] },
    'Partial Squat': { primaryAngle: 'knee', optimalRange: [100, 130], repPhases: ['up', 'down'] },
    'Squat Hold': { primaryAngle: 'knee', optimalRange: [70, 100], repPhases: ['holding', 'released'] }
};
let camera = null;


// Check MediaPipe availability
function checkMediaPipeAvailability() {
    console.log('Checking MediaPipe availability...');

    // Check if required MediaPipe objects are available
    if (typeof Pose === 'undefined') {
        console.error('❌ MediaPipe Pose not available');
        return false;
    }

    if (typeof Camera === 'undefined') {
        console.warn('⚠️ MediaPipe Camera not available (using fallback)');
    }

    if (typeof drawConnectors === 'undefined') {
        console.warn('⚠️ MediaPipe drawConnectors not available (using custom)');
    }

    if (typeof drawLandmarks === 'undefined') {
        console.warn('⚠️ MediaPipe drawLandmarks not available (using custom)');
    }

    console.log('✅ MediaPipe Pose is available');
    return true;
}

// Initialize MediaPipe Pose
async function initializePoseDetection() {
    return new Promise((resolve, reject) => {
        console.log('Creating MediaPipe Pose instance...');

        // Check MediaPipe availability first
        if (!checkMediaPipeAvailability()) {
            reject(new Error('MediaPipe not available'));
            return;
        }

        try {
            pose = new Pose({
                locateFile: (file) => {
                    console.log(`Loading MediaPipe file: ${file}`);
                    return `https://cdn.jsdelivr.net/npm/@mediapipe/pose/${file}`;
                }
            });

            pose.setOptions({
                modelComplexity: 1,
                smoothLandmarks: true,
                minDetectionConfidence: 0.5,
                minTrackingConfidence: 0.5
            });

            pose.onResults(onPoseResults);

            console.log('MediaPipe Pose created successfully');

            // Wait for pose to be ready
            setTimeout(() => {
                console.log('MediaPipe Pose initialized');
                resolve();
            }, 2000);

        } catch (error) {
            console.error('Error creating MediaPipe Pose:', error);
            reject(error);
        }
    });
}

// Skeleton drawing functions
function drawSkeleton(ctx, landmarks) {
    // PATTERN 2: Star Pattern - Wrist hub with radiating fingers (BEST for Physio)
    // Analyze hand positions for intelligent feedback
    const handAnalysis = analyzeHandPosition(landmarks);
    
    const bodyConnections = [
        [0, 1], [1, 2], [2, 3], [3, 7], [0, 4], [4, 5], [5, 6], [6, 8], // Face
        [9, 10], // Neck
        [11, 12], // Shoulders
        [11, 13], [13, 15], // Left arm
        [12, 14], [14, 16], // Right arm
        [11, 23], [12, 24], // Torso
        [23, 24], // Hips
        [23, 25], [25, 27], // Left leg
        [24, 26], [26, 28], // Right leg
    ];
    
    const leftHandConnections = [
        [15, 17], [15, 19], [15, 21],  // Left wrist to each finger
    ];
    
    const rightHandConnections = [
        [16, 18], [16, 20], [16, 22],  // Right wrist to each finger
    ];

    // Draw body skeleton in green
    ctx.strokeStyle = '#00FF00';
    ctx.lineWidth = 3;
    
    let drawnConnections = 0;

    bodyConnections.forEach(([start, end]) => {
        if (start >= landmarks.length || end >= landmarks.length) return;

        const startPoint = landmarks[start];
        const endPoint = landmarks[end];

        if (startPoint && endPoint &&
            startPoint.visibility > 0.5 && endPoint.visibility > 0.5) {
            try {
                ctx.beginPath();
                ctx.moveTo(startPoint.x * ctx.canvas.width, startPoint.y * ctx.canvas.height);
                ctx.lineTo(endPoint.x * ctx.canvas.width, endPoint.y * ctx.canvas.height);
                ctx.stroke();
                drawnConnections++;
            } catch (error) {
                console.error(`Error drawing connection [${start}, ${end}]:`, error);
            }
        }
    });
    
    // Draw left hand with intelligent color coding
    const leftHandColor = getHandLineColor(handAnalysis.leftHand, true);
    ctx.strokeStyle = leftHandColor;
    ctx.lineWidth = 3;
    
    leftHandConnections.forEach(([start, end]) => {
        if (start >= landmarks.length || end >= landmarks.length) return;

        const startPoint = landmarks[start];
        const endPoint = landmarks[end];

        if (startPoint && endPoint &&
            startPoint.visibility > 0.5 && endPoint.visibility > 0.5) {
            try {
                ctx.beginPath();
                ctx.moveTo(startPoint.x * ctx.canvas.width, startPoint.y * ctx.canvas.height);
                ctx.lineTo(endPoint.x * ctx.canvas.width, endPoint.y * ctx.canvas.height);
                ctx.stroke();
                drawnConnections++;
            } catch (error) {
                console.error(`Error drawing left hand [${start}, ${end}]:`, error);
            }
        }
    });
    
    // Draw right hand with intelligent color coding
    const rightHandColor = getHandLineColor(handAnalysis.rightHand, false);
    ctx.strokeStyle = rightHandColor;
    ctx.lineWidth = 3;
    
    rightHandConnections.forEach(([start, end]) => {
        if (start >= landmarks.length || end >= landmarks.length) return;

        const startPoint = landmarks[start];
        const endPoint = landmarks[end];

        if (startPoint && endPoint &&
            startPoint.visibility > 0.5 && endPoint.visibility > 0.5) {
            try {
                ctx.beginPath();
                ctx.moveTo(startPoint.x * ctx.canvas.width, startPoint.y * ctx.canvas.height);
                ctx.lineTo(endPoint.x * ctx.canvas.width, endPoint.y * ctx.canvas.height);
                ctx.stroke();
                drawnConnections++;
            } catch (error) {
                console.error(`Error drawing right hand [${start}, ${end}]:`, error);
            }
        }
    });
    
    console.log(`✓ Drew ${drawnConnections}/${bodyConnections.length + leftHandConnections.length + rightHandConnections.length} connections`);
    console.log(`✓ Hand status - Left: ${handAnalysis.leftHand.status} (${handAnalysis.leftHand.spread.toFixed(3)}), Right: ${handAnalysis.rightHand.status} (${handAnalysis.rightHand.spread.toFixed(3)})`);
}

function drawJointPoints(ctx, landmarks) {
    ctx.fillStyle = '#FF0000';
    
    let drawnPoints = 0;

    landmarks.forEach((landmark, index) => {
        if (landmark && landmark.visibility > 0.5) {
            try {
                ctx.beginPath();
                ctx.arc(
                    landmark.x * ctx.canvas.width,
                    landmark.y * ctx.canvas.height,
                    5,
                    0,
                    2 * Math.PI
                );
                ctx.fill();
                drawnPoints++;
            } catch (error) {
                console.error(`Error drawing joint point ${index}:`, error);
            }
        }
    });
    
    console.log(`✓ Drew ${drawnPoints}/${landmarks.length} joint points`);
}

// Hand analysis functions
function calculateHandSpread(wristIndex, fingerIndices, landmarks) {
    // Calculate average distance between wrist and fingers
    const wrist = landmarks[wristIndex];
    if (!wrist || wrist.visibility < 0.5) return 0;
    
    let totalDistance = 0;
    let validFingers = 0;
    
    fingerIndices.forEach(fingerIdx => {
        const finger = landmarks[fingerIdx];
        if (finger && finger.visibility > 0.5) {
            const dx = finger.x - wrist.x;
            const dy = finger.y - wrist.y;
            const distance = Math.sqrt(dx * dx + dy * dy);
            totalDistance += distance;
            validFingers++;
        }
    });
    
    return validFingers > 0 ? totalDistance / validFingers : 0;
}

function analyzeHandPosition(landmarks) {
    // Analyze both hands
    const leftWrist = 15;  // Left wrist landmark
    const rightWrist = 16; // Right wrist landmark
    const leftFingers = [17, 19, 21];  // Left finger tips
    const rightFingers = [18, 20, 22]; // Right finger tips
    
    const leftSpread = calculateHandSpread(leftWrist, leftFingers, landmarks);
    const rightSpread = calculateHandSpread(rightWrist, rightFingers, landmarks);
    
    // Thresholds (adjust based on camera distance)
    const HAND_OPEN_THRESHOLD = 0.08;  // Hand is open if spread > 0.08
    const HAND_CLOSED_THRESHOLD = 0.03; // Hand is closed if spread < 0.03
    
    return {
        leftHand: {
            spread: leftSpread,
            isOpen: leftSpread > HAND_OPEN_THRESHOLD,
            isClosed: leftSpread < HAND_CLOSED_THRESHOLD,
            status: leftSpread > HAND_OPEN_THRESHOLD ? 'open' : 
                    leftSpread < HAND_CLOSED_THRESHOLD ? 'closed' : 'partial'
        },
        rightHand: {
            spread: rightSpread,
            isOpen: rightSpread > HAND_OPEN_THRESHOLD,
            isClosed: rightSpread < HAND_CLOSED_THRESHOLD,
            status: rightSpread > HAND_OPEN_THRESHOLD ? 'open' : 
                    rightSpread < HAND_CLOSED_THRESHOLD ? 'closed' : 'partial'
        }
    };
}

function getHandLineColor(handStatus, isLeftHand) {
    // Return color based on hand position quality
    if (handStatus.isOpen) {
        return '#00FF00'; // Green = hand open (good form for most exercises)
    } else if (handStatus.isClosed) {
        return '#FFA500'; // Orange = hand closed (check form)
    } else {
        return '#FFFF00'; // Yellow = partially open (monitor)
    }
}

function updateHandFeedback(handAnalysis) {
    // NOTE: Hand feedback is now integrated into exercise-specific feedback
    // This function is kept for reference but posture feedback is managed by provideFormFeedback
    // Store hand analysis for quality scoring but don't override exercise feedback
}

// Exercise-specific posture feedback
function getExerciseSpecificFeedback(exerciseName, angles, phase) {
    const feedback = [];
    
    // Only provide hand feedback for exercises where it's relevant
    const handRelevantExercises = [
        'Wrist Flexion', 'Wrist Extension', 'Shoulder Internal Rotation', 
        'Shoulder External Rotation', 'Elbow Flexion', 'Elbow Extension'
    ];
    
    if (handRelevantExercises.includes(exerciseName) && window.currentHandAnalysis) {
        const hands = window.currentHandAnalysis;
        if (hands.leftHand.isClosed || hands.rightHand.isClosed) {
            feedback.push('✋ Keep hands open for proper form');
        }
    }
    
    // Exercise-specific form corrections
    switch(exerciseName) {
        case 'Neck Flexion':
            if (window.currentLandmarks) {
                const lm = window.currentLandmarks;
                if (lm[11] && lm[12]) {
                    const shoulderDiff = Math.abs(lm[11].y - lm[12].y);
                    if (shoulderDiff > 0.08) feedback.push('📍 Keep shoulders level');
                }
            }
            feedback.push('🔻 Bend head forward, tuck chin');
            break;
            
        case 'Neck Extension':
            feedback.push('🔺 Extend head backward smoothly');
            if (window.currentLandmarks) {
                const lm = window.currentLandmarks;
                if (lm[11] && lm[12]) {
                    const shoulderDiff = Math.abs(lm[11].y - lm[12].y);
                    if (shoulderDiff > 0.08) feedback.push('📍 Keep shoulders level');
                }
            }
            break;
            
        case 'Neck Rotation':
            feedback.push('↔️ Turn head side to side evenly');
            if (angles.neckRotateLeft && angles.neckRotateRight) {
                const diff = Math.abs(angles.neckRotateLeft - angles.neckRotateRight);
                if (diff > 10) feedback.push('⚖️ Balance rotation on both sides');
            }
            break;
            
        case 'Shoulder Flexion':
            feedback.push('👐 Keep arms straight, raise forward');
            if (window.currentLandmarks) {
                const lm = window.currentLandmarks;
                if (lm[11] && lm[12]) {
                    const shoulderDiff = Math.abs(lm[11].y - lm[12].y);
                    if (shoulderDiff > 0.12) feedback.push('📍 Keep shoulders level');
                }
            }
            break;
            
        case 'Shoulder Extension':
            feedback.push('👐 Pull arms backward, keep chest open');
            break;
            
        case 'Shoulder Abduction':
            feedback.push('👐 Raise arms out to sides to shoulder level');
            break;
            
        case 'Shoulder Adduction':
            feedback.push('🤝 Bring arms across body in controlled motion');
            break;
            
        case 'Shoulder Internal Rotation':
            feedback.push('🔄 Rotate forearm inward across body');
            break;
            
        case 'Shoulder External Rotation':
            feedback.push('🔄 Rotate forearm outward away from body');
            break;
            
        case 'Elbow Flexion':
            feedback.push('💪 Bend elbow bringing hand toward shoulder');
            if (angles.elbowLeft && angles.elbowRight) {
                const diff = Math.abs(angles.elbowLeft - angles.elbowRight);
                if (diff > 15) feedback.push('⚖️ Balance both arms equally');
            }
            break;
            
        case 'Elbow Extension':
            feedback.push('💪 Straighten arm fully, tricep focus');
            break;
            
        case 'Knee Flexion':
            feedback.push('🦵 Bend knee bringing foot toward hamstring');
            if (window.currentLandmarks) {
                const lm = window.currentLandmarks;
                if (lm[23] && lm[24]) {
                    const hipDiff = Math.abs(lm[23].y - lm[24].y);
                    if (hipDiff > 0.12) feedback.push('📍 Keep hips level');
                }
            }
            break;
            
        case 'Knee Extension':
            feedback.push('🦵 Straighten leg fully, quad contraction');
            break;
            
        case 'Hip Abduction':
            feedback.push('🦵 Lift leg out to side, keep upper body still');
            if (window.currentLandmarks) {
                const lm = window.currentLandmarks;
                if (lm[11] && lm[12]) {
                    const shoulderDiff = Math.abs(lm[11].y - lm[12].y);
                    if (shoulderDiff > 0.12) feedback.push('📍 Don\'t lean, keep trunk stable');
                }
            }
            break;
            
        case 'Hip Flexion':
            feedback.push('🦵 Bring knee toward chest, controlled motion');
            break;
            
        case 'Wrist Flexion':
            feedback.push('✋ Bend wrist downward, keep forearm stable');
            if (window.currentHandAnalysis) {
                const hands = window.currentHandAnalysis;
                if (hands.leftHand.isClosed || hands.rightHand.isClosed) {
                    feedback.push('✋ Keep fingers extended');
                }
            }
            break;
            
        case 'Wrist Extension':
            feedback.push('✋ Bend wrist upward, keep forearm stable');
            break;
            
        case 'Back Extension':
            feedback.push('🔄 Arch back slightly, engage core');
            if (window.currentLandmarks) {
                const lm = window.currentLandmarks;
                if (lm[11] && lm[12] && lm[23] && lm[24]) {
                    const shoulderDiff = Math.abs(lm[11].y - lm[12].y);
                    const hipDiff = Math.abs(lm[23].y - lm[24].y);
                    if (shoulderDiff > 0.12 || hipDiff > 0.12) {
                        feedback.push('📍 Keep body alignment straight');
                    }
                }
            }
            break;
            
        case 'Ankle Dorsiflexion':
            feedback.push('🦶 Pull toes upward toward shin');
            break;
            
        case 'Ankle Plantarflexion':
            feedback.push('🦶 Point toes downward and away');
            break;
            
        case 'Ankle Inversion':
            feedback.push('🦶 Turn sole of foot inward');
            break;
            
        case 'Ankle Eversion':
            feedback.push('🦶 Turn sole of foot outward');
            break;
            
        case 'Ankle Circles':
            feedback.push('⭕ Rotate ankle in full circles');
            break;
            
        case 'Body Weight Squat':
            feedback.push('🏋️ Lower hips back and down, knees over toes');
            if (window.currentLandmarks) {
                const lm = window.currentLandmarks;
                // Check knee tracking over ankle
                if (lm[25] && lm[27] && lm[29]) {
                    const kneeX = lm[27].x;
                    const ankleX = lm[29].x;
                    if (Math.abs(kneeX - ankleX) > 0.15) feedback.push('📍 Knees over ankles');
                }
                // Check if hips level
                if (lm[23] && lm[24]) {
                    const hipDiff = Math.abs(lm[23].y - lm[24].y);
                    if (hipDiff > 0.1) feedback.push('📍 Keep hips level');
                }
            }
            break;
            
        case 'Wall Sit':
            feedback.push('🚪 Slide back against wall, knees 90°');
            break;
            
        case 'Sumo Squat':
            feedback.push('🏋️ Wide stance squat, toes 45° out');
            if (window.currentLandmarks) {
                const lm = window.currentLandmarks;
                if (lm[23] && lm[24]) {
                    const hipDiff = Math.abs(lm[23].y - lm[24].y);
                    if (hipDiff > 0.1) feedback.push('📍 Keep hips level');
                }
            }
            break;
            
        case 'Partial Squat':
            feedback.push('🏋️ Shallow squat, light bending');
            if (window.currentLandmarks) {
                const lm = window.currentLandmarks;
                if (lm[25] && lm[27] && lm[29]) {
                    const kneeX = lm[27].x;
                    const ankleX = lm[29].x;
                    if (Math.abs(kneeX - ankleX) > 0.15) feedback.push('📍 Knees aligned over ankles');
                }
            }
            break;
            
        case 'Squat Hold':
            feedback.push('🏋️ Hold squat position, maintain posture');
            if (window.currentLandmarks) {
                const lm = window.currentLandmarks;
                if (lm[11] && lm[12]) {
                    const shoulderDiff = Math.abs(lm[11].y - lm[12].y);
                    if (shoulderDiff > 0.1) feedback.push('📍 Keep shoulders level and back straight');
                }
            }
            break;
    }
    
    return feedback;
}

// Process pose detection results
function onPoseResults(results) {
    if (!isDetecting) return;

    const canvas = document.getElementById('overlayCanvas');
    if (!canvas) {
        console.error('❌ Canvas element not found');
        return;
    }

    const canvasCtx = canvas.getContext('2d');
    if (!canvasCtx) {
        console.error('❌ Failed to get canvas 2d context');
        return;
    }

    // Set canvas size to match video
    const video = document.getElementById('videoElement');
    if (!video) {
        console.error('❌ Video element not found');
        return;
    }

    canvas.width = video.videoWidth || 640;
    canvas.height = video.videoHeight || 480;
    
    // Ensure canvas is visible
    if (canvas.style.display === 'none') {
        canvas.style.display = 'block';
        console.log('⚠️ Canvas was hidden, made visible');
    }
    
    // Check computed style
    const computedStyle = window.getComputedStyle(canvas);
    if (computedStyle.display === 'none' || computedStyle.visibility === 'hidden') {
        console.warn('⚠️ Canvas is hidden by CSS:', {
            display: computedStyle.display,
            visibility: computedStyle.visibility,
            opacity: computedStyle.opacity
        });
    }
    
    console.log(`✓ Canvas size: ${canvas.width}x${canvas.height}, Video size: ${video.videoWidth}x${video.videoHeight}`);

    // Clear canvas
    canvasCtx.save();
    canvasCtx.clearRect(0, 0, canvas.width, canvas.height);

    // Draw pose landmarks and connections
    if (results.poseLandmarks && results.poseLandmarks.length > 0) {
        console.log(`✓ Drawing skeleton with ${results.poseLandmarks.length} landmarks`);

        // Draw connections (skeleton lines) manually
        try {
            drawSkeleton(canvasCtx, results.poseLandmarks);
            console.log('✓ Skeleton drawn');
        } catch (error) {
            console.error('❌ Error drawing skeleton:', error);
        }

        // Draw landmarks (joint points) manually
        try {
            drawJointPoints(canvasCtx, results.poseLandmarks);
            console.log('✓ Joint points drawn');
        } catch (error) {
            console.error('❌ Error drawing joint points:', error);
        }

        // Analyze hand position and update feedback
        try {
            const handAnalysis = analyzeHandPosition(results.poseLandmarks);
            window.currentHandAnalysis = handAnalysis; // Store for quality scoring and exercise-specific feedback
            // Note: Hand feedback is now integrated into exercise-specific feedback
            console.log('✓ Hand analysis complete');
        } catch (error) {
            console.error('❌ Error analyzing hand position:', error);
        }

        // Store landmarks for ML processing
        window.currentLandmarks = results.poseLandmarks;

        // Process exercise detection
        processExerciseDetection(results.poseLandmarks);
    } else {
        console.log('⚠️ No landmarks detected');
        window.currentLandmarks = null;
    }

    canvasCtx.restore();
}

// Exercise detection and analysis
function processExerciseDetection(landmarks) {
    const currentTime = Date.now();
    if (currentTime - exerciseState.lastPoseTime < 100) return; // Process every 100ms
    exerciseState.lastPoseTime = currentTime;

    console.log('Processing exercise detection with landmarks:', landmarks.length);

    // CHECK: Are required landmarks visible for current exercise?
    if (!areLandmarksVisibleForExercise(landmarks, currentExercise)) {
        console.warn(`❌ Required landmarks not visible for ${currentExercise}. Reps not counted.`);
        exerciseState.angles = {};
        exerciseState.visibility = false;
        updateExerciseUI({}, 'ready');
        return;
    }
    
    exerciseState.visibility = true;

    // Calculate key joint angles
    const angles = calculateJointAngles(landmarks);
    exerciseState.angles = angles;
    
    // Track angles for averaging
    if (angles && Object.keys(angles).length > 0) {
        // Get primary angle for this exercise
        let primaryAngle = 0;
        if (currentExercise.includes('Shoulder')) {
            primaryAngle = angles['shoulder'] || angles['right_shoulder'] || 0;
        } else if (currentExercise.includes('Elbow')) {
            primaryAngle = angles['elbow'] || angles['right_elbow'] || 0;
        } else if (currentExercise.includes('Knee')) {
            primaryAngle = angles['knee'] || angles['right_knee'] || 0;
        } else if (currentExercise.includes('Hip')) {
            primaryAngle = angles['hip'] || angles['right_hip'] || 0;
        } else if (currentExercise.includes('Ankle')) {
            primaryAngle = angles['ankle'] || angles['right_ankle'] || 0;
        } else if (currentExercise.includes('Neck')) {
            primaryAngle = angles['neck'] || angles['neck_rotation'] || 0;
        } else if (currentExercise.includes('Wrist')) {
            primaryAngle = angles['wrist'] || angles['right_wrist'] || 0;
        }
        
        if (primaryAngle > 0) {
            exerciseState.allAngles.push(primaryAngle);
        }
    }

    // Detect exercise type and phase
    const exerciseType = detectExerciseType(angles);
    const phase = detectExercisePhase(angles, currentExercise);  // Use currentExercise directly

    // Count reps and provide feedback - always do this for the current exercise
    if (currentExercise) {
        countReps(phase);
        provideFormFeedback(angles, currentExercise, phase);  // Use currentExercise instead of detected type
    }

    // Update UI
    updateExerciseUI(angles, phase);

    // Store landmarks for backend processing
    window.currentLandmarks = landmarks;
}

// Check if landmark is visible (has sufficient confidence)
function isLandmarkVisible(landmark, confidenceThreshold = 0.5) {
    return landmark && landmark.visibility !== undefined && landmark.visibility > confidenceThreshold;
}

// Check if required landmarks for an exercise are visible
function areLandmarksVisibleForExercise(landmarks, exerciseName) {
    // Define required landmarks for each exercise type
    const requiredLandmarks = {
        // Neck exercises: need head/neck visible
        'Neck Flexion': [0, 1], // Nose and eyes
        'Neck Extension': [0, 1],
        'Neck Rotation': [0, 1],
        
        // Shoulder exercises: need shoulders and elbows only (vertical reference calculated)
        'Shoulder Flexion': [11, 12, 13, 14],
        'Shoulder Abduction': [11, 12, 13, 14],
        'Shoulder Extension': [11, 12, 13, 14],
        'Shoulder Rotation': [11, 12, 13, 14],
        
        // Elbow exercises: need elbows and wrists
        'Elbow Flexion': [11, 12, 13, 14, 15, 16], // Shoulders, elbows, wrists
        'Elbow Extension': [11, 12, 13, 14, 15, 16],
        
        // Wrist exercises: need wrists
        'Wrist Flexion': [15, 16],
        'Wrist Extension': [15, 16],
        
        // Knee exercises: need knees
        'Knee Flexion': [25, 26, 27, 28],
        'Knee Extension': [25, 26, 27, 28],
        
        // Hip exercises: need hips
        'Hip Abduction': [23, 24, 25, 26, 27, 28],
        'Hip Flexion': [23, 24, 25, 26, 27, 28],
        
        // Ankle exercises
        'Ankle Dorsiflexion': [27, 28, 31, 32], // Knees, ankles, feet
        'Ankle Plantarflexion': [27, 28, 31, 32],
        'Ankle Inversion': [27, 28, 31, 32],
        'Ankle Eversion': [27, 28, 31, 32],
        'Ankle Rotation': [27, 28, 31, 32],
        
        // Back exercises
        'Back Extension': [11, 12, 23, 24], // Shoulders, hips
        
        // Body weight squat
        'Body Weight Squat': [23, 24, 25, 26, 27, 28], // Full legs
        'Wall Sit': [23, 24, 25, 26, 27, 28], // Full legs
        'Sumo Squat': [23, 24, 25, 26, 27, 28], // Full legs
        'Partial Squat': [23, 24, 25, 26, 27, 28], // Full legs
        'Squat Hold': [23, 24, 25, 26, 27, 28] // Full legs
    };
    
    const required = requiredLandmarks[exerciseName] || [];
    
    if (required.length === 0) {
        console.warn(`⚠️ No visibility check defined for ${exerciseName}`);
        return true; // Allow if not defined
    }
    
    // Different confidence thresholds for different landmark types
    // Hip landmarks (23, 24) are body reference and can have lower visibility
    // Joint landmarks (11, 12, 13, 14, 25, 26, 27, 28) need higher visibility
    for (const idx of required) {
        const isHipLandmark = [23, 24].includes(idx);
        const threshold = isHipLandmark ? 0.3 : 0.5;  // Lower threshold for hip body reference
        
        if (!landmarks[idx]) {
            console.debug(`❌ Required landmark missing: ${idx} for ${exerciseName}`);
            return false;
        }
        
        if (!isLandmarkVisible(landmarks[idx], threshold)) {
            console.debug(`❌ Required landmark has low visibility: ${idx} (threshold: ${threshold}) for ${exerciseName}`);
            return false;
        }
    }
    
    return true;
}

// Calculate joint angles
function calculateJointAngles(landmarks) {
    const angles = {};

    // Helper function to calculate angle between three points
    const calculateAngle = (p1, p2, p3) => {
        if (!p1 || !p2 || !p3) return null;
        
        // Check that landmarks have valid coordinates (don't need high visibility for body reference points)
        if (!p1.x || !p1.y || !p2.x || !p2.y || !p3.x || !p3.y) {
            return null;
        }

        // For main joint (p2), ensure it has reasonable visibility
        // For reference points (p1, p3), use coordinates even if visibility is lower
        if (isLandmarkVisible(p2, 0.3) === false) {
            return null;
        }

        // Calculate vectors
        const v1 = { x: p1.x - p2.x, y: p1.y - p2.y };
        const v2 = { x: p3.x - p2.x, y: p3.y - p2.y };

        // Calculate angle using dot product
        const dot = v1.x * v2.x + v1.y * v2.y;
        const det = v1.x * v2.y - v1.y * v2.x;

        let angle = Math.atan2(det, dot);
        angle = Math.abs(angle) * (180 / Math.PI);

        // Ensure angle is in valid range
        if (angle > 180) angle = 360 - angle;

        return angle;
    };

    // Shoulder angles (for arm exercises)
    // Calculate angle of arm relative to vertical (downward direction)
    // Arm down = 0°, arm horizontal = 90°, arm overhead = 180°
    if (landmarks[11] && landmarks[13]) {
        // Left arm: vector from shoulder to elbow
        const armVec = { x: landmarks[13].x - landmarks[11].x, y: landmarks[13].y - landmarks[11].y };
        const verticalVec = { x: 0, y: 1 };  // Downward direction
        
        const dot = armVec.x * verticalVec.x + armVec.y * verticalVec.y;
        const det = armVec.x * verticalVec.y - armVec.y * verticalVec.x;
        
        let angle = Math.atan2(det, dot);
        angle = Math.abs(angle) * (180 / Math.PI);
        
        if (angle > 180) angle = 360 - angle;
        angles.shoulderLeft = angle;
        console.log(`👈 Left shoulder: vec(${armVec.x.toFixed(2)}, ${armVec.y.toFixed(2)}) -> angle: ${angle.toFixed(1)}°`);
    }
    if (landmarks[12] && landmarks[14]) {
        // Right arm: vector from shoulder to elbow
        const armVec = { x: landmarks[14].x - landmarks[12].x, y: landmarks[14].y - landmarks[12].y };
        const verticalVec = { x: 0, y: 1 };  // Downward direction
        
        const dot = armVec.x * verticalVec.x + armVec.y * verticalVec.y;
        const det = armVec.x * verticalVec.y - armVec.y * verticalVec.x;
        
        let angle = Math.atan2(det, dot);
        angle = Math.abs(angle) * (180 / Math.PI);
        
        if (angle > 180) angle = 360 - angle;
        angles.shoulderRight = angle;
        console.log(`👉 Right shoulder: vec(${armVec.x.toFixed(2)}, ${armVec.y.toFixed(2)}) -> angle: ${angle.toFixed(1)}°`);
    }

    // Shoulder rotation angles
    if (landmarks[11] && landmarks[13] && landmarks[15]) {
        angles.shoulderRotateLeft = calculateAngle(
            landmarks[13], landmarks[11], landmarks[15]
        );
    }
    if (landmarks[12] && landmarks[14] && landmarks[16]) {
        angles.shoulderRotateRight = calculateAngle(
            landmarks[14], landmarks[12], landmarks[16]
        );
    }

    // Elbow angles (forearm angle relative to vertical - like shoulder method)
    // Arm extended = 0°, arm bent = 90°, arm fully flexed = 170°
    if (landmarks[13] && landmarks[15]) {
        // Left forearm: vector from elbow to wrist
        const forearmVec = { x: landmarks[15].x - landmarks[13].x, y: landmarks[15].y - landmarks[13].y };
        const verticalVec = { x: 0, y: 1 };  // Downward direction
        
        const dot = forearmVec.x * verticalVec.x + forearmVec.y * verticalVec.y;
        const det = forearmVec.x * verticalVec.y - forearmVec.y * verticalVec.x;
        
        let angle = Math.atan2(det, dot);
        angle = Math.abs(angle) * (180 / Math.PI);
        
        if (angle > 180) angle = 360 - angle;
        angles.elbowLeft = angle;
    }
    if (landmarks[14] && landmarks[16]) {
        // Right forearm: vector from elbow to wrist
        const forearmVec = { x: landmarks[16].x - landmarks[14].x, y: landmarks[16].y - landmarks[14].y };
        const verticalVec = { x: 0, y: 1 };  // Downward direction
        
        const dot = forearmVec.x * verticalVec.x + forearmVec.y * verticalVec.y;
        const det = forearmVec.x * verticalVec.y - forearmVec.y * verticalVec.x;
        
        let angle = Math.atan2(det, dot);
        angle = Math.abs(angle) * (180 / Math.PI);
        
        if (angle > 180) angle = 360 - angle;
        angles.elbowRight = angle;
    }

    // Hip angles
    if (landmarks[11] && landmarks[23] && landmarks[25]) {
        angles.hipLeft = calculateAngle(
            { x: landmarks[11].x, y: landmarks[11].y - 0.2 },
            landmarks[23],
            landmarks[25]
        );
    }
    if (landmarks[12] && landmarks[24] && landmarks[26]) {
        angles.hipRight = calculateAngle(
            { x: landmarks[12].x, y: landmarks[12].y - 0.2 },
            landmarks[24],
            landmarks[26]
        );
    }

    // Knee angles (shin angle relative to vertical)
    // Leg straight = 0°, leg bent at 90° = 90°, fully bent = 140°+
    if (landmarks[25] && landmarks[27]) {
        // Left leg: vector from knee to ankle
        const shinVec = { x: landmarks[27].x - landmarks[25].x, y: landmarks[27].y - landmarks[25].y };
        
        // Normalize the vector
        const len = Math.sqrt(shinVec.x * shinVec.x + shinVec.y * shinVec.y);
        if (len === 0) {
            angles.kneeLeft = null;
        } else {
            const normalized = { x: shinVec.x / len, y: shinVec.y / len };
            const verticalVec = { x: 0, y: 1 };  // Downward direction
            
            const dot = normalized.x * verticalVec.x + normalized.y * verticalVec.y;
            const det = normalized.x * verticalVec.y - normalized.y * verticalVec.x;
            
            let angle = Math.atan2(det, dot);
            angle = Math.abs(angle) * (180 / Math.PI);
            
            if (angle > 180) angle = 360 - angle;
            angles.kneeLeft = angle;
        }
    }
    if (landmarks[26] && landmarks[28]) {
        // Right leg: vector from knee to ankle
        const shinVec = { x: landmarks[28].x - landmarks[26].x, y: landmarks[28].y - landmarks[26].y };
        
        // Normalize the vector
        const len = Math.sqrt(shinVec.x * shinVec.x + shinVec.y * shinVec.y);
        if (len === 0) {
            angles.kneeRight = null;
        } else {
            const normalized = { x: shinVec.x / len, y: shinVec.y / len };
            const verticalVec = { x: 0, y: 1 };  // Downward direction
            
            const dot = normalized.x * verticalVec.x + normalized.y * verticalVec.y;
            const det = normalized.x * verticalVec.y - normalized.y * verticalVec.x;
            
            let angle = Math.atan2(det, dot);
            angle = Math.abs(angle) * (180 / Math.PI);
            
            if (angle > 180) angle = 360 - angle;
            angles.kneeRight = angle;
        }
    }

    // Neck flexion - angle between spine (shoulder-to-hip) and head relative to shoulder
    if (landmarks[0] && landmarks[11] && landmarks[12] && landmarks[23] && landmarks[24]) {
        // Spine reference: shoulder midpoint to hip midpoint
        const shoulderMid = { x: (landmarks[11].x + landmarks[12].x) / 2, y: (landmarks[11].y + landmarks[12].y) / 2 };
        const hipMid = { x: (landmarks[23].x + landmarks[24].x) / 2, y: (landmarks[23].y + landmarks[24].y) / 2 };
        
        // Calculate angle between spine (vertical reference) and head direction
        angles.neckFlexLeft = calculateAngle(
            { x: shoulderMid.x, y: shoulderMid.y - 0.3 },  // Point above shoulder
            shoulderMid,
            landmarks[0]  // Head/nose
        );
        angles.neckFlexRight = angles.neckFlexLeft; // Same for both sides (flexion is symmetric)
    }

    // Neck rotation - detect head turn angle relative to shoulders
    if (landmarks[0] && landmarks[11] && landmarks[12] && landmarks[23] && landmarks[24]) {
        const shoulderMid = { x: (landmarks[11].x + landmarks[12].x) / 2, y: (landmarks[11].y + landmarks[12].y) / 2 };
        const hipMid = { x: (landmarks[23].x + landmarks[24].x) / 2, y: (landmarks[23].y + landmarks[24].y) / 2 };
        
        // Calculate lateral rotation angle: head position relative to shoulder center using spine as reference
        angles.neckRotateLeft = calculateAngle(
            landmarks[11],  // Left shoulder
            shoulderMid,    // Shoulder midpoint (center)
            landmarks[0]    // Head
        ) / 2;  // Divide by 2 to get actual rotation (not full angle between points)
        
        angles.neckRotateRight = angles.neckRotateLeft; // Same value for rotation detection
    }

    // Wrist flexion (using hand landmarks if available)
    if (landmarks[15] && landmarks[17] && landmarks[19]) {
        angles.wristFlexLeft = calculateAngle(
            landmarks[13], landmarks[15], landmarks[17]
        );
    }
    if (landmarks[16] && landmarks[18] && landmarks[20]) {
        angles.wristFlexRight = calculateAngle(
            landmarks[14], landmarks[16], landmarks[18]
        );
    }

    // Ankle angles - dorsiflexion/plantarflexion (knee → ankle → foot)
    if (landmarks[25] && landmarks[27] && landmarks[29]) {
        // Left ankle: hip → knee → ankle → foot
        angles.ankleAngleLeft = calculateAngle(
            landmarks[25], landmarks[27], landmarks[29]
        );
    }
    if (landmarks[26] && landmarks[28] && landmarks[30]) {
        // Right ankle: hip → knee → ankle → foot
        angles.ankleAngleRight = calculateAngle(
            landmarks[26], landmarks[28], landmarks[30]
        );
    }

    // Ankle rotation/inversion-eversion - using foot landmarks relative to ankle
    if (landmarks[27] && landmarks[29] && landmarks[31]) {
        // Calculate angle from ankle to foot position, comparing to expected alignment
        angles.ankleRotateLeft = calculateAngle(
            landmarks[27],  // Knee
            landmarks[29],  // Ankle
            landmarks[31]   // Foot index
        );
    }
    if (landmarks[28] && landmarks[30] && landmarks[32]) {
        // Right side
        angles.ankleRotateRight = calculateAngle(
            landmarks[28],  // Knee
            landmarks[30],  // Ankle
            landmarks[32]   // Foot index
        );
    }

    // Back extension (using shoulder and hip depth)
    if (landmarks[11] && landmarks[12] && landmarks[23] && landmarks[24]) {
        const shoulderMidpoint = { x: (landmarks[11].x + landmarks[12].x) / 2, y: (landmarks[11].y + landmarks[12].y) / 2 };
        const hipMidpoint = { x: (landmarks[23].x + landmarks[24].x) / 2, y: (landmarks[23].y + landmarks[24].y) / 2 };
        angles.backExtend = calculateAngle(
            shoulderMidpoint,
            hipMidpoint,
            { x: hipMidpoint.x, y: hipMidpoint.y + 0.3 }
        );
    }

    console.log('Calculated angles:', angles);
    return angles;
}

// Detect exercise type based on movement patterns
function detectExerciseType(angles) {
    console.log('Detecting exercise type with angles:', angles);

    // Check for valid angles
    const hasValidAngles = Object.values(angles).some(angle => angle !== null && angle !== undefined);
    if (!hasValidAngles) return currentExercise;

    // Detect squats (knee angle changes)
    const avgKneeAngle = getAverageAngle(angles.kneeLeft, angles.kneeRight);
    if (avgKneeAngle !== null && avgKneeAngle < 120) {
        console.log('Detected squat exercise');
        return 'Body Weight Squat';
    }

    // Detect shoulder flexion (shoulder angle changes)
    const avgShoulderAngle = getAverageAngle(angles.shoulderLeft, angles.shoulderRight);
    if (avgShoulderAngle !== null && avgShoulderAngle < 90) {
        console.log('Detected shoulder flexion');
        return 'Shoulder Flexion';
    }

    // Detect elbow flexion (elbow angle changes)
    const avgElbowAngle = getAverageAngle(angles.elbowLeft, angles.elbowRight);
    if (avgElbowAngle !== null && avgElbowAngle < 120) {
        console.log('Detected elbow flexion');
        return 'Elbow Flexion';
    }

    return currentExercise; // Default to current exercise
}

// Helper function to get average angle
function getAverageAngle(angle1, angle2) {
    const validAngles = [angle1, angle2].filter(angle => angle !== null && angle !== undefined);
    if (validAngles.length === 0) return null;
    return validAngles.reduce((sum, angle) => sum + angle, 0) / validAngles.length;
}

// Detect exercise phase using configuration
function detectExercisePhase(angles, exerciseType) {
    const config = EXERCISE_CONFIG[exerciseType];
    if (!config) return 'ready';

    const primaryAngle = config.primaryAngle;
    let angle = getAverageAngle(angles[primaryAngle + 'Left'], angles[primaryAngle + 'Right']);

    // Handle special angle naming conventions
    if (angle === null && angles[primaryAngle] !== undefined) {
        angle = angles[primaryAngle];
    }

    if (angle === null) {
        console.debug(`⚠️ ${exerciseType}: No angle detected (Missing ${primaryAngle}Left/Right)`);
        console.debug(`   Available angles: ${Object.keys(angles).filter(k => angles[k] !== null).join(', ')}`);
        return 'ready';
    }

    const [minOptimal, maxOptimal] = config.optimalRange;
    const isInOptimalRange = angle >= minOptimal && angle <= maxOptimal;

    const phase = isInOptimalRange ? config.repPhases[1] : config.repPhases[0];
    
    // Enhanced logging for shoulder exercises
    if (exerciseType.includes('Shoulder') || exerciseType.includes('Elbow')) {
        console.log(`📊 ${exerciseType} phase: ${phase} (angle: ${angle.toFixed(1)}°, range: ${minOptimal}-${maxOptimal}°, in-range: ${isInOptimalRange})`);
    }

    return phase;
}

// Count reps using configuration — full-cycle approach
// A rep requires: start_phase (held) → end_phase (held) → start_phase (held) → end_phase (held) = 1 rep
// First time we just initialize. After that: waiting_start → in_start → waiting_end → in_end(=rep counted) → waiting_start
function countReps(phase) {
    const config = EXERCISE_CONFIG[currentExercise];
    if (!config) return;
    
    // Don't count reps if required landmarks aren't visible
    if (exerciseState.visibility === false) {
        console.debug(`⏸️ Reps not counted - required landmarks not visible for ${currentExercise}`);
        return;
    }

    const startPhase = config.repPhases[0];
    const endPhase = config.repPhases[1];

    // Phase stabilization: only accept a phase change after it's held for N consecutive frames
    if (phase === exerciseState.lastRawPhase) {
        exerciseState.phaseHoldFrames++;
    } else {
        exerciseState.phaseHoldFrames = 1;
        exerciseState.lastRawPhase = phase;
    }

    // Don't act until phase is stable (held for required frames)
    if (exerciseState.phaseHoldFrames < exerciseState.phaseHoldRequired) {
        return;
    }

    const stablePhase = phase;

    // If currentPhase is the same as stable phase, no transition — nothing to do
    if (exerciseState.currentPhase === stablePhase) {
        return;
    }

    // Phase actually changed (after stabilization)
    const prevPhase = exerciseState.currentPhase;
    exerciseState.currentPhase = stablePhase;

    // Initialize on first stable phase
    if (prevPhase === null) {
        // Start by waiting for the start phase of the first cycle
        if (stablePhase === startPhase) {
            exerciseState.cycleState = 'in_start';
            console.log(`📍 INITIAL: In start phase (${startPhase}) for ${currentExercise}`);
        } else {
            exerciseState.cycleState = 'waiting_start';
            console.log(`📍 INITIAL: Waiting for start phase (${startPhase}) for ${currentExercise}, currently in ${stablePhase}`);
        }
        return;
    }

    // State machine for full-cycle rep counting
    const now = Date.now();
    switch (exerciseState.cycleState) {
        case 'waiting_start':
            if (stablePhase === startPhase) {
                exerciseState.cycleState = 'in_start';
                console.debug(`🔄 Entered start phase (${startPhase})`);
            }
            break;

        case 'in_start':
            if (stablePhase === endPhase) {
                // Transition from start → end: check debounce, count the rep
                if (now - exerciseState.lastRepCountTime >= exerciseState.repCountDebounce) {
                    exerciseState.reps++;
                    exerciseState.lastRepCountTime = now;
                    exerciseState.cycleState = 'waiting_start'; // Wait for next start phase
                    console.log(`✅ Rep counted! Total: ${exerciseState.reps} | Exercise: ${currentExercise} | ${startPhase} → ${endPhase}`);
                    showNotification(`Rep ${exerciseState.reps}!`, 'success');
                    
                    // Voice feedback for rep counting
                    if (typeof speakRepCount === 'function') {
                        speakRepCount(exerciseState.reps);
                    }
                } else {
                    console.debug(`⏳ Rep debounced (${exerciseState.repCountDebounce - (now - exerciseState.lastRepCountTime)}ms remaining)`);
                    exerciseState.cycleState = 'waiting_start';
                }
            }
            break;
    }
}

// Calculate comprehensive quality score with multiple metrics
function calculateQualityScore(angles, phase) {
    const config = EXERCISE_CONFIG[currentExercise];
    if (!config) return 50;

    let totalScore = 0;
    let componentWeights = {
        angleAccuracy: 0.4,    // 40% - Primary angle accuracy
        symmetry: 0.25,        // 25% - Left-right balance
        stability: 0.15,       // 15% - Confidence in detection
        posture: 0.15,         // 15% - Body alignment
        rom: 0.05              // 5% - Range of motion usage
    };

    // 1. ANGLE ACCURACY SCORING (40%)
    const primaryAngle = config.primaryAngle;
    const leftAngle = angles[primaryAngle + 'Left'];
    const rightAngle = angles[primaryAngle + 'Right'];
    const mainAngle = getAverageAngle(leftAngle, rightAngle);

    if (mainAngle === null) return 0;

    const [minOptimal, maxOptimal] = config.optimalRange;
    let angleScore = 100;

    if (mainAngle < minOptimal) {
        // Penalty increases as we move further from optimal range
        const deviationPercent = ((minOptimal - mainAngle) / minOptimal) * 100;
        angleScore -= Math.min(100, deviationPercent * 0.5); // Softer penalty for under-extension
    } else if (mainAngle > maxOptimal) {
        // Penalty for over-extension
        const deviationPercent = ((mainAngle - maxOptimal) / maxOptimal) * 100;
        angleScore -= Math.min(100, deviationPercent * 0.5);
    } else {
        // Bonus for being in optimal range - higher score for being closer to center
        const rangeCenter = (minOptimal + maxOptimal) / 2;
        const distanceFromCenter = Math.abs(mainAngle - rangeCenter);
        const maxDistanceFromCenter = (maxOptimal - minOptimal) / 2;
        const centerBonus = Math.max(0, 10 * (1 - distanceFromCenter / maxDistanceFromCenter));
        angleScore = Math.min(100, angleScore + centerBonus);
    }

    // 2. SYMMETRY SCORING (25%)
    let symmetryScore = 100;
    if (leftAngle !== null && rightAngle !== null) {
        const angleDifference = Math.abs(leftAngle - rightAngle);
        const symmetryThreshold = (maxOptimal - minOptimal) * 0.15; // Allow 15% of range difference
        if (angleDifference > symmetryThreshold) {
            symmetryScore -= Math.min(100, (angleDifference / symmetryThreshold) * 50);
        } else {
            // Bonus for good symmetry
            symmetryScore = Math.min(100, 100 - (angleDifference / symmetryThreshold) * 25);
        }
    } else {
        // Single-side exercise - check if the angle value itself is reasonable
        symmetryScore = angleScore; // Use angle score as proxy
    }

    // 3. STABILITY SCORING (15%) - Based on hand analysis
    let stabilityScore = 80; // Default stability
    const handAnalysis = window.currentHandAnalysis;
    if (handAnalysis) {
        // Good stability if hands are stable (not twitching between states)
        if (handAnalysis.leftHand && (handAnalysis.leftHand.isOpen || handAnalysis.leftHand.isClosed)) {
            stabilityScore += 10;
        }
        if (handAnalysis.rightHand && (handAnalysis.rightHand.isOpen || handAnalysis.rightHand.isClosed)) {
            stabilityScore += 10;
        }
    }
    stabilityScore = Math.min(100, stabilityScore);

    // 4. POSTURE SCORING (15%)
    let postureScore = 100;
    if (window.currentLandmarks) {
        const landmarks = window.currentLandmarks;
        // Check shoulder alignment (both shoulders should be roughly at same height)
        if (landmarks[11] && landmarks[12]) {
            const shoulderHeightDiff = Math.abs(landmarks[11].y - landmarks[12].y);
            if (shoulderHeightDiff > 0.1) { // Significant shoulder drop
                postureScore -= Math.min(50, shoulderHeightDiff * 100);
            }
        }
        // Check hip alignment (both hips should be roughly at same height)
        if (landmarks[23] && landmarks[24]) {
            const hipHeightDiff = Math.abs(landmarks[23].y - landmarks[24].y);
            if (hipHeightDiff > 0.1) {
                postureScore -= Math.min(50, hipHeightDiff * 100);
            }
        }
    }
    postureScore = Math.max(0, postureScore);

    // 5. RANGE OF MOTION SCORING (5%)
    let romScore = 80; // Baseline
    // Check if we're using the full range when not in optimal zone
    if (mainAngle < minOptimal || mainAngle > maxOptimal) {
        romScore += 10; // Extending range
    } else {
        romScore += 20; // In optimal zone
    }
    romScore = Math.min(100, romScore);

    // WEIGHTED AVERAGE
    totalScore = (
        (angleScore * componentWeights.angleAccuracy) +
        (symmetryScore * componentWeights.symmetry) +
        (stabilityScore * componentWeights.stability) +
        (postureScore * componentWeights.posture) +
        (romScore * componentWeights.rom)
    );

    totalScore = Math.max(0, Math.min(100, totalScore));

    console.log(`Quality Breakdown - Angle: ${angleScore.toFixed(0)}% | Symmetry: ${symmetryScore.toFixed(0)}% | Stability: ${stabilityScore.toFixed(0)}% | Posture: ${postureScore.toFixed(0)}% | ROM: ${romScore.toFixed(0)}% = Total: ${totalScore.toFixed(0)}%`);

    return totalScore;
}

// Get main exercise angle using configuration
function getMainExerciseAngle(angles, exerciseType) {
    const config = EXERCISE_CONFIG[exerciseType];
    if (!config) return 0;

    const primaryAngle = config.primaryAngle;
    let leftAngle = angles[primaryAngle + 'Left'];
    let rightAngle = angles[primaryAngle + 'Right'];

    // Handle special angle naming conventions
    if (!leftAngle && !rightAngle) {
        // Try without Left/Right suffix (for single-value angles like neckFlex, wristFlex, etc.)
        if (angles[primaryAngle] !== undefined) {
            return angles[primaryAngle];
        }
    }

    return getAverageAngle(leftAngle, rightAngle) || 0;
}

// Provide form feedback using configuration
function provideFormFeedback(angles, exerciseType, phase) {
    const feedback = [];
    const config = EXERCISE_CONFIG[exerciseType];

    if (!config) {
        feedback.push("Exercise not configured for tracking");
        exerciseState.formFeedback = feedback;
        return;
    }

    const primaryAngle = config.primaryAngle;
    let angle = getAverageAngle(angles[primaryAngle + 'Left'], angles[primaryAngle + 'Right']);

    // Handle special angle naming conventions
    if (angle === null && angles[primaryAngle] !== undefined) {
        angle = angles[primaryAngle];
    }

    if (angle === null) {
        feedback.push("Position yourself in the camera view");
        exerciseState.formFeedback = feedback;
        return;
    }

    const [minOptimal, maxOptimal] = config.optimalRange;
    const isInOptimalRange = angle >= minOptimal && angle <= maxOptimal;

    // Add angle-based feedback
    if (isInOptimalRange) {
        feedback.push(`✅ Perfect form! Maintain ${angle.toFixed(0)}°`);
    } else if (angle < minOptimal) {
        feedback.push(`📈 Increase range: ${angle.toFixed(0)}° → ${minOptimal}°`);
    } else {
        feedback.push(`📉 Decrease range: ${angle.toFixed(0)}° → ${maxOptimal}°`);
    }

    // Add phase-specific feedback
    if (phase === config.repPhases[1]) {
        feedback.push(`📌 Great ${config.repPhases[1]} position!`);
    }
    
    // Add exercise-specific form corrections
    const exerciseFeedback = getExerciseSpecificFeedback(exerciseType, angles, phase);
    feedback.push(...exerciseFeedback);
    
    // Add symmetry feedback if applicable
    if (angles[primaryAngle + 'Left'] && angles[primaryAngle + 'Right']) {
        const leftAngle = angles[primaryAngle + 'Left'];
        const rightAngle = angles[primaryAngle + 'Right'];
        const diff = Math.abs(leftAngle - rightAngle);
        const threshold = (maxOptimal - minOptimal) * 0.15;
        
        if (diff > threshold) {
            feedback.push(`⚖️ Balance: L ${leftAngle.toFixed(0)}° vs R ${rightAngle.toFixed(0)}°`);
        }
    }

    exerciseState.formFeedback = feedback;
    console.log(`Generated feedback for ${exerciseType}:`, feedback);
}

// Update exercise UI
function updateExerciseUI(angles, phase) {
    console.log(`Updating UI - Exercise: ${currentExercise}, Phase: ${phase}, Visibility: ${exerciseState.visibility}, Angles:`, angles);

    // Update rep counter
    const repsElement = document.getElementById('repCount');
    if (repsElement) {
        repsElement.textContent = exerciseState.reps;
        console.log(`Updated reps to: ${exerciseState.reps}`);
    }

    // Update angle display
    const angleElement = document.getElementById('jointAngle');
    if (angleElement) {
        const mainAngle = getMainExerciseAngle(angles, currentExercise);
        const displayAngle = mainAngle !== null ? Math.round(mainAngle) : 0;
        angleElement.textContent = `${displayAngle}°`;
        console.log(`Updated angle to: ${displayAngle}°`);
    }

    // Update phase display
    const phaseElement = document.getElementById('phaseDisplay');
    if (phaseElement) {
        phaseElement.textContent = `Phase: ${phase}`;
        console.log(`Updated phase to: ${phase}`);
    }

    // Update current exercise
    const exerciseElement = document.getElementById('currentExercise');
    if (exerciseElement) {
        exerciseElement.textContent = currentExercise || '-';
    }

    // Update quality score
    const qualityElement = document.getElementById('qualityScore');
    if (qualityElement) {
        const quality = calculateQualityScore(angles, phase);
        qualityElement.textContent = `${Math.round(quality)}%`;
        
        // Update quality bar fill
        const qualityBarFill = document.getElementById('qualityBar');
        if (qualityBarFill) {
            qualityBarFill.style.width = `${Math.round(quality)}%`;
        }
        
        // Track quality for session average
        exerciseState.allQualityScores.push(quality);
        exerciseState.avgQualityScore = exerciseState.allQualityScores.reduce((a, b) => a + b, 0) / exerciseState.allQualityScores.length;
        
        // Apply color coding based on quality level
        if (quality >= 80) {
            qualityElement.className = 'quality-value quality-excellent';
        } else if (quality >= 60) {
            qualityElement.className = 'quality-value quality-good';
        } else if (quality >= 40) {
            qualityElement.className = 'quality-value quality-fair';
        } else {
            qualityElement.className = 'quality-value quality-poor';
        }
        
        console.log(`Updated quality to: ${Math.round(quality)}%`);
    }

    // Update pose detection status
    const landmarksElement = document.getElementById('landmarksStatus');
    if (landmarksElement) {
        if (exerciseState.visibility === false) {
            // Show which body parts need to be visible
            const requiredParts = {
                'Neck Flexion': 'head/neck',
                'Neck Extension': 'head/neck',
                'Neck Rotation': 'head/neck',
                'Shoulder Flexion': 'shoulders & arms',
                'Shoulder Abduction': 'shoulders & arms',
                'Shoulder Extension': 'shoulders & arms',
                'Shoulder Rotation': 'shoulders & arms',
                'Elbow Flexion': 'elbow & wrist',
                'Elbow Extension': 'elbow & wrist',
                'Wrist Flexion': 'wrist',
                'Wrist Extension': 'wrist',
                'Knee Flexion': 'knees',
                'Knee Extension': 'knees',
                'Hip Abduction': 'hips & legs',
                'Hip Flexion': 'hips & legs',
                'Ankle Dorsiflexion': 'feet & ankles',
                'Ankle Plantarflexion': 'feet & ankles',
                'Ankle Inversion': 'feet & ankles',
                'Ankle Eversion': 'feet & ankles',
                'Ankle Rotation': 'feet & ankles',
                'Back Extension': 'back',
                'Body Weight Squat': 'full body',
                'Wall Sit': 'full body',
                'Sumo Squat': 'full body',
                'Partial Squat': 'full body',
                'Squat Hold': 'full body'
            };
            const bodyParts = requiredParts[currentExercise] || 'required body parts';
            landmarksElement.textContent = `❌ Not Detected (Show: ${bodyParts})`;
            landmarksElement.className = 'landmarks-value not-detected';
        } else {
            const hasLandmarks = Object.keys(angles).length > 0 && Object.values(angles).some(angle => angle !== null);
            landmarksElement.textContent = hasLandmarks ? '✅ Detected' : '❌ Not Detected';
            landmarksElement.className = hasLandmarks ? 'landmarks-value detected' : 'landmarks-value';
        }
        console.log(`Updated landmarks status: ${exerciseState.visibility !== false ? 'Detected' : 'Not Detected'}`);;
    }

    // Update posture feedback
    const postureElement = document.getElementById('postureFeedback');
    if (postureElement && exerciseState.formFeedback.length > 0) {
        // Show the most relevant feedback items
        // Prioritize: angle feedback (first), form guidance, then balance/alignment
        const feedback = exerciseState.formFeedback;
        
        // Get the main angle feedback and one form guidance message
        let displayText = feedback[0]; // Angle feedback
        
        // Find and add the most relevant form guidance (looking for positioning tips)
        const formGuidance = feedback.find(f => 
            f.includes('Keep') || f.includes('Bring') || f.includes('Raise') || 
            f.includes('Bend') || f.includes('Rotate') || f.includes('Lower') ||
            f.includes('Turn') || f.includes('Slide')
        );
        
        if (formGuidance) {
            displayText = formGuidance;
        }
        
        // Check if form is good for color coding
        const isGood = feedback[0].includes('✅ Perfect') || feedback.some(f => f.includes('Great'));
        const needsUp = feedback[0].includes('📈 Increase');
        const needsDown = feedback[0].includes('📉 Decrease');
        const isBalancing = feedback.some(f => f.includes('⚖️'));
        const isAligning = feedback.some(f => f.includes('📍'));
        
        postureElement.textContent = displayText;
        
        // Set appropriate CSS class based on feedback type
        if (isGood) {
            postureElement.className = 'posture-value good';
        } else if (isBalancing || isAligning) {
            postureElement.className = 'posture-value needs-improvement';
        } else if (needsUp || needsDown) {
            postureElement.className = 'posture-value needs-improvement';
        } else {
            postureElement.className = 'posture-value';
        }
        
        console.log(`Updated posture feedback: "${displayText}"`);
        
        // Voice feedback for form corrections - only speak on change or after cooldown
        if (typeof speakFormFeedback === 'function' && voiceAssistant.enabled) {
            const now = Date.now();
            const feedbackText = feedback.length > 0 ? feedback[0] : '';
            
            // Only speak if feedback changed or cooldown expired
            if (feedbackText !== exerciseState.lastSpokenFeedback || 
                (now - exerciseState.lastFeedbackSpokenTime > exerciseState.feedbackCooldown)) {
                
                // Only speak actual feedback, not "perfect form" on every frame
                if (feedbackText && !feedbackText.includes('Perfect form')) {
                    speakFormFeedback(feedback);
                    exerciseState.lastSpokenFeedback = feedbackText;
                    exerciseState.lastFeedbackSpokenTime = now;
                }
            }
        }
    } else if (postureElement) {
        postureElement.textContent = 'Position yourself in the camera';
        postureElement.className = 'posture-value needs-improvement';
    }

    // Update feedback message
    const feedbackElement = document.getElementById('feedbackMessage');
    if (feedbackElement && exerciseState.formFeedback.length > 0) {
        feedbackElement.textContent = exerciseState.formFeedback[0];
    }

    // Update detailed form feedback
    const feedbackElement = document.getElementById('formFeedback');
    if (feedbackElement && exerciseState.formFeedback.length > 0) {
        feedbackElement.innerHTML = exerciseState.formFeedback
            .map(feedback => `<div class="feedback-item">${feedback}</div>`)
            .join('');
    }
}

// Camera and WebSocket
async function startCamera() {
    try {
        console.log(`Starting camera for exercise: ${currentExercise}`);

        // Stop any existing camera stream first
        if (videoStream) {
            console.log('Stopping existing video stream...');
            videoStream.getTracks().forEach(track => track.stop());
            videoStream = null;
        }

        // Reset pose detection to ensure fresh start for each exercise
        pose = null;
        isDetecting = false;

        // Check if browser supports required APIs
        if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
            throw new Error('Camera API not supported in this browser');
        }

        // Get camera stream first
        console.log('Requesting camera access...');
        videoStream = await navigator.mediaDevices.getUserMedia({
            video: {
                width: { ideal: 640 },
                height: { ideal: 480 },
                facingMode: 'user'
            }
        });

        const video = document.getElementById('videoElement');
        if (!video) {
            throw new Error('Video element not found');
        }

        video.srcObject = videoStream;

        // Wait for video to be ready
        await new Promise((resolve) => {
            video.onloadedmetadata = () => {
                console.log('✓ Video metadata loaded');
                resolve();
            };
        });

        // Hide placeholder, show video
        const placeholder = document.getElementById('cameraPlaceholder');
        if (placeholder) {
            placeholder.style.display = 'none';
        }
        video.style.display = 'block';
        
        // Test canvas visibility with a simple drawing
        const canvas = document.getElementById('overlayCanvas');
        if (canvas) {
            canvas.style.display = 'block';
            const testCtx = canvas.getContext('2d');
            canvas.width = video.videoWidth || 640;
            canvas.height = video.videoHeight || 480;
            
            // Draw a test rectangle to verify canvas is visible
            testCtx.strokeStyle = '#FFFF00';
            testCtx.lineWidth = 5;
            testCtx.strokeRect(10, 10, canvas.width - 20, canvas.height - 20);
            testCtx.fillStyle = '#FFFF0077';
            testCtx.fillRect(15, 15, 200, 50);
            testCtx.fillStyle = '#FFFFFF';
            testCtx.font = '20px Arial';
            testCtx.fillText('Canvas Test OK', 25, 45);
            
            console.log('✓ Canvas test drawing complete');
        } else {
            console.error('❌ Canvas element not found during test');
        }

        // Initialize MediaPipe fresh for this exercise
        try {
            console.log('Initializing MediaPipe Pose for this exercise...');
            await initializePoseDetection();
            console.log('✓ MediaPipe Pose initialized');

            // Start MediaPipe pose detection
            isDetecting = true;
            console.log('✓ Starting pose detection...');

            // Check MediaPipe status
            checkMediaPipeStatus();

            // Start frame processing
            processVideoFrames(video);

        } catch (mediaPipeError) {
            console.error('❌ MediaPipe initialization failed:', mediaPipeError);
            showNotification('Camera started but pose detection unavailable', 'warning');

            // Try to continue with video only mode
            isDetecting = false;

            // Show fallback message
            const postureElement = document.getElementById('postureFeedback');
            if (postureElement) {
                postureElement.textContent = 'Pose detection unavailable - Video only mode';
                postureElement.className = 'posture-value needs-improvement';
            }
        }

        // Connect WebSocket for backend communication
        connectWebSocket();

        // Update UI
        const startBtn = document.getElementById('startBtn');
        const pauseBtn = document.getElementById('pauseBtn');
        if (startBtn) startBtn.style.display = 'none';
        if (pauseBtn) pauseBtn.style.display = 'inline-flex';

        showNotification('Camera started! Position yourself in the frame.', 'success');

    } catch (error) {
        console.error('Error starting camera:', error);

        // Provide specific error messages
        let errorMessage = 'Failed to start camera';
        if (error.name === 'NotAllowedError') {
            errorMessage = 'Camera permission denied. Please allow camera access.';
        } else if (error.name === 'NotFoundError') {
            errorMessage = 'No camera found. Please connect a camera.';
        } else if (error.name === 'NotReadableError') {
            errorMessage = 'Camera is already in use by another application.';
        } else if (error.message) {
            errorMessage = `Camera error: ${error.message}`;
        }

        showNotification(errorMessage, 'error');
    }
}

// Process video frames for pose detection
async function processVideoFrames(video) {
    if (!isDetecting || !pose || !video) return;

    try {
        await pose.send({ image: video });
    } catch (error) {
        console.error('Error processing frame:', error);

        // If MediaPipe fails, try to recover
        if (error.message.includes('not ready') || error.message.includes('not loaded')) {
            console.log('MediaPipe not ready, retrying...');
            setTimeout(() => {
                if (isDetecting) {
                    processVideoFrames(video);
                }
            }, 1000);
        }
    }

    // Continue processing frames if still detecting
    if (isDetecting) {
        requestAnimationFrame(() => processVideoFrames(video));
    }
}

// Debug function to check MediaPipe status
function checkMediaPipeStatus() {
    console.log('MediaPipe Status Check:');
    console.log('- Pose object:', pose ? '✅ Created' : '❌ Not created');
    console.log('- Is detecting:', isDetecting);
    console.log('- Current exercise:', currentExercise);

    if (pose) {
        console.log('- Pose options configured');
    }
}

// Pause camera
function pauseCamera() {
    isDetecting = false;
    console.log('Camera paused');

    const startBtn = document.getElementById('startBtn');
    const pauseBtn = document.getElementById('pauseBtn');
    if (startBtn) startBtn.style.display = 'inline-flex';
    if (pauseBtn) pauseBtn.style.display = 'none';

    showNotification('Camera paused', 'info');
}

// Stop camera
function stopCamera() {
    isDetecting = false;
    console.log('Stopping camera...');

    if (videoStream) {
        videoStream.getTracks().forEach(track => track.stop());
        videoStream = null;
    }

    const video = document.getElementById('videoElement');
    if (video) {
        video.srcObject = null;
    }

    // Save exercise session before resetting state
    const exerciseToSave = selectedExercise || currentExercise;
    if (exerciseToSave && exerciseState.reps > 0) {
        // Calculate average angle
        let avgAngle = 0;
        if (exerciseState.allAngles && exerciseState.allAngles.length > 0) {
            avgAngle = exerciseState.allAngles.reduce((a, b) => a + b, 0) / exerciseState.allAngles.length;
        }
        // Calculate duration in seconds
        const duration = exerciseState.startTime ? Math.floor((Date.now() - exerciseState.startTime) / 1000) : 0;
        saveExerciseSession(exerciseToSave, exerciseState.reps, exerciseState.avgQualityScore || 0, duration, 100, avgAngle);
    }

    // Reset exercise state
    exerciseState = {
        reps: 0,
        currentPhase: null,
        angles: {},
        allAngles: [],
        allQualityScores: [],
        formFeedback: [],
        lastPoseTime: 0,
        exerciseType: null,
        visibility: true,
        lastSpokenFeedback: '',
        lastFeedbackSpokenTime: 0,
        feedbackCooldown: 3000,
        lastRepCountTime: 0,
        repCountDebounce: 1000,
        cycleState: 'waiting_start',
        phaseHoldFrames: 0,
        phaseHoldRequired: 3,
        lastRawPhase: null,
        startTime: null,
        avgQualityScore: 0
    };
    const canvas = document.getElementById('overlayCanvas');
    if (canvas) {
        const canvasCtx = canvas.getContext('2d');
        canvasCtx.clearRect(0, 0, canvas.width, canvas.height);
    }

    // Update UI
    const startBtn = document.getElementById('startBtn');
    const pauseBtn = document.getElementById('pauseBtn');
    const placeholder = document.getElementById('cameraPlaceholder');
    if (startBtn) startBtn.style.display = 'inline-flex';
    if (pauseBtn) pauseBtn.style.display = 'none';
    if (placeholder) placeholder.style.display = 'block';
    if (video) video.style.display = 'none';

    showNotification('Camera stopped', 'info');
}

// Reset exercise
function resetExercise() {
    if (websocket) {
        websocket.send(JSON.stringify({ type: 'reset' }));
    }

    // Reset exercise state
    exerciseState = {
        reps: 0,
        currentPhase: 'ready',
        angles: {},
        allAngles: [],
        allQualityScores: [],
        formFeedback: [],
        lastPoseTime: 0,
        exerciseType: null,
        visibility: true,
        lastRepCountTime: 0,
        lastSpokenFeedback: '',
        lastFeedbackSpokenTime: 0,
        feedbackCooldown: 3000,
        repCountDebounce: 1000,
        cycleState: 'waiting_start',
        phaseHoldFrames: 0,
        phaseHoldRequired: 3,
        lastRawPhase: null,
        startTime: Date.now(),
        avgQualityScore: 0
    };

    resetExerciseData();
    
    // Update UI
    const repsElement = document.getElementById('repCount');
    if (repsElement) repsElement.textContent = '0';
    const angleElement = document.getElementById('jointAngle');
    if (angleElement) angleElement.textContent = '0°';
    const qualityElement = document.getElementById('qualityScore');
    if (qualityElement) qualityElement.textContent = '0%';
    
    showNotification('Exercise reset', 'info');
}

function connectWebSocket() {
    if (!currentUser || !authToken) {
        showNotification('Please login to start exercises', 'error');
        return;
    }

    const wsUrl = `ws://${window.location.hostname}:8000/ws/${currentUser.id}`;
    websocket = new WebSocket(wsUrl);

    websocket.onopen = function () {
        console.log('WebSocket connected');
        showNotification('Connected to exercise tracking system', 'success');
    };

    websocket.onmessage = function (event) {
        const data = JSON.parse(event.data);
        handleWebSocketMessage(data);
    };

    websocket.onerror = function (error) {
        console.error('WebSocket error:', error);
        showNotification('Connection error. Please try again.', 'error');
    };

    websocket.onclose = function () {
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

    // Update feedback message
    if (data.voice_message) {
        const feedbackElement = document.getElementById('feedbackMessage');
        feedbackElement.textContent = data.voice_message;

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

            canvas.toBlob(function (blob) {
                const reader = new FileReader();
                reader.onloadend = function () {
                    const base64data = reader.result.split(',')[1];

                    // Include exercise name for backend rep counting
                    websocket.send(JSON.stringify({
                        type: 'frame',
                        frame_data: base64data,
                        exercise_name: currentExercise || null  // Send selected exercise, null for auto-detection
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
    document.getElementById('feedbackMessage').textContent = 'Feedback will appear here';
}

async function exitExercise() {
    console.log('🔴 Exiting exercise started...');
    
    try {
        // 1. SAVE SESSION FIRST (before stopping anything)
        try {
            if (currentExercise && exerciseState.reps > 0) {
                console.log('💾 Saving session for:', currentExercise, 'reps:', exerciseState.reps);
                
                // Calculate average angle
                let avgAngle = 0;
                if (exerciseState.allAngles && exerciseState.allAngles.length > 0) {
                    avgAngle = exerciseState.allAngles.reduce((a, b) => a + b, 0) / exerciseState.allAngles.length;
                }
                
                // Calculate duration in seconds
                const duration = exerciseState.startTime ? Math.floor((Date.now() - exerciseState.startTime) / 1000) : 0;
                
                // AWAIT the save to ensure it completes before resetting state
                await saveExerciseSession(currentExercise, exerciseState.reps, exerciseState.avgQualityScore || 0, duration, 100, avgAngle);
                
                // If we're in rehab context, update rehab session status
                if (window._rehabContext) {
                    const quality = Math.round(exerciseState.avgQualityScore || 0);
                    const status = quality >= 70 ? 'completed' : 'incomplete';
                    await updateRehabSessionStatus(currentExercise, exerciseState.reps, quality, status);
                }
            } else {
                console.log('ℹ️ No session to save:', { exercise: currentExercise, reps: exerciseState.reps });
            }
        } catch (e) {
            console.warn('⚠️  Could not save session:', e.message);
        }
        
        // 2. STOP CAMERA AND VIDEO
        try {
            isDetecting = false;
            if (videoStream) {
                videoStream.getTracks().forEach(track => {
                    try {
                        track.stop();
                    } catch (e) {
                        console.warn('Could not stop track:', e);
                    }
                });
                videoStream = null;
            }
            
            const video = document.getElementById('videoElement');
            if (video) {
                video.srcObject = null;
                video.style.display = 'none';
            }
            
            console.log('✓ Video stream stopped');
        } catch (e) {
            console.warn('⚠️  Could not stop camera:', e.message);
        }
        
        // 3. CLEAR CANVAS
        try {
            const canvas = document.getElementById('overlayCanvas');
            if (canvas) {
                const canvasCtx = canvas.getContext('2d');
                canvasCtx.clearRect(0, 0, canvas.width, canvas.height);
            }
        } catch (e) {
            console.warn('⚠️  Could not clear canvas:', e.message);
        }
        
        // 4. CLOSE WEBSOCKET
        try {
            if (websocket) {
                if (websocket.readyState === WebSocket.OPEN) {
                    websocket.close();
                    console.log('✓ WebSocket closed');
                }
                websocket = null;
            }
        } catch (e) {
            console.warn('⚠️  Could not close websocket:', e.message);
        }
        
        // 5. CLOSE POSE
        try {
            if (pose) {
                pose.close();
                pose = null;
                console.log('✓ MediaPipe Pose closed');
            }
        } catch (e) {
            console.warn('⚠️  Could not close pose:', e.message);
        }
        
        // 6. RESET ALL STATE
        isDetecting = false;
        currentExercise = null;
        selectedExercise = null;
        exerciseState = {
            reps: 0,
            currentPhase: null,
            angles: {},
            allAngles: [],
            allQualityScores: [],
            formFeedback: [],
            lastPoseTime: 0,
            exerciseType: null,
            visibility: true,
            lastSpokenFeedback: '',
            lastFeedbackSpokenTime: 0,
            feedbackCooldown: 3000,
            lastRepCountTime: 0,
            repCountDebounce: 1000,
            cycleState: 'waiting_start',
            phaseHoldFrames: 0,
            phaseHoldRequired: 3,
            lastRawPhase: null,
            startTime: null,
            avgQualityScore: 0
        };
        
        // Reset UI elements
        try {
            document.getElementById('repCount').textContent = '0';
            document.getElementById('jointAngle').textContent = '0°';
            document.getElementById('qualityScore').textContent = '0%';
            document.getElementById('cameraPlaceholder').style.display = 'block';
            document.getElementById('startBtn').style.display = 'inline-flex';
            document.getElementById('pauseBtn').style.display = 'none';
        } catch (e) {
            console.warn('⚠️  Could not reset UI:', e.message);
        }
        
        console.log('✓ All state reset');
        
        // 7. NAVIGATE AWAY (SMART NAVIGATION)
        console.log('🔵 Navigating to previous page...');
        
        // If we came from rehab plan, go back there and reload it
        if (window._rehabContext) {
            console.log('📋 Going back to Rehab Plan');
            window._rehabContext = null; // Clear context
            showPage('rehabPlan');
            loadRehabPlanData(); // Reload to show updated status
        } else if (previousPage === 'exerciseList' && currentCategory) {
            // User came from a category exercise list - reload that category's exercises
            console.log(`📂 Going back to ${currentCategory} exercises`);
            loadCategoryExercises(currentCategory);
        } else if (previousPage === 'allExercises') {
            // User came from all exercises view
            console.log('📋 Going back to all exercises');
            showPage('allExercises');
        } else {
            // Default: return to categories
            console.log('📁 Going back to exercise categories');
            showPage('exercises');
        }
        console.log('✓ Exited exercise successfully');
        
    } catch (e) {
        console.error('❌ CRITICAL: Exit exercise failed:', e);
        // Force navigation even if something failed - use smart navigation
        if (previousPage === 'exerciseList' && currentCategory) {
            console.log(`⚠️ Error recovery: Going back to ${currentCategory} exercises`);
            loadCategoryExercises(currentCategory);
        } else if (previousPage === 'allExercises') {
            console.log('⚠️ Error recovery: Going back to all exercises');
            showPage('allExercises');
        } else {
            console.log('⚠️ Error recovery: Going back to exercise categories');
            showPage('exercises');
        }
    }
}

// Save exercise session to backend
async function saveExerciseSession(exerciseName, totalReps, qualityScore = 0, duration = 0, postureCorrectness = 100, averageAngle = 0) {
    console.log('💾 saveExerciseSession called:', { exerciseName, totalReps, qualityScore, duration, postureCorrectness, averageAngle });
    console.log('💾 Auth state:', { hasUser: !!currentUser, hasToken: !!authToken, username: currentUser?.username });
    
    if (!currentUser || !authToken) {
        console.warn('❌ User not authenticated for saving session - data will be lost!');
        showNotification('Please log in to save exercise data', 'warning');
        return null;
    }

    try {
        const sessionData = {
            exercise_name: exerciseName,
            total_reps: totalReps,
            average_joint_angle: averageAngle,
            quality_score: qualityScore,
            duration_seconds: duration,
            posture_correctness: postureCorrectness
        };
        
        console.log('💾 Sending session data to API:', JSON.stringify(sessionData));

        const response = await fetch(`${API_BASE}/sessions`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${authToken}`
            },
            body: JSON.stringify(sessionData)
        });

        console.log('💾 API response status:', response.status);

        if (response.ok) {
            const session = await response.json();
            console.log('✅ Exercise session saved successfully:', session);
            
            // Show completion notification
            showNotification(`${exerciseName}: ${totalReps} reps saved!`, 'success');
            
            // Mark that we have new session data to show on dashboard
            window._pendingDashboardRefresh = true;
            
            return session;
        } else if (response.status === 401) {
            // Token expired - try to re-authenticate
            console.warn('⚠️ Token expired, attempting re-auth...');
            const refreshed = await tryRefreshAuth();
            if (refreshed) {
                // Retry the save with new token
                return await saveExerciseSession(exerciseName, totalReps, qualityScore, duration, postureCorrectness, averageAngle);
            } else {
                showNotification('Session expired. Please log in again to save data.', 'error');
                return null;
            }
        } else {
            const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
            console.error('❌ Error saving session:', response.status, error);
            showNotification(`Could not save exercise session: ${error.detail || response.status}`, 'error');
        }
    } catch (error) {
        console.error('Error saving exercise session:', error);
        showNotification('Error saving progress: ' + error.message, 'error');
    }
}

// Dashboard
async function loadDashboardData() {
    console.log('📊 loadDashboardData called. Auth:', { hasUser: !!currentUser, hasToken: !!authToken });

    // Cap date picker at today so users can't select future dates
    const picker = document.getElementById('sessionDateFilter');
    if (picker && !picker.max) {
        const today = new Date();
        picker.max = `${today.getFullYear()}-${String(today.getMonth() + 1).padStart(2, '0')}-${String(today.getDate()).padStart(2, '0')}`;
    }
    
    if (!currentUser || !authToken) {
        console.warn('📊 Cannot load dashboard: not authenticated');
        return;
    }

    try {
        // Load sessions
        const url = `${API_BASE}/sessions`;
        console.log('📊 Fetching sessions from:', url);
        const sessionsResponse = await fetch(url, {
            headers: {
                'Authorization': `Bearer ${authToken}`
            }
        });

        console.log('📊 Sessions response status:', sessionsResponse.status);

        if (sessionsResponse.ok) {
            const sessions = await sessionsResponse.json();
            console.log('📊 Sessions loaded:', sessions.length, 'sessions');
            if (sessions.length > 0) {
                console.log('📊 Latest session:', sessions[0]);
            }
            allSessionsData = sessions; // Store all sessions for filtering
            
            // Update all dashboard components
            updateDashboardStats(sessions);
            updateBodyPartStats(sessions);
            buildExercisePerformanceTable(sessions);
            displayRecentSessions(sessions, 'all');
            generateWeeklyChart(sessions);
            generateQualityChart(sessions);
            updateAIInsights(sessions);
            updateRangeOfMotion(sessions);
        } else if (sessionsResponse.status === 401) {
            console.warn('📊 Token expired for dashboard load');
            showNotification('Session expired. Please log in again.', 'warning');
        } else {
            console.error('📊 Failed to load sessions:', sessionsResponse.status);
        }
    } catch (error) {
        console.error('Error loading dashboard data:', error);
    }
}

function updateDashboardStats(sessions) {
    const setTrend = (id, cls, icon, text) => {
        const el = document.getElementById(id);
        if (el) { el.className = 'sc-trend ' + cls; el.innerHTML = `<i class="fas fa-${icon}"></i> ${text}`; }
    };

    if (!sessions || sessions.length === 0) {
        document.getElementById('totalSessions').textContent = '0';
        document.getElementById('totalReps').textContent = '0';
        document.getElementById('avgQuality').textContent = '0%';
        document.getElementById('daysActive').textContent = '0';
        document.getElementById('currentStreak').textContent = '0';
        document.getElementById('totalDuration').textContent = '0h';
        setTrend('trendSessions', 'neutral', 'minus', 'No data');
        setTrend('trendReps', 'neutral', 'minus', 'No data');
        setTrend('trendQuality', 'neutral', 'minus', 'No data');
        setTrend('trendDays', 'neutral', 'minus', 'No data');
        setTrend('trendStreak', 'neutral', 'minus', 'No data');
        setTrend('trendDuration', 'neutral', 'minus', 'No data');
        return;
    }

    const totalSessions = sessions.length;
    const totalReps = sessions.reduce((sum, session) => sum + (session.total_reps || 0), 0);
    const avgQuality = sessions.length > 0 ?
        sessions.reduce((sum, session) => sum + (session.quality_score || 0), 0) / sessions.length : 0;

    // Calculate unique days
    const uniqueDays = new Set(sessions.map(session =>
        new Date(session.date).toDateString()
    )).size;

    // Calculate current streak
    const streak = calculateCurrentStreak(sessions);

    // Calculate total duration from duration_seconds field
    const totalSeconds = sessions.reduce((sum, session) => {
        return sum + (session.duration_seconds || 0);
    }, 0);
    const totalHours = (totalSeconds / 3600).toFixed(1);

    document.getElementById('totalSessions').textContent = totalSessions;
    document.getElementById('totalReps').textContent = totalReps;
    document.getElementById('avgQuality').textContent = `${avgQuality.toFixed(1)}%`;
    document.getElementById('daysActive').textContent = uniqueDays;
    document.getElementById('currentStreak').textContent = streak;
    document.getElementById('totalDuration').textContent = totalHours + 'h';

    // Update trends based on actual data
    setTrend('trendSessions', 'up', 'arrow-up', 'Active');
    setTrend('trendReps', totalReps > 0 ? 'up' : 'neutral', totalReps > 0 ? 'arrow-up' : 'minus', totalReps > 0 ? 'Growing' : 'Start');
    setTrend('trendQuality', avgQuality >= 70 ? 'up' : avgQuality >= 40 ? 'neutral' : 'down', avgQuality >= 70 ? 'arrow-up' : avgQuality >= 40 ? 'minus' : 'arrow-down', avgQuality >= 70 ? 'Great' : avgQuality >= 40 ? 'Fair' : 'Needs work');
    setTrend('trendDays', 'up', 'arrow-up', uniqueDays > 1 ? 'Consistent' : 'Started');
    setTrend('trendStreak', streak > 0 ? 'up' : 'neutral', streak > 0 ? 'arrow-up' : 'minus', streak > 0 ? 'Keep going!' : 'Build it');
    setTrend('trendDuration', 'up', 'arrow-up', 'On track');
}

function calculateCurrentStreak(sessions) {
    if (!sessions || sessions.length === 0) return 0;

    // Sort sessions by date descending
    const sortedSessions = [...sessions].sort((a, b) => new Date(b.date) - new Date(a.date));

    let streak = 0;
    let currentDate = new Date();
    currentDate.setHours(0, 0, 0, 0);

    for (let session of sortedSessions) {
        const sessionDate = new Date(session.date);
        sessionDate.setHours(0, 0, 0, 0);

        const diffTime = Math.abs(currentDate - sessionDate);
        const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));

        if (diffDays === 0 || diffDays === 1) {
            streak++;
            currentDate = sessionDate;
            // Move to previous day
            currentDate.setDate(currentDate.getDate() - 1);
        } else {
            break;
        }
    }

    return streak;
}

function updateBodyPartStats(sessions) {
    const bodyPartStatsDiv = document.getElementById('bodyPartStats');
    if (!bodyPartStatsDiv) return;

    if (!sessions || sessions.length === 0) {
        bodyPartStatsDiv.innerHTML = '<div class="empty-state-sm"><i class="fas fa-person"></i><p>No exercise data yet. Start a session to track body performance.</p></div>';
        return;
    }

    const bodyParts = {
        'Shoulder': { reps: 0, sessions: 0, quality: 0, count: 0 },
        'Elbow': { reps: 0, sessions: 0, quality: 0, count: 0 },
        'Knee': { reps: 0, sessions: 0, quality: 0, count: 0 },
        'Hip': { reps: 0, sessions: 0, quality: 0, count: 0 },
        'Neck': { reps: 0, sessions: 0, quality: 0, count: 0 },
        'Wrist': { reps: 0, sessions: 0, quality: 0, count: 0 },
        'Ankle': { reps: 0, sessions: 0, quality: 0, count: 0 },
        'Squat': { reps: 0, sessions: 0, quality: 0, count: 0 },
        'Back': { reps: 0, sessions: 0, quality: 0, count: 0 }
    };

    sessions.forEach(session => {
        const exercise = session.exercise_name || '';
        for (let [part, stats] of Object.entries(bodyParts)) {
            if (exercise.includes(part)) {
                stats.reps += session.total_reps || 0;
                stats.sessions += 1;
                stats.quality += session.quality_score || 0;
                stats.count += 1;
                break;
            }
        }
    });

    // Calculate averages and render
    bodyPartStatsDiv.innerHTML = '';

    let anyData = false;
    for (let [part, stats] of Object.entries(bodyParts)) {
        if (stats.count > 0) {
            anyData = true;
            const avgQuality = (stats.quality / stats.count).toFixed(0);
            const card = document.createElement('div');
            card.className = 'body-part-card';
            card.innerHTML = `
                <h3>${part}</h3>
                <div class="body-part-stat">${stats.reps}</div>
                <div class="body-part-substat">Total Reps</div>
                <div style="margin-top: 0.5rem; font-size: 0.85rem; color: #667eea;">
                    ${stats.sessions} sessions | ${avgQuality}% quality
                </div>
            `;
            bodyPartStatsDiv.appendChild(card);
        }
    }
    if (!anyData) {
        bodyPartStatsDiv.innerHTML = '<div class="empty-state-sm"><i class="fas fa-person"></i><p>No exercise data yet. Start a session to track body performance.</p></div>';
    }
}

function buildExercisePerformanceTable(sessions) {
    const tableBody = document.getElementById('exerciseTableBody');
    const sessionsList = document.getElementById('sessionsList');

    if (!sessions || sessions.length === 0) {
        if (tableBody) tableBody.innerHTML = '<tr><td colspan="6" class="empty-table-cell"><div class="empty-state-sm"><i class="fas fa-clipboard-check"></i><p>No sessions yet. Start exercising to see your progress!</p></div></td></tr>';
        if (sessionsList) sessionsList.innerHTML = '';
        return;
    }

    // Group sessions by exercise
    const exerciseStats = {};
    sessions.forEach(session => {
        const exercise = session.exercise_name;
        if (!exerciseStats[exercise]) {
            exerciseStats[exercise] = {
                name: exercise,
                totalReps: 0,
                bestReps: 0,
                sessionCount: 0,
                totalQuality: 0,
                lastSession: null
            };
        }
        exerciseStats[exercise].totalReps += session.total_reps || 0;
        exerciseStats[exercise].bestReps = Math.max(exerciseStats[exercise].bestReps, session.total_reps || 0);
        exerciseStats[exercise].sessionCount += 1;
        exerciseStats[exercise].totalQuality += session.quality_score || 0;
        if (!exerciseStats[exercise].lastSession || new Date(session.date) > new Date(exerciseStats[exercise].lastSession)) {
            exerciseStats[exercise].lastSession = session.date;
        }
    });

    // Store for sorting
    window.exerciseStatsData = Object.values(exerciseStats);
    renderExerciseTable(window.exerciseStatsData, 'all');
}

function renderExerciseTable(data, category = 'all') {
    const tableBody = document.getElementById('exerciseTableBody');
    tableBody.innerHTML = '';

    // Filter by category
    let filtered = data;
    if (category !== 'all') {
        filtered = data.filter(ex => ex.name.includes(category));
    }

    // Sort by total reps descending
    filtered.sort((a, b) => b.totalReps - a.totalReps);

    filtered.forEach(exercise => {
        const avgQuality = exercise.sessionCount > 0 ? (exercise.totalQuality / exercise.sessionCount) : 0;
        const lastDate = new Date(exercise.lastSession);
        const lastDateStr = lastDate.toLocaleDateString('en-IN', { day: '2-digit', month: 'short', year: 'numeric' });

        const row = document.createElement('tr');
        row.innerHTML = `
            <td class="exercise-name">${exercise.name}</td>
            <td><strong>${exercise.totalReps}</strong></td>
            <td><strong>${exercise.bestReps}</strong></td>
            <td><strong>${exercise.sessionCount}</strong></td>
            <td>
                <span class="quality-bar" style="width: ${avgQuality}px;"></span>
                <span class="quality-percentage">${avgQuality.toFixed(0)}%</span>
            </td>
            <td>${lastDateStr}</td>
        `;
        tableBody.appendChild(row);
    });
}

function generateWeeklyChart(sessions) {
    // Update the existing Chart.js instance created in initCharts()
    const chart = window._weeklyChart;
    if (!chart) return;

    // Reset to zeros if no sessions
    if (!sessions || sessions.length === 0) {
        chart.data.datasets[0].data = [0, 0, 0, 0, 0, 0, 0];
        chart.update();
        return;
    }

    const weekData = { Mon: 0, Tue: 0, Wed: 0, Thu: 0, Fri: 0, Sat: 0, Sun: 0 };
    const dayMap = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];

    // Get last 7 days
    const today = new Date();
    const lastWeek = new Date(today.getTime() - 7 * 24 * 60 * 60 * 1000);

    sessions.forEach(session => {
        const sessionDate = new Date(session.date);
        if (sessionDate >= lastWeek && sessionDate <= today) {
            const dayName = dayMap[sessionDate.getDay()];
            weekData[dayName] += session.total_reps || 0;
        }
    });

    chart.data.datasets[0].data = Object.values(weekData);
    chart.update();
}

function generateQualityChart(sessions) {
    // Update the existing Chart.js instance created in initCharts()
    const chart = window._qualityChart;
    if (!chart) return;

    // Reset to empty if no sessions
    if (!sessions || sessions.length === 0) {
        chart.data.labels = [];
        chart.data.datasets[0].data = [];
        chart.update();
        return;
    }

    // Get last 10 sessions for quality trend
    const recentSessions = [...sessions]
        .sort((a, b) => new Date(b.date) - new Date(a.date))
        .slice(0, 10)
        .reverse();

    chart.data.labels = recentSessions.map(s => {
        const name = s.exercise_name || 'Session';
        return name.length > 12 ? name.substring(0, 12) + '…' : name;
    });
    chart.data.datasets[0].data = recentSessions.map(s => s.quality_score || 0);
    chart.update();
}

/* ── AI Insights — data-driven from real sessions ── */
function updateAIInsights(sessions) {
    const container = document.getElementById('aiInsightsBody');
    if (!container) return;

    if (!sessions || sessions.length === 0) {
        container.innerHTML = '<div class="empty-state-sm"><i class="fas fa-brain"></i><p>Complete some exercise sessions to receive AI-powered insights.</p></div>';
        return;
    }

    const insights = [];

    // Analyze body part improvements
    const bodyPartSessions = {};
    sessions.forEach(s => {
        const name = s.exercise_name || '';
        const parts = ['Shoulder', 'Elbow', 'Knee', 'Hip', 'Neck', 'Wrist', 'Ankle', 'Back'];
        for (const part of parts) {
            if (name.toLowerCase().includes(part.toLowerCase())) {
                if (!bodyPartSessions[part]) bodyPartSessions[part] = [];
                bodyPartSessions[part].push(s);
                break;
            }
        }
    });

    // Check for quality improvements per body part
    for (const [part, partSessions] of Object.entries(bodyPartSessions)) {
        if (partSessions.length >= 2) {
            const sorted = [...partSessions].sort((a, b) => new Date(a.date) - new Date(b.date));
            const first = sorted[0].quality_score || 0;
            const last = sorted[sorted.length - 1].quality_score || 0;
            const diff = last - first;
            if (diff > 5) {
                insights.push({ icon: 'fas fa-lightbulb', cls: 'ai-positive', text: `Your ${part.toLowerCase()} quality improved by ${diff.toFixed(0)}% across ${partSessions.length} sessions. Great progress!` });
            } else if (diff < -5) {
                insights.push({ icon: 'fas fa-exclamation-triangle', cls: 'ai-warning', text: `${part} quality dropped by ${Math.abs(diff).toFixed(0)}% recently. Consider reviewing your form or taking rest days.` });
            }
        }
    }

    // Check consistency
    const uniqueDays = new Set(sessions.map(s => new Date(s.date).toDateString())).size;
    if (uniqueDays >= 3) {
        insights.push({ icon: 'fas fa-check-circle', cls: 'ai-positive', text: `You've exercised on ${uniqueDays} different days. Consistent effort leads to better recovery!` });
    }

    // Check average quality
    const avgQ = sessions.reduce((sum, s) => sum + (s.quality_score || 0), 0) / sessions.length;
    if (avgQ >= 80) {
        insights.push({ icon: 'fas fa-star', cls: 'ai-positive', text: `Excellent average quality of ${avgQ.toFixed(0)}%! Your form is consistently strong.` });
    } else if (avgQ < 50 && sessions.length >= 3) {
        insights.push({ icon: 'fas fa-exclamation-triangle', cls: 'ai-warning', text: `Average quality is ${avgQ.toFixed(0)}%. Focus on proper form — quality over quantity leads to faster recovery.` });
    }

    // Total reps milestone
    const totalReps = sessions.reduce((sum, s) => sum + (s.total_reps || 0), 0);
    if (totalReps >= 100) {
        insights.push({ icon: 'fas fa-trophy', cls: 'ai-positive', text: `Milestone reached: ${totalReps} total reps completed! Keep up the great work.` });
    }

    if (insights.length === 0) {
        insights.push({ icon: 'fas fa-info-circle', cls: '', text: `${sessions.length} session${sessions.length > 1 ? 's' : ''} logged so far. Keep exercising to unlock detailed insights.` });
    }

    container.innerHTML = insights.map(i => `<div class="ai-item ${i.cls}"><i class="${i.icon}"></i><p>${i.text}</p></div>`).join('');
}

/* ── Range of Motion — data-driven from session angles ── */
function updateRangeOfMotion(sessions) {
    const romData = {
        Shoulder: { max: 0, target: 180 },
        Elbow: { max: 0, target: 170 },
        Knee: { max: 0, target: 170 },
        Hip: { max: 0, target: 120 },
    };

    if (sessions && sessions.length > 0) {
        sessions.forEach(s => {
            const name = (s.exercise_name || '').toLowerCase();
            const angle = parseFloat(s.average_joint_angle) || 0;
            if (angle <= 0) return;

            for (const part of Object.keys(romData)) {
                if (name.includes(part.toLowerCase())) {
                    romData[part].max = Math.max(romData[part].max, angle);
                    break;
                }
            }
        });
    }

    for (const [part, data] of Object.entries(romData)) {
        const pct = data.target > 0 ? Math.min((data.max / data.target) * 100, 100) : 0;
        const fillEl = document.getElementById('rom' + part + 'Fill');
        const valEl = document.getElementById('rom' + part + 'Val');
        if (fillEl) fillEl.style.width = pct.toFixed(0) + '%';
        if (valEl) valEl.textContent = `${Math.round(data.max)}° / ${data.target}°`;
    }
}

function filterExerciseTable(button, category) {
    // Update active button
    document.querySelectorAll('.section-filters .filter-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    button.classList.add('active');

    // Render filtered table
    renderExerciseTable(window.exerciseStatsData || [], category);
}

function sortExerciseTable(columnIndex) {
    if (!window.exerciseStatsData) return;

    const sortFunctions = [
        (a, b) => a.name.localeCompare(b.name),
        (a, b) => b.totalReps - a.totalReps,
        (a, b) => b.bestReps - a.bestReps,
        (a, b) => b.sessionCount - a.sessionCount,
        (a, b) => (b.totalQuality / b.sessionCount) - (a.totalQuality / a.sessionCount)
    ];

    if (columnIndex < sortFunctions.length) {
        window.exerciseStatsData.sort(sortFunctions[columnIndex]);
        renderExerciseTable(window.exerciseStatsData, 'all');
    }
}

function displayRecentSessions(sessions, category = 'all') {
    const sessionsList = document.getElementById('sessionsList');
    sessionsList.innerHTML = '';

    // Filter sessions by category if needed
    let filteredSessions = sessions;
    if (category && category !== 'all') {
        filteredSessions = sessions.filter(session => {
            return session.exercise_name.includes(category);
        });
    }

    if (filteredSessions.length === 0) {
        const dateVal = (document.getElementById('sessionDateFilter') || {}).value || '';
        const searchVal = ((document.getElementById('sessionSearch') || {}).value || '').trim();
        if (dateVal) {
            const [year, month, day] = dateVal.split('-').map(Number);
            const displayDate = new Date(year, month - 1, day)
                .toLocaleDateString('en-IN', { day: '2-digit', month: 'long', year: 'numeric' });
            sessionsList.innerHTML = `<div class="session-empty-date"><i class="fas fa-calendar-times"></i><p>No sessions found for <strong>${displayDate}</strong>.</p></div>`;
        } else if (searchVal) {
            sessionsList.innerHTML = `<div class="session-empty-date"><i class="fas fa-search"></i><p>No sessions match "<strong>${searchVal}</strong>".</p></div>`;
        } else {
            sessionsList.innerHTML = '<div class="empty-state"><i class="fas fa-clipboard-check"></i><p>No sessions yet. Start exercising to see your progress!</p></div>';
        }
        return;
    }

    // Sort by date descending
    filteredSessions.sort((a, b) => new Date(b.date) - new Date(a.date));

    filteredSessions.slice(0, 10).forEach((session, index) => {
        const sessionItem = document.createElement('div');
        sessionItem.className = 'session-item';

        const date = new Date(session.date);
        // If the date string has no timezone indicator, treat it as local time
        // by appending 'Z' check — if no 'Z' or offset, parse as-is (local)
        const dateStr = date.toLocaleDateString('en-IN', { day: '2-digit', month: 'short', year: 'numeric' });
        const timeStr = date.toLocaleTimeString('en-IN', { hour: '2-digit', minute: '2-digit', hour12: true });

        // Determine quality indicator
        const quality = session.quality_score || 0;
        let qualityClass = 'quality-poor';
        if (quality >= 80) qualityClass = 'quality-good';
        else if (quality >= 60) qualityClass = 'quality-fair';

        const durationSecs = session.duration_seconds || 0;
        const durationMin = Math.round(durationSecs / 60);

        sessionItem.innerHTML = `
            <div class="session-exercise">${session.exercise_name}</div>
            <div class="session-details">
                <div class="detail-item">
                    <span class="detail-label">Reps:</span>
                    <span class="detail-value">${session.total_reps || 0}</span>
                </div>
                <div class="detail-item">
                    <span class="detail-label">Quality:</span>
                    <span class="detail-value">${quality}%</span>
                </div>
                <div class="detail-item">
                    <span class="detail-label">Angle:</span>
                    <span class="detail-value">${session.average_joint_angle ? session.average_joint_angle.toFixed(1) : 'N/A'}°</span>
                </div>
                <div class="detail-item">
                    <span class="detail-label">Duration:</span>
                    <span class="detail-value">${durationMin}m</span>
                </div>
            </div>
            <div class="session-date">
                <span class="quality-indicator ${qualityClass}"></span>
                ${dateStr} at ${timeStr}
            </div>
        `;

        sessionsList.appendChild(sessionItem);
    });
}

function refreshDashboardData() {
    console.log('Refreshing dashboard data...');
    loadDashboardData();
}

function updateDashboardTimeFilter() {
    const timeFilter = document.getElementById('dashboardTimeFilter').value;
    if (!currentUser || !authToken) return;

    // For now, just reload all data. In future, could filter by date range
    loadDashboardData();
}

function updateSessionSort() {
    applySessionSort(getFilteredSessions());
}

// ── Helpers shared by all session-history filters ──

function getFilteredSessions() {
    const dateVal = (document.getElementById('sessionDateFilter') || {}).value || '';
    const searchVal = ((document.getElementById('sessionSearch') || {}).value || '').toLowerCase().trim();

    let filtered = [...allSessionsData];

    if (dateVal) {
        filtered = filtered.filter(s => {
            const d = new Date(s.date);
            const y = d.getFullYear();
            const m = String(d.getMonth() + 1).padStart(2, '0');
            const day = String(d.getDate()).padStart(2, '0');
            return `${y}-${m}-${day}` === dateVal;
        });
    }

    if (searchVal) {
        filtered = filtered.filter(s =>
            (s.exercise_name || '').toLowerCase().includes(searchVal)
        );
    }

    return filtered;
}

function applySessionSort(sessions) {
    const sortType = (document.getElementById('sessionSort') || {}).value || 'recent';
    const sorted = [...sessions];
    switch (sortType) {
        case 'quality':
            sorted.sort((a, b) => (b.quality_score || 0) - (a.quality_score || 0));
            break;
        case 'reps':
            sorted.sort((a, b) => (b.total_reps || 0) - (a.total_reps || 0));
            break;
        case 'recent':
        default:
            sorted.sort((a, b) => new Date(b.date) - new Date(a.date));
    }
    displayRecentSessions(sorted);
}

function filterSessionsByDate() {
    const picker = document.getElementById('sessionDateFilter');
    const dateVal = picker ? picker.value : '';
    const clearBtn = document.getElementById('clearDateFilter');
    const banner = document.getElementById('dateFilterBanner');
    const label = document.getElementById('dateFilterLabel');

    if (dateVal) {
        const [year, month, day] = dateVal.split('-').map(Number);
        const displayDate = new Date(year, month - 1, day)
            .toLocaleDateString('en-IN', { day: '2-digit', month: 'long', year: 'numeric' });
        if (clearBtn) clearBtn.style.display = '';
        if (banner) banner.style.display = 'flex';
        if (label) label.textContent = `Showing sessions for: ${displayDate}`;
    } else {
        if (clearBtn) clearBtn.style.display = 'none';
        if (banner) banner.style.display = 'none';
    }

    applySessionSort(getFilteredSessions());
}

function clearSessionDateFilter() {
    const picker = document.getElementById('sessionDateFilter');
    if (picker) picker.value = '';
    const clearBtn = document.getElementById('clearDateFilter');
    const banner = document.getElementById('dateFilterBanner');
    if (clearBtn) clearBtn.style.display = 'none';
    if (banner) banner.style.display = 'none';
    applySessionSort(getFilteredSessions());
}

function filterSessionsBySearch() {
    applySessionSort(getFilteredSessions());
}

// ============================================================================
// REPORTS PAGE — connected to real session data
// ============================================================================

// Chart instances so we can destroy before re-creating
let _recoveryChart = null;
let _distributionChart = null;

async function loadReportsData() {
    console.log('📈 loadReportsData called');

    if (!currentUser || !authToken) {
        console.warn('📈 Not authenticated — showing empty reports');
        document.getElementById('rptTotalSessions').textContent = '--';
        document.getElementById('rptDaysActive').textContent = '--';
        document.getElementById('rptQualityAvg').textContent = '--';
        return;
    }

    try {
        // Fetch sessions and stats in parallel
        const [sessionsRes, statsRes] = await Promise.all([
            fetch(`${API_BASE}/sessions`, { headers: { 'Authorization': `Bearer ${authToken}` } }),
            fetch(`${API_BASE}/progress/stats`, { headers: { 'Authorization': `Bearer ${authToken}` } })
        ]);

        if (!sessionsRes.ok || !statsRes.ok) {
            console.error('📈 Failed to fetch reports data', sessionsRes.status, statsRes.status);
            if (sessionsRes.status === 401 || statsRes.status === 401) {
                showNotification('Session expired. Please log in again.', 'warning');
            }
            return;
        }

        const sessions = await sessionsRes.json();
        const stats = await statsRes.json();
        console.log('📈 Reports data loaded:', sessions.length, 'sessions, stats:', stats);

        // ── Summary cards ──
        document.getElementById('rptTotalSessions').textContent =
            stats.total_sessions > 0 ? `${stats.total_sessions} sessions` : '0 sessions';

        document.getElementById('rptDaysActive').textContent =
            stats.days_active > 0 ? `${stats.days_active} days` : '0 days';

        document.getElementById('rptQualityAvg').textContent =
            stats.total_sessions > 0 ? `${stats.avg_quality_score.toFixed(1)}% accuracy` : '0%';

        // Trends
        const setCardTrend = (id, cls, icon, text) => {
            const el = document.getElementById(id);
            if (el) { el.className = 'rpt-trend ' + cls; el.innerHTML = `<i class="fas fa-${icon}"></i> ${text}`; }
        };
        if (stats.total_sessions > 0) {
            setCardTrend('rptWeeklyTrend', 'up', 'arrow-up', `${stats.weekly_reps} reps this week`);
            setCardTrend('rptActiveTrend', 'up', 'arrow-up', stats.days_active > 1 ? 'Consistent' : 'Started');
            const qClass = stats.avg_quality_score >= 70 ? 'up' : stats.avg_quality_score >= 40 ? 'neutral' : 'down';
            const qIcon  = stats.avg_quality_score >= 70 ? 'arrow-up' : stats.avg_quality_score >= 40 ? 'minus' : 'arrow-down';
            const qText  = stats.avg_quality_score >= 70 ? 'Great form' : stats.avg_quality_score >= 40 ? 'Fair' : 'Needs work';
            setCardTrend('rptQualityTrend', qClass, qIcon, qText);
        }

        // ── Recovery Progress Chart (quality over time) ──
        buildRecoveryChart(sessions);

        // ── Exercise Distribution Doughnut ──
        buildDistributionChart(stats.exercises_completed);

        // ── AI Report ──
        buildAIReport(sessions, stats);

    } catch (err) {
        console.error('📈 Error loading reports:', err);
    }
}

function buildRecoveryChart(sessions) {
    if (!sessions || sessions.length === 0) return;

    const rCtx = document.getElementById('recoveryProgressChart');
    if (!rCtx) return;

    // Destroy old instance
    if (_recoveryChart) { _recoveryChart.destroy(); _recoveryChart = null; }

    // Group sessions by date and average quality
    const sorted = [...sessions].sort((a, b) => new Date(a.date) - new Date(b.date));
    const byDate = {};
    sorted.forEach(s => {
        const d = new Date(s.date).toLocaleDateString('en-IN', { day: '2-digit', month: 'short' });
        if (!byDate[d]) byDate[d] = { sum: 0, count: 0 };
        byDate[d].sum += (s.quality_score || 0);
        byDate[d].count += 1;
    });

    const labels = Object.keys(byDate);
    const data = labels.map(l => +(byDate[l].sum / byDate[l].count).toFixed(1));

    const colors = {
        primary: '#667eea',
        primaryLight: 'rgba(102,126,234,0.15)'
    };

    _recoveryChart = new Chart(rCtx.getContext('2d'), {
        type: 'line',
        data: {
            labels,
            datasets: [{
                label: 'Quality %',
                data,
                borderColor: colors.primary,
                backgroundColor: colors.primaryLight,
                fill: true,
                tension: 0.4,
                pointBackgroundColor: '#fff',
                pointBorderColor: colors.primary,
                pointBorderWidth: 2,
                pointRadius: 4,
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: { beginAtZero: true, max: 100, ticks: { callback: v => v + '%' } }
            },
            plugins: { legend: { display: false } }
        }
    });
}

function buildDistributionChart(exercises) {
    const eCtx = document.getElementById('exerciseDistributionChart');
    if (!eCtx) return;

    if (_distributionChart) { _distributionChart.destroy(); _distributionChart = null; }

    if (!exercises || exercises.length === 0) return;

    // Categorize exercises by body part
    const partMap = {};
    exercises.forEach(ex => {
        const name = ex.name || '';
        let part = 'Other';
        const parts = ['Shoulder', 'Knee', 'Hip', 'Neck', 'Elbow', 'Wrist', 'Ankle', 'Squat', 'Back'];
        for (const p of parts) {
            if (name.includes(p)) { part = p; break; }
        }
        partMap[part] = (partMap[part] || 0) + ex.total_reps;
    });

    const labels = Object.keys(partMap);
    const data = Object.values(partMap);
    const palette = ['#667eea', '#48bb78', '#9f7aea', '#ed8936', '#38b2ac', '#fc8181', '#63b3ed', '#f6e05e', '#b794f4'];

    _distributionChart = new Chart(eCtx.getContext('2d'), {
        type: 'doughnut',
        data: {
            labels,
            datasets: [{
                data,
                backgroundColor: palette.slice(0, labels.length),
                borderWidth: 0,
                hoverOffset: 8,
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            cutout: '65%',
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: { font: { size: 12 }, padding: 16, usePointStyle: true, pointStyle: 'circle' }
                },
                tooltip: {
                    callbacks: { label: ctx => ` ${ctx.label}: ${ctx.parsed} reps` }
                }
            }
        }
    });
}

function buildAIReport(sessions, stats) {
    const body = document.getElementById('aiReportBody');
    if (!body) return;

    if (!sessions || sessions.length === 0) {
        body.innerHTML = '<div class="air-section"><h4>Executive Summary</h4><p>No session data available yet. Complete some exercises to generate your AI recovery report.</p></div>';
        return;
    }

    // Compute report data
    const totalSessions = stats.total_sessions;
    const avgQuality = stats.avg_quality_score;
    const avgPosture = stats.avg_posture_correctness;
    const daysActive = stats.days_active;
    const totalReps = stats.total_reps;
    const exercisesList = stats.exercises_completed || [];
    const bestExercise = stats.best_exercise || 'N/A';
    const weeklyReps = stats.weekly_reps;

    // Determine progress level
    const progressLevel = avgQuality >= 80 ? 'excellent' : avgQuality >= 60 ? 'good' : avgQuality >= 40 ? 'moderate' : 'early';
    const progressText = { excellent: 'progressing excellently', good: 'progressing well', moderate: 'showing steady improvement', early: 'in its early stages' }[progressLevel];

    // Find strongest and weakest exercise categories
    let strongest = null, weakest = null;
    if (exercisesList.length > 0) {
        strongest = exercisesList.reduce((a, b) => (a.avg_quality || 0) > (b.avg_quality || 0) ? a : b);
        weakest = exercisesList.reduce((a, b) => (a.avg_quality || 0) < (b.avg_quality || 0) ? a : b);
    }

    // Build findings
    let findings = '';
    if (avgQuality >= 70)       findings += `<li><i class="fas fa-check-circle t-green"></i> Average quality score is strong at ${avgQuality.toFixed(1)}%</li>`;
    else if (avgQuality >= 40)  findings += `<li><i class="fas fa-exclamation-circle t-orange"></i> Average quality score is fair at ${avgQuality.toFixed(1)}% — focus on form</li>`;
    else                        findings += `<li><i class="fas fa-times-circle t-red"></i> Average quality score is low at ${avgQuality.toFixed(1)}% — slow down and prioritize correct form</li>`;

    findings += `<li><i class="fas fa-check-circle t-green"></i> Exercise consistency: ${daysActive} active day${daysActive !== 1 ? 's' : ''} across ${totalSessions} session${totalSessions !== 1 ? 's' : ''}</li>`;

    if (strongest && strongest.name !== (weakest && weakest.name)) {
        findings += `<li><i class="fas fa-check-circle t-green"></i> Strongest exercise: ${strongest.name} (${strongest.avg_quality.toFixed(1)}% quality)</li>`;
        if (weakest) findings += `<li><i class="fas fa-exclamation-circle t-orange"></i> Needs improvement: ${weakest.name} (${weakest.avg_quality.toFixed(1)}% quality)</li>`;
    }

    if (avgPosture >= 70)      findings += `<li><i class="fas fa-info-circle t-blue"></i> Posture correctness is good at ${avgPosture.toFixed(1)}%</li>`;
    else if (avgPosture > 0)   findings += `<li><i class="fas fa-exclamation-circle t-orange"></i> Posture correctness at ${avgPosture.toFixed(1)}% — pay attention to alignment</li>`;

    // Build recommendations
    let recs = '';
    if (weeklyReps < 50)       recs += `<li><i class="fas fa-arrow-right t-blue"></i> Aim for at least 50 reps per week to build consistency (currently ${weeklyReps})</li>`;
    if (weakest && weakest.avg_quality < 70) recs += `<li><i class="fas fa-arrow-right t-blue"></i> Focus on ${weakest.name} — practice with slower, controlled movements</li>`;
    if (exercisesList.length < 3) recs += `<li><i class="fas fa-arrow-right t-blue"></i> Add variety — try at least 3 different exercise types for balanced recovery</li>`;
    if (exercisesList.length >= 3) recs += `<li><i class="fas fa-arrow-right t-blue"></i> Great variety with ${exercisesList.length} exercises — maintain this balance</li>`;
    if (avgQuality < 80)       recs += `<li><i class="fas fa-arrow-right t-blue"></i> Target quality scores above 80% before increasing reps</li>`;
    if (avgQuality >= 80)      recs += `<li><i class="fas fa-arrow-right t-blue"></i> Quality is excellent — consider increasing reps or adding more challenging exercises</li>`;

    body.innerHTML = `
        <div class="air-section"><h4>Executive Summary</h4><p>Based on your ${totalSessions} session${totalSessions !== 1 ? 's' : ''} over ${daysActive} day${daysActive !== 1 ? 's' : ''}, rehabilitation is ${progressText}. Best performing exercise is <strong>${bestExercise}</strong> with ${totalReps} total reps completed.</p></div>
        <div class="air-section"><h4>Key Findings</h4><ul class="air-list">${findings}</ul></div>
        <div class="air-section"><h4>Recommendations</h4><ul class="air-list">${recs}</ul></div>
    `;
}

// ============================================================================
// REHAB PLAN PAGE — connected to real session data
// ============================================================================

async function loadRehabPlanData() {
    console.log('🏥 loadRehabPlanData called — loading selector options');
    initRehabSelector();
}

// ================================================================
//  REHABILITATION PLAN — Selector & Generator
// ================================================================

let _rehabSelectedLocation = null;
let _rehabSelectedGoals = new Set();
let _rehabSelectedDifficulty = 'Beginner';

async function initRehabSelector() {
    const injuryGrid = document.getElementById('injuryGrid');
    const goalGrid = document.getElementById('goalGrid');
    if (!injuryGrid || !goalGrid) return;

    try {
        const res = await fetch(`${API_BASE}/rehab-plan/options`);
        if (!res.ok) throw new Error('Failed to load options');
        const data = await res.json();

        // Render injury location cards
        injuryGrid.innerHTML = data.injury_locations.map(loc => `
            <div class="injury-card" data-location="${loc.id}" onclick="selectInjuryLocation(this, '${loc.id}')">
                <div class="injury-card-icon"><i class="fas ${loc.icon}"></i></div>
                <h3>${loc.label}</h3>
                <p>${loc.description}</p>
            </div>
        `).join('');

        // Render goal cards
        goalGrid.innerHTML = data.rehab_goals.map(g => `
            <div class="goal-card" data-goal="${g.id}" onclick="toggleRehabGoal(this, '${g.id}')">
                <div class="goal-card-icon"><i class="fas ${g.icon}"></i></div>
                <h3>${g.label}</h3>
                <p>${g.description}</p>
            </div>
        `).join('');

        // Difficulty pills
        document.querySelectorAll('.diff-pill').forEach(pill => {
            pill.addEventListener('click', () => {
                document.querySelectorAll('.diff-pill').forEach(p => p.classList.remove('active'));
                pill.classList.add('active');
                _rehabSelectedDifficulty = pill.dataset.diff;
            });
        });

        // Generate button
        document.getElementById('generatePlanBtn').addEventListener('click', generateRehabPlan);

    } catch (err) {
        console.error('Error loading rehab options', err);
        injuryGrid.innerHTML = '<p style="color:var(--text-secondary);padding:1rem;">Failed to load options. Make sure the backend is running.</p>';
    }
}

function selectInjuryLocation(el, locationId) {
    document.querySelectorAll('.injury-card').forEach(c => c.classList.remove('selected'));
    el.classList.add('selected');
    _rehabSelectedLocation = locationId;
    updateGenerateButton();
}

function toggleRehabGoal(el, goalId) {
    if (_rehabSelectedGoals.has(goalId)) {
        _rehabSelectedGoals.delete(goalId);
        el.classList.remove('selected');
    } else {
        _rehabSelectedGoals.add(goalId);
        el.classList.add('selected');
    }
    updateGenerateButton();
}

function updateGenerateButton() {
    const btn = document.getElementById('generatePlanBtn');
    const hint = document.getElementById('generateHint');
    const ready = _rehabSelectedLocation && _rehabSelectedGoals.size > 0;
    btn.disabled = !ready;
    if (ready) {
        hint.textContent = `Ready to generate a plan for ${_rehabSelectedLocation} — ${_rehabSelectedGoals.size} goal(s) selected`;
        hint.style.color = 'var(--green)';
    } else if (_rehabSelectedLocation) {
        hint.textContent = 'Now select at least one rehabilitation goal';
        hint.style.color = 'var(--text-secondary)';
    } else {
        hint.textContent = 'Please select an injury location and at least one goal';
        hint.style.color = 'var(--text-secondary)';
    }
}

async function generateRehabPlan() {
    const btn = document.getElementById('generatePlanBtn');
    btn.disabled = true;
    btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Generating Plan...';

    try {
        const res = await fetch(`${API_BASE}/rehab-plan`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                injury_location: _rehabSelectedLocation,
                rehab_goals: Array.from(_rehabSelectedGoals),
                difficulty: _rehabSelectedDifficulty,
            })
        });

        if (!res.ok) {
            const err = await res.json();
            throw new Error(err.detail || 'Failed to generate plan');
        }

        const plan = await res.json();
        renderRehabPlan(plan);

    } catch (err) {
        console.error('Error generating rehab plan:', err);
        showNotification('Failed to generate plan: ' + err.message, 'error');
    } finally {
        btn.disabled = false;
        btn.innerHTML = '<i class="fas fa-magic"></i> Generate My Rehab Plan';
    }
}

function renderRehabPlan(plan) {
    // Hide selector, show result
    document.getElementById('rehabSelector').style.display = 'none';
    const resultDiv = document.getElementById('rehabPlanResult');
    resultDiv.style.display = 'block';

    // Title & overview
    document.getElementById('planTitle').textContent = plan.plan_name;
    document.getElementById('planOverview').textContent = plan.overview;

    // Summary cards
    const totalExercises = plan.days.reduce((sum, d) => sum + d.exercises.length, 0);
    const totalSets = plan.days.reduce((sum, d) => sum + d.exercises.reduce((s, e) => s + e.sets, 0), 0);
    const summaryHTML = `
        <div class="ps-card ps-blue"><div class="ps-icon"><i class="fas fa-map-marker-alt"></i></div><div class="ps-body"><span class="ps-val">${plan.injury_location}</span><span class="ps-label">Injury Area</span></div></div>
        <div class="ps-card ps-teal"><div class="ps-icon"><i class="fas fa-calendar-alt"></i></div><div class="ps-body"><span class="ps-val">${plan.days.length} Days</span><span class="ps-label">Plan Duration</span></div></div>
        <div class="ps-card ps-purple"><div class="ps-icon"><i class="fas fa-dumbbell"></i></div><div class="ps-body"><span class="ps-val">${totalExercises}</span><span class="ps-label">Total Exercises</span></div></div>
        <div class="ps-card ps-green"><div class="ps-icon"><i class="fas fa-layer-group"></i></div><div class="ps-body"><span class="ps-val">${plan.difficulty}</span><span class="ps-label">Difficulty</span></div></div>
        <div class="ps-card ps-orange"><div class="ps-icon"><i class="fas fa-redo"></i></div><div class="ps-body"><span class="ps-val">${totalSets}</span><span class="ps-label">Total Sets</span></div></div>
    `;
    document.getElementById('planSummaryCards').innerHTML = summaryHTML;

    // Fetch existing rehab sessions to determine status
    loadRehabStatus(plan);

    // Scroll to top
    resultDiv.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

/**
 * Load rehabilitation status and render the plan with proper status indicators
 */
async function loadRehabStatus(plan) {
    let rehabSessions = {};
    
    if (currentUser && authToken) {
        try {
            const response = await fetch(`${API_BASE}/rehab-sessions`, {
                headers: { 'Authorization': `Bearer ${authToken}` }
            });
            if (response.ok) {
                const sessions = await response.json();
                // Index sessions by exercise_name-day for quick lookup
                sessions.forEach(session => {
                    const key = `${session.exercise_name}-${session.day}`;
                    rehabSessions[key] = session;
                });
                console.log('Loaded rehab sessions:', Object.keys(rehabSessions).length);
            }
        } catch (error) {
            console.warn('Could not load rehab sessions:', error);
        }
    }
    
    renderRehabPlanWithStatus(plan, rehabSessions);
}

/**
 * Render rehabilitation plan with exercise status indicators and action buttons
 */
function renderRehabPlanWithStatus(plan, rehabSessions) {
    let daysHTML = '';
    
    plan.days.forEach(day => {
        let exRows = '';
        let dayCompleted = 0;
        let dayTotal = day.exercises.length;
        
        day.exercises.forEach((ex, i) => {
            const holdText = ex.hold_seconds ? ` · Hold ${ex.hold_seconds}s` : '';
            const sessionKey = `${ex.name}-${day.day}`;
            const sessionData = rehabSessions[sessionKey];
            
            // Determine status
            let status = 'pending';
            let statusIcon = 'circle';
            let statusClass = 'status-pending';
            let statusText = 'Pending';
            
            if (sessionData) {
                status = sessionData.status;
                if (status === 'completed') {
                    statusIcon = 'check-circle';
                    statusClass = 'status-completed';
                    statusText = '✔ Completed';
                    dayCompleted++;
                } else if (status === 'incomplete') {
                    statusIcon = 'times-circle';
                    statusClass = 'status-incomplete';
                    statusText = '❌ Incomplete';
                } else if (status === 'skipped') {
                    statusIcon = 'minus-circle';
                    statusClass = 'status-skipped';
                    statusText = '⊘ Skipped';
                }
            }
            
            exRows += `
                <div class="plan-exercise-row">
                    <div class="plan-ex-num">${i + 1}</div>
                    <div class="plan-ex-info">
                        <h4>${ex.name}</h4>
                        <p class="plan-ex-desc">${ex.description}</p>
                        ${ex.notes ? `<p class="plan-ex-notes"><i class="fas fa-info-circle"></i> ${ex.notes}</p>` : ''}
                    </div>
                    <div class="plan-ex-stats">
                        <span class="plan-ex-badge badge-sets"><i class="fas fa-redo"></i> ${ex.sets} Sets</span>
                        <span class="plan-ex-badge badge-reps"><i class="fas fa-hashtag"></i> ${ex.reps} Reps</span>
                        ${holdText ? `<span class="plan-ex-badge badge-hold"><i class="fas fa-stopwatch"></i>${holdText.replace(' · Hold ', '')} Hold</span>` : ''}
                        <span class="plan-ex-badge badge-rest"><i class="fas fa-pause"></i> ${ex.rest_seconds}s Rest</span>
                    </div>
                    <div class="plan-ex-actions">
                        <span class="plan-ex-status ${statusClass}"><i class="fas fa-${statusIcon}"></i> ${statusText}</span>
                        <button class="btn btn-primary btn-sm" onclick="startRehabExercise('${ex.name}', ${day.day}, '${plan.plan_name}')">
                            <i class="fas fa-play"></i> Start
                        </button>
                    </div>
                </div>`;
        });

        // Color coding for focus
        const focusColor = {
            'Pain Reduction': 'focus-red',
            'Increase ROM': 'focus-blue',
            'Strength Building': 'focus-purple',
            'Daily Mobility': 'focus-green'
        }[day.focus] || 'focus-blue';
        
        // Calculate day progress percentage
        const dayProgress = Math.round((dayCompleted / dayTotal) * 100);

        daysHTML += `
            <div class="plan-day-card">
                <div class="plan-day-header ${focusColor}">
                    <div class="plan-day-num">Day ${day.day}</div>
                    <div class="plan-day-info">
                        <h3>${day.title}</h3>
                        <p class="plan-day-goal"><i class="fas fa-bullseye"></i> ${day.daily_goal}</p>
                    </div>
                    <span class="plan-day-focus-badge ${focusColor}">${day.focus}</span>
                </div>
                <div class="plan-day-progress">
                    <div class="progress-info">
                        <span class="progress-label">Day Progress</span>
                        <span class="progress-value">${dayCompleted}/${dayTotal} exercises</span>
                    </div>
                    <div class="progress-bar">
                        <div class="progress-fill" style="width: ${dayProgress}%"></div>
                    </div>
                    <span class="progress-percentage">${dayProgress}%</span>
                </div>
                <div class="plan-day-exercises">${exRows}</div>
            </div>`;
    });
    document.getElementById('planDays').innerHTML = daysHTML;
}

/**
 * Start an exercise from the rehab plan
 */
function startRehabExercise(exerciseName, day, planName) {
    console.log(`📋 Starting rehab exercise: ${exerciseName} (Day ${day}) from plan: ${planName}`);
    
    // Set current exercise
    currentExercise = exerciseName;
    selectedExercise = exerciseName;
    
    // Store rehab context for tracking
    window._rehabContext = {
        exerciseName: exerciseName,
        day: day,
        planName: planName
    };
    
    // Start the exercise with camera tracking
    showPage('exercise');
    startCamera();
}

/**
 * Update rehab session status after exercise completion
 */
async function updateRehabSessionStatus(exerciseName, reps, quality, status) {
    if (!window._rehabContext || !currentUser || !authToken) {
        console.warn('Cannot update rehab status: missing context or auth');
        return;
    }
    
    const ctx = window._rehabContext;
    const sessionKey = `${exerciseName}-${ctx.day}`;
    
    try {
        // First, try to find existing session
        const getResponse = await fetch(`${API_BASE}/rehab-sessions`, {
            headers: { 'Authorization': `Bearer ${authToken}` }
        });
        
        if (!getResponse.ok) return;
        
        const sessions = await getResponse.json();
        const existingSession = sessions.find(s => s.exercise_name === exerciseName && s.day === ctx.day);
        
        if (existingSession) {
            // Update existing session
            const updateResponse = await fetch(`${API_BASE}/rehab-sessions/${existingSession.id}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${authToken}`
                },
                body: JSON.stringify({
                    reps_done: reps,
                    quality_score: quality,
                    status: status,
                    notes: `Completed from rehab plan: ${ctx.planName}`
                })
            });
            
            if (updateResponse.ok) {
                console.log(`✅ Rehab session updated: ${exerciseName} - Status: ${status}`);
            }
        } else {
            // Create new session
            const createResponse = await fetch(`${API_BASE}/rehab-sessions`, {
                method:  'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${authToken}`
                },
                body: JSON.stringify({
                    exercise_name: exerciseName,
                    day: ctx.day,
                    target_reps: 10, // Default, would be from plan
                    reps_done: reps,
                    quality_score: quality,
                    status: status,
                    notes: `Completed from rehab plan: ${ctx.planName}`
                })
            });
            
            if (createResponse.ok) {
                console.log(`✅ Rehab session created: ${exerciseName} - Status: ${status}`);
            }
        }
    } catch (error) {
        console.error('Error updating rehab session:', error);
    }
}

function showRehabSelector() {
    document.getElementById('rehabPlanResult').style.display = 'none';
    document.getElementById('rehabSelector').style.display = 'block';
}

function printRehabPlan() {
    window.print();
}


function filterSessionsByCategory(button, category) {
    if (button) {
        document.querySelectorAll('.session-filters .filter-btn, .filter-btn').forEach(btn => {
            btn.classList.remove('active');
        });
        button.classList.add('active');
    }
    displayRecentSessions(allSessionsData, category);
}

// ================================================================
//   AI CHATBOT (Full Page + Shared Logic)
// ================================================================

/**
 * Gather current exercise session context for the chatbot.
 */
function getChatContext() {
    return {
        exercise: currentExercise || null,
        rep_count: exerciseData ? String(exerciseData.reps || '') : '',
        quality_score: exerciseData ? String(exerciseData.quality || '') : '',
        joint_angle: exerciseData ? String(exerciseData.angle || '') : '',
        posture_feedback: exerciseData ? (exerciseData.posture || '') : '',
    };
}

/**
 * Convert markdown-like formatting to HTML.
 */
function formatChatMarkdown(text) {
    if (!text) return '';
    let html = text
        .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')    // bold
        .replace(/\*(.+?)\*/g, '<em>$1</em>')                 // italic
        .replace(/`(.+?)`/g, '<code>$1</code>')               // inline code
        .replace(/^(\d+)\.\s+(.+)$/gm, '<li>$2</li>')         // numbered list
        .replace(/^[•\-]\s+(.+)$/gm, '<li>$1</li>');          // bullet list

    // Wrap consecutive <li> in <ul>
    html = html.replace(/((?:<li>.*?<\/li>\s*)+)/g, '<ul>$1</ul>');
    // Convert newlines to <br> (except inside lists)
    html = html.replace(/\n/g, '<br>');
    // Clean up <br> right after/before <ul>
    html = html.replace(/<br><ul>/g, '<ul>').replace(/<\/ul><br>/g, '</ul>');
    return html;
}

/**
 * Send message from the full-page chatbot.
 */
async function sendChatMessage() {
    const input = document.getElementById('chatInput');
    const message = input.value.trim();
    if (!message) return;

    addChatMessage(message, 'user');
    input.value = '';
    updateChatContextBar();
    showTypingIndicator('chatMessages');

    try {
        const ctx = getChatContext();
        const response = await fetch(`${API_BASE}/chat`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                user_message: message,
                exercise: ctx.exercise,
                rep_count: ctx.rep_count,
                quality_score: ctx.quality_score,
                joint_angle: ctx.joint_angle,
                posture_feedback: ctx.posture_feedback,
            })
        });
        removeTypingIndicator('chatMessages');

        if (response.ok) {
            const data = await response.json();
            addChatMessage(data.response, 'bot');
        } else {
            addChatMessage('Sorry, I encountered an error. Please try again.', 'bot');
        }
    } catch (error) {
        removeTypingIndicator('chatMessages');
        console.error('Chatbot error:', error);
        addChatMessage('Sorry, I encountered an error. Please check your connection and try again.', 'bot');
    }
}

/**
 * Add a message bubble to a chat container.
 */
function addChatMessage(message, sender, containerId = 'chatMessages') {
    const container = document.getElementById(containerId);
    if (!container) return;
    const div = document.createElement('div');
    div.className = `message ${sender}-message`;
    const icon = sender === 'bot' ? 'fa-robot' : 'fa-user';
    const formattedMsg = sender === 'bot' ? formatChatMarkdown(message) : escapeHTMLChat(message);
    div.innerHTML = `
        <div class="msg-avatar"><i class="fas ${icon}"></i></div>
        <div class="message-content">${formattedMsg}</div>
    `;
    container.appendChild(div);
    container.scrollTop = container.scrollHeight;
}

function escapeHTMLChat(str) {
    const div = document.createElement('div');
    div.textContent = str;
    return div.innerHTML;
}

/**
 * Show typing indicator dots.
 */
function showTypingIndicator(containerId) {
    const container = document.getElementById(containerId);
    if (!container) return;
    // Remove any existing indicator
    removeTypingIndicator(containerId);
    const div = document.createElement('div');
    div.className = 'message bot-message';
    div.id = `typing-${containerId}`;
    div.innerHTML = `
        <div class="msg-avatar"><i class="fas fa-robot"></i></div>
        <div class="message-content">
            <div class="typing-indicator"><div class="dot"></div><div class="dot"></div><div class="dot"></div></div>
        </div>
    `;
    container.appendChild(div);
    container.scrollTop = container.scrollHeight;
}

function removeTypingIndicator(containerId) {
    const el = document.getElementById(`typing-${containerId}`);
    if (el) el.remove();
}

/**
 * Update the context bar showing current session data.
 */
function updateChatContextBar() {
    const bar = document.getElementById('chatContextBar');
    if (!bar) return;
    const ctx = getChatContext();
    const chips = [];
    if (ctx.exercise) chips.push(`<span class="ctx-chip ctx-exercise"><i class="fas fa-dumbbell"></i> ${ctx.exercise}</span>`);
    if (ctx.rep_count) chips.push(`<span class="ctx-chip ctx-reps"><i class="fas fa-redo-alt"></i> ${ctx.rep_count} reps</span>`);
    if (ctx.quality_score) chips.push(`<span class="ctx-chip ctx-quality"><i class="fas fa-star"></i> ${ctx.quality_score}% quality</span>`);
    if (ctx.joint_angle) chips.push(`<span class="ctx-chip ctx-angle"><i class="fas fa-drafting-compass"></i> ${ctx.joint_angle}°</span>`);
    if (chips.length > 0) {
        bar.innerHTML = chips.join('');
        bar.style.display = 'flex';
    } else {
        bar.style.display = 'none';
    }
}

// Quick message helpers (full page)
function sendQuickMessage(msg) {
    const input = document.getElementById('chatInput');
    if (input) input.value = msg;
    sendChatMessage();
}

async function askExerciseList() {
    sendQuickMessage('List all exercises');
}

async function askSafetyTip() {
    try {
        const resp = await fetch(`${API_BASE}/chatbot/safety-tip`);
        if (resp.ok) {
            const data = await resp.json();
            addChatMessage(data.tip, 'bot');
        }
    } catch (e) {
        console.error('Safety tip error:', e);
    }
}

function askPostureTips() {
    sendQuickMessage('Give me posture tips');
}

async function askMotivation() {
    try {
        const resp = await fetch(`${API_BASE}/chatbot/motivation`);
        if (resp.ok) {
            const data = await resp.json();
            addChatMessage(data.message, 'bot');
        }
    } catch (e) {
        addChatMessage("Keep up the great work! Every rep counts toward your recovery.", 'bot');
    }
}

function clearChatHistory() {
    const container = document.getElementById('chatMessages');
    if (container) {
        container.innerHTML = `
            <div class="message bot-message">
                <div class="msg-avatar"><i class="fas fa-robot"></i></div>
                <div class="message-content"><p>Chat cleared. How can I help you?</p></div>
            </div>
        `;
    }
}

// ================================================================
//   VOICE INPUT FOR CHATBOT
// ================================================================
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

/* ================================================================
   SETTINGS PAGE – Full Implementation
   ================================================================ */
(function initSettingsPage() {

    /* ── State ── */
    const STG_KEY = 'physio_settings';
    let stgDefaults = {
        displayName: '', email: '',
        injury: '', goal: '', age: '', height: '', weight: '', dominantSide: '',
        aiCoaching: true, adaptiveRehab: true, difficulty: 'beginner',
        voiceEnabled: false, voiceSpeed: 0.9, voiceVolume: 0.8,
        cameraId: '', skeletonOverlay: true, sensitivity: 3,
        exerciseReminders: true, rehabAlerts: true, emailNotifs: false,
        darkMode: false, compactSidebar: false, fontSize: 'medium',
        avatarData: ''
    };
    let stgCurrent = {};
    let stgSaved = {};
    let stgDirty = false;

    /* ── Load from localStorage ── */
    function loadSettings() {
        try {
            const raw = localStorage.getItem(STG_KEY);
            stgSaved = raw ? { ...stgDefaults, ...JSON.parse(raw) } : { ...stgDefaults };
        } catch { stgSaved = { ...stgDefaults }; }
        stgCurrent = { ...stgSaved };
        applyToDOM(stgCurrent);
        applyLiveSettings(stgCurrent);
        setDirty(false);
    }

    /* ── Persist ── */
    function persistSettings() {
        localStorage.setItem(STG_KEY, JSON.stringify(stgCurrent));
        stgSaved = { ...stgCurrent };
        setDirty(false);
        flashSavedIndicator();
    }

    /* ── Apply values to form elements ── */
    function applyToDOM(s) {
        setVal('settingsName', s.displayName);
        setVal('settingsEmail', s.email);
        setVal('settingsInjury', s.injury);
        setVal('settingsGoal', s.goal);
        setVal('stgAge', s.age);
        setVal('stgHeight', s.height);
        setVal('stgWeight', s.weight);
        setVal('stgDominantSide', s.dominantSide);
        setChecked('stgAiCoaching', s.aiCoaching);
        setChecked('stgAdaptiveRehab', s.adaptiveRehab);
        setChecked('voiceEnabled', s.voiceEnabled);
        setVal('voiceSpeed', s.voiceSpeed);
        setVal('voiceVolume', s.voiceVolume);
        setVal('stgCamera', s.cameraId);
        setChecked('stgSkeletonOverlay', s.skeletonOverlay);
        setVal('stgSensitivity', s.sensitivity);
        setChecked('stgExerciseReminders', s.exerciseReminders);
        setChecked('stgRehabAlerts', s.rehabAlerts);
        setChecked('stgEmailNotifs', s.emailNotifs);
        setChecked('darkMode', s.darkMode);
        setChecked('compactSidebar', s.compactSidebar);

        // difficulty buttons
        document.querySelectorAll('.stg-diff-btn').forEach(b => {
            b.classList.toggle('active', b.dataset.diff === s.difficulty);
        });
        // font size buttons
        document.querySelectorAll('.stg-font-btn').forEach(b => {
            b.classList.toggle('active', b.dataset.size === s.fontSize);
        });
        // slider displays
        updateSliderDisplays();
        // avatar
        if (s.avatarData) {
            const img = document.getElementById('stgAvatarImg');
            if (img) { img.src = s.avatarData; img.style.display = 'block'; }
            const icon = document.querySelector('#stgAvatar > i');
            if (icon) icon.style.display = 'none';
        }
    }

    /* ── Read DOM into stgCurrent ── */
    function readFromDOM() {
        stgCurrent.displayName = getVal('settingsName');
        stgCurrent.email = getVal('settingsEmail');
        stgCurrent.injury = getVal('settingsInjury');
        stgCurrent.goal = getVal('settingsGoal');
        stgCurrent.age = getVal('stgAge');
        stgCurrent.height = getVal('stgHeight');
        stgCurrent.weight = getVal('stgWeight');
        stgCurrent.dominantSide = getVal('stgDominantSide');
        stgCurrent.aiCoaching = getChecked('stgAiCoaching');
        stgCurrent.adaptiveRehab = getChecked('stgAdaptiveRehab');
        stgCurrent.voiceEnabled = getChecked('voiceEnabled');
        stgCurrent.voiceSpeed = parseFloat(getVal('voiceSpeed')) || 0.9;
        stgCurrent.voiceVolume = parseFloat(getVal('voiceVolume')) || 0.8;
        stgCurrent.cameraId = getVal('stgCamera');
        stgCurrent.skeletonOverlay = getChecked('stgSkeletonOverlay');
        stgCurrent.sensitivity = parseInt(getVal('stgSensitivity')) || 3;
        stgCurrent.exerciseReminders = getChecked('stgExerciseReminders');
        stgCurrent.rehabAlerts = getChecked('stgRehabAlerts');
        stgCurrent.emailNotifs = getChecked('stgEmailNotifs');
        stgCurrent.darkMode = getChecked('darkMode');
        stgCurrent.compactSidebar = getChecked('compactSidebar');
    }

    /* ── Apply live settings (theme, font, etc.) ── */
    function applyLiveSettings(s) {
        document.body.classList.toggle('dark-mode', !!s.darkMode);
        document.body.classList.toggle('compact-sidebar', !!s.compactSidebar);
        document.documentElement.style.fontSize =
            s.fontSize === 'small' ? '14px' : s.fontSize === 'large' ? '17px' : '15.5px';
    }

    /* ── Dirty tracking ── */
    function setDirty(dirty) {
        stgDirty = dirty;
        const bar = document.getElementById('stgSaveBar');
        if (bar) bar.classList.toggle('visible', dirty);
    }
    function checkDirty() {
        readFromDOM();
        const dirty = JSON.stringify(stgCurrent) !== JSON.stringify(stgSaved);
        setDirty(dirty);
    }

    /* ── Helpers ── */
    function setVal(id, v) { const el = document.getElementById(id); if (el) el.value = v ?? ''; }
    function getVal(id) { const el = document.getElementById(id); return el ? el.value : ''; }
    function setChecked(id, v) { const el = document.getElementById(id); if (el) el.checked = !!v; }
    function getChecked(id) { const el = document.getElementById(id); return el ? el.checked : false; }

    function updateSliderDisplays() {
        const speedEl = document.getElementById('voiceSpeedVal');
        const volEl = document.getElementById('voiceVolumeVal');
        const sensEl = document.getElementById('stgSensitivityVal');
        const speed = document.getElementById('voiceSpeed');
        const vol = document.getElementById('voiceVolume');
        const sens = document.getElementById('stgSensitivity');
        if (speedEl && speed) speedEl.textContent = parseFloat(speed.value).toFixed(1) + '×';
        if (volEl && vol) volEl.textContent = Math.round(parseFloat(vol.value) * 100) + '%';
        if (sensEl && sens) {
            const labels = ['Very Low','Low','Medium','High','Very High'];
            sensEl.textContent = labels[parseInt(sens.value) - 1] || 'Medium';
        }
    }

    function flashSavedIndicator() {
        const ind = document.getElementById('stgSavedIndicator');
        if (!ind) return;
        ind.classList.add('visible');
        setTimeout(() => ind.classList.remove('visible'), 2500);
    }

    /* ── Tab Navigation ── */
    function setupTabs() {
        document.querySelectorAll('.stg-tab').forEach(tab => {
            tab.addEventListener('click', () => {
                document.querySelectorAll('.stg-tab').forEach(t => t.classList.remove('active'));
                document.querySelectorAll('.stg-panel').forEach(p => p.classList.remove('active'));
                tab.classList.add('active');
                const panel = document.getElementById('stgPanel-' + tab.dataset.stgTab);
                if (panel) panel.classList.add('active');
            });
        });
    }

    /* ── Difficulty Buttons ── */
    function setupDifficulty() {
        document.querySelectorAll('.stg-diff-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                document.querySelectorAll('.stg-diff-btn').forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
                stgCurrent.difficulty = btn.dataset.diff;
                checkDirty();
            });
        });
    }

    /* ── Font Size Buttons ── */
    function setupFontSize() {
        document.querySelectorAll('.stg-font-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                document.querySelectorAll('.stg-font-btn').forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
                stgCurrent.fontSize = btn.dataset.size;
                applyLiveSettings(stgCurrent);
                checkDirty();
            });
        });
    }

    /* ── Listen to all inputs ── */
    function setupChangeListeners() {
        const ids = [
            'settingsName','settingsEmail','settingsInjury','settingsGoal',
            'stgAge','stgHeight','stgWeight','stgDominantSide',
            'stgAiCoaching','stgAdaptiveRehab',
            'voiceEnabled','voiceSpeed','voiceVolume',
            'stgCamera','stgSkeletonOverlay','stgSensitivity',
            'stgExerciseReminders','stgRehabAlerts','stgEmailNotifs',
            'darkMode','compactSidebar'
        ];
        ids.forEach(id => {
            const el = document.getElementById(id);
            if (!el) return;
            const ev = (el.type === 'checkbox' || el.type === 'range') ? 'input' : 'change';
            el.addEventListener(ev, () => {
                // Live-apply theme toggles immediately
                if (id === 'darkMode' || id === 'compactSidebar') {
                    readFromDOM();
                    applyLiveSettings(stgCurrent);
                }
                updateSliderDisplays();
                checkDirty();
            });
            // also listen to 'input' for text fields for real-time dirty detection
            if (el.tagName === 'INPUT' && el.type !== 'checkbox' && el.type !== 'range') {
                el.addEventListener('input', checkDirty);
            }
        });
    }

    /* ── Public: Save ── */
    window.saveAllSettings = function () {
        readFromDOM();
        persistSettings();
        applyLiveSettings(stgCurrent);
        if (typeof showToast === 'function') showToast('Settings saved successfully!', 'success');
    };

    /* ── Public: Discard ── */
    window.discardSettingsChanges = function () {
        stgCurrent = { ...stgSaved };
        applyToDOM(stgCurrent);
        applyLiveSettings(stgCurrent);
        setDirty(false);
    };

    /* ── Public: Avatar ── */
    window.handleAvatarUpload = function (event) {
        const file = event.target.files[0];
        if (!file) return;
        if (file.size > 2 * 1024 * 1024) {
            if (typeof showToast === 'function') showToast('Image must be under 2MB', 'error');
            return;
        }
        const reader = new FileReader();
        reader.onload = function (e) {
            stgCurrent.avatarData = e.target.result;
            const img = document.getElementById('stgAvatarImg');
            if (img) { img.src = e.target.result; img.style.display = 'block'; }
            const icon = document.querySelector('#stgAvatar > i');
            if (icon) icon.style.display = 'none';
            checkDirty();
        };
        reader.readAsDataURL(file);
    };
    window.removeAvatar = function () {
        stgCurrent.avatarData = '';
        const img = document.getElementById('stgAvatarImg');
        if (img) { img.src = ''; img.style.display = 'none'; }
        const icon = document.querySelector('#stgAvatar > i');
        if (icon) icon.style.display = '';
        checkDirty();
    };

    /* ── Public: Change Password ── */
    window.changeSettingsPassword = async function () {
        const curr = document.getElementById('stgCurrentPwd')?.value;
        const newP = document.getElementById('stgNewPwd')?.value;
        const conf = document.getElementById('stgConfirmPwd')?.value;
        if (!curr || !newP) { if (typeof showToast === 'function') showToast('Please fill in all password fields', 'error'); return; }
        if (newP.length < 6) { if (typeof showToast === 'function') showToast('Password must be at least 6 characters', 'error'); return; }
        if (newP !== conf) { if (typeof showToast === 'function') showToast('Passwords do not match', 'error'); return; }
        try {
            const token = localStorage.getItem('authToken');
            if (!token) { if (typeof showToast === 'function') showToast('You must be logged in to change password', 'error'); return; }
            const resp = await fetch(`${window.API_BASE || 'http://localhost:8000'}/change-password`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json', 'Authorization': 'Bearer ' + token },
                body: JSON.stringify({ current_password: curr, new_password: newP })
            });
            if (resp.ok) {
                if (typeof showToast === 'function') showToast('Password changed!', 'success');
                document.getElementById('stgCurrentPwd').value = '';
                document.getElementById('stgNewPwd').value = '';
                document.getElementById('stgConfirmPwd').value = '';
            } else {
                const d = await resp.json().catch(() => ({}));
                if (typeof showToast === 'function') showToast(d.detail || 'Password change failed', 'error');
            }
        } catch (e) {
            if (typeof showToast === 'function') showToast('Network error', 'error');
        }
    };

    /* ── Public: Camera List ── */
    window.refreshCameraList = async function () {
        try {
            const devices = await navigator.mediaDevices.enumerateDevices();
            const cameras = devices.filter(d => d.kind === 'videoinput');
            const sel = document.getElementById('stgCamera');
            if (!sel) return;
            const currentVal = sel.value;
            sel.innerHTML = '<option value="">Default Camera</option>';
            cameras.forEach((cam, idx) => {
                const opt = document.createElement('option');
                opt.value = cam.deviceId;
                opt.textContent = cam.label || `Camera ${idx + 1}`;
                sel.appendChild(opt);
            });
            sel.value = currentVal;
            if (typeof showToast === 'function') showToast(`Found ${cameras.length} camera(s)`, 'info');
        } catch (e) {
            if (typeof showToast === 'function') showToast('Cannot access camera devices', 'error');
        }
    };

    /* ── Public: Export Health Data ── */
    window.exportHealthData = async function () {
        try {
            const token = localStorage.getItem('authToken');
            let exportData = { settings: stgCurrent, exportDate: new Date().toISOString(), sessions: [] };
            if (token) {
                try {
                    const resp = await fetch(`${window.API_BASE || 'http://localhost:8000'}/sessions`, {
                        headers: { 'Authorization': 'Bearer ' + token }
                    });
                    if (resp.ok) { exportData.sessions = await resp.json(); }
                } catch {}
            }
            const blob = new Blob([JSON.stringify(exportData, null, 2)], { type: 'application/json' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url; a.download = `physio-health-data-${new Date().toISOString().slice(0,10)}.json`;
            document.body.appendChild(a); a.click(); document.body.removeChild(a);
            URL.revokeObjectURL(url);
            if (typeof showToast === 'function') showToast('Health data exported!', 'success');
        } catch (e) {
            if (typeof showToast === 'function') showToast('Export failed', 'error');
        }
    };

    /* ── Public: Delete Account ── */
    window.confirmDeleteAccount = function () {
        const ok = confirm('⚠️ Are you sure you want to delete your account?\n\nThis will permanently remove all your data, exercise sessions, and progress. This action CANNOT be undone.');
        if (!ok) return;
        const doubleOk = confirm('This is your last chance. Type OK in the next prompt or press OK to confirm permanent deletion.');
        if (!doubleOk) return;
        // attempt backend call
        const token = localStorage.getItem('authToken');
        if (token) {
            fetch(`${window.API_BASE || 'http://localhost:8000'}/delete-account`, {
                method: 'DELETE',
                headers: { 'Authorization': 'Bearer ' + token }
            }).catch(() => {});
        }
        localStorage.clear();
        if (typeof showToast === 'function') showToast('Account deleted', 'info');
        setTimeout(() => location.reload(), 1500);
    };

    /* ── Init on DOM ready ── */
    function init() {
        setupTabs();
        setupDifficulty();
        setupFontSize();
        loadSettings();
        setupChangeListeners();
        // Auto-populate camera list
        if (navigator.mediaDevices) {
            navigator.mediaDevices.enumerateDevices().then(devices => {
                const cameras = devices.filter(d => d.kind === 'videoinput');
                const sel = document.getElementById('stgCamera');
                if (!sel || cameras.length === 0) return;
                cameras.forEach((cam, idx) => {
                    const opt = document.createElement('option');
                    opt.value = cam.deviceId;
                    opt.textContent = cam.label || `Camera ${idx + 1}`;
                    sel.appendChild(opt);
                });
                if (stgCurrent.cameraId) sel.value = stgCurrent.cameraId;
            }).catch(() => {});
        }
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

    /* Also load settings when navigating to settings page so values are fresh */
    const origShowPage = window.showPage;
    if (typeof origShowPage === 'function') {
        window.showPage = function(pageName) {
            origShowPage(pageName);
            if (pageName === 'settings') loadSettings();
        };
    }
})();
