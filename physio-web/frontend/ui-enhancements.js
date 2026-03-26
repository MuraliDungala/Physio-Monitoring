/* ================================================================
   PhysioMonitor - UI Enhancements
   Sidebar, search, notifications, voice, floating chat, charts, auth UX
   ================================================================ */

document.addEventListener('DOMContentLoaded', () => {
    initSidebar();
    initCharts();
    initFloatingChat();
    initUserDropdown();
    initGlobalSearch();
    initNotifications();
    initVoiceToggle();
    initAuthEnhancements();
    syncAuthUI();
});

/* ── Sidebar ── */
function initSidebar() {
    const sidebar = document.getElementById('sidebar');
    const toggleBtn = document.getElementById('sidebarToggleBtn');
    const closeBtn = document.getElementById('sidebarCloseBtn');

    if (toggleBtn) {
        toggleBtn.addEventListener('click', () => {
            sidebar.classList.toggle('open');
        });
    }
    if (closeBtn) {
        closeBtn.addEventListener('click', () => {
            sidebar.classList.remove('open');
        });
    }

    // Sidebar nav items
    document.querySelectorAll('.sidebar-nav .nav-item').forEach(item => {
        item.addEventListener('click', function (e) {
            e.preventDefault();
            const page = this.dataset.page;
            if (page && typeof showPage === 'function') {
                showPage(page);
            }
            document.querySelectorAll('.sidebar-nav .nav-item').forEach(n => n.classList.remove('active'));
            this.classList.add('active');
            if (window.innerWidth <= 1024) {
                sidebar.classList.remove('open');
            }
        });
    });

    // Close sidebar when clicking outside on mobile
    document.addEventListener('click', (e) => {
        if (window.innerWidth <= 1024 && sidebar.classList.contains('open')) {
            if (!sidebar.contains(e.target) && e.target !== toggleBtn && !toggleBtn.contains(e.target)) {
                sidebar.classList.remove('open');
            }
        }
    });

    // Show hamburger only on mobile
    function checkMobile() {
        if (toggleBtn) {
            toggleBtn.style.display = window.innerWidth <= 1024 ? 'flex' : 'none';
        }
    }
    checkMobile();
    window.addEventListener('resize', checkMobile);
}

/* ── Register nav button ── */
(function wireRegisterNav() {
    const registerNavBtn = document.getElementById('registerNavBtn');
    if (registerNavBtn) {
        registerNavBtn.addEventListener('click', (e) => {
            e.preventDefault();
            if (typeof showRegisterModal === 'function') showRegisterModal();
        });
    }
})();

/* ── Charts ── */
function initCharts() {
    // Wait for Chart.js to be available
    if (typeof Chart === 'undefined') {
        setTimeout(initCharts, 500);
        return;
    }

    const chartColors = {
        primary: '#1E88E5',
        primaryLight: 'rgba(30, 136, 229, 0.15)',
        teal: '#00897B',
        tealLight: 'rgba(0, 137, 123, 0.15)',
        purple: '#7C4DFF',
        purpleLight: 'rgba(124, 77, 255, 0.15)',
        green: '#43A047',
        orange: '#FB8C00',
        red: '#E53935',
        grid: 'rgba(0, 0, 0, 0.05)',
        text: '#64748B',
    };
    // Store chart colors globally for reuse
    window._chartColors = chartColors;

    const commonOptions = {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: { display: false },
            tooltip: {
                backgroundColor: 'rgba(26, 32, 44, 0.9)',
                titleFont: { family: 'Inter', size: 13, weight: '600' },
                bodyFont: { family: 'Inter', size: 12 },
                padding: 10,
                cornerRadius: 8,
                displayColors: false,
            }
        },
        scales: {
            x: {
                grid: { display: false },
                ticks: { font: { family: 'Inter', size: 11 }, color: chartColors.text }
            },
            y: {
                grid: { color: chartColors.grid },
                ticks: { font: { family: 'Inter', size: 11 }, color: chartColors.text }
            }
        }
    };

    // Weekly Activity Chart (dashboard) — start empty (all zeros)
    const wCtx = document.getElementById('weeklyActivityChart');
    if (wCtx) {
        window._weeklyChart = new Chart(wCtx.getContext('2d'), {
            type: 'bar',
            data: {
                labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
                datasets: [{
                    label: 'Sessions',
                    data: [0, 0, 0, 0, 0, 0, 0],
                    backgroundColor: chartColors.primaryLight,
                    borderColor: chartColors.primary,
                    borderWidth: 2,
                    borderRadius: 6,
                    barPercentage: 0.6,
                }]
            },
            options: { ...commonOptions, plugins: { ...commonOptions.plugins, legend: { display: false } } }
        });
    }

    // Quality Trend Chart (dashboard) — start empty (no data)
    const qCtx = document.getElementById('qualityTrendChart');
    if (qCtx) {
        window._qualityChart = new Chart(qCtx.getContext('2d'), {
            type: 'line',
            data: {
                labels: [],
                datasets: [{
                    label: 'Quality %',
                    data: [],
                    borderColor: chartColors.teal,
                    backgroundColor: chartColors.tealLight,
                    fill: true,
                    tension: 0.4,
                    pointBackgroundColor: '#fff',
                    pointBorderColor: chartColors.teal,
                    pointBorderWidth: 2,
                    pointRadius: 4,
                    pointHoverRadius: 6,
                }]
            },
            options: commonOptions
        });
    }

    // Recovery Progress Chart & Exercise Distribution Chart
    // Now initialized dynamically by loadReportsData() in script.js
}

/* ══════════════════════════════════════════════════════════════
   FLOATING AI CHATBOT WIDGET (Enhanced)
   ══════════════════════════════════════════════════════════════ */
function initFloatingChat() {
    // Already wired via onclick in HTML
    // Set up periodic context updates
    setInterval(updateFloatingChatContext, 3000);
}

function toggleFloatingChat() {
    const win = document.getElementById('floatingChatWindow');
    if (win) {
        const isOpen = win.style.display !== 'none';
        win.style.display = isOpen ? 'none' : 'flex';
        // Remove badge when opening
        const badge = document.getElementById('fcBadge');
        if (badge && !isOpen) badge.style.display = 'none';
        // Update context bar
        if (!isOpen) updateFloatingChatContext();
        // Focus input
        if (!isOpen) {
            setTimeout(() => {
                const input = document.getElementById('floatingChatInput');
                if (input) input.focus();
            }, 300);
        }
    }
}

/**
 * Update the floating chat context chips showing active session data.
 */
function updateFloatingChatContext() {
    const bar = document.getElementById('fcContext');
    if (!bar) return;
    const ctx = (typeof getChatContext === 'function') ? getChatContext() : {};
    const chips = [];
    if (ctx.exercise) chips.push(`<span class="fc-ctx-chip"><i class="fas fa-dumbbell"></i> ${ctx.exercise}</span>`);
    if (ctx.rep_count) chips.push(`<span class="fc-ctx-chip"><i class="fas fa-redo-alt"></i> ${ctx.rep_count} reps</span>`);
    if (ctx.quality_score) chips.push(`<span class="fc-ctx-chip"><i class="fas fa-star"></i> ${ctx.quality_score}%</span>`);
    if (chips.length > 0) {
        bar.innerHTML = chips.join('');
        bar.style.display = 'flex';
    } else {
        bar.style.display = 'none';
    }
}

/**
 * Send a message from the floating chat widget.
 */
async function sendFloatingChat() {
    const input = document.getElementById('floatingChatInput');
    if (!input || !input.value.trim()) return;

    const msg = input.value.trim();
    const container = document.getElementById('floatingChatMessages');

    // Add user message
    const userDiv = document.createElement('div');
    userDiv.className = 'message user-message';
    userDiv.innerHTML = `<div class="msg-avatar"><i class="fas fa-user"></i></div><div class="message-content"><p>${escapeHTML(msg)}</p></div>`;
    container.appendChild(userDiv);
    input.value = '';
    container.scrollTop = container.scrollHeight;

    // Show typing indicator
    if (typeof showTypingIndicator === 'function') {
        showTypingIndicator('floatingChatMessages');
    }

    // Call the AI /chat endpoint
    try {
        const API_BASE = `http://${window.location.hostname}:8001`;
        const ctx = (typeof getChatContext === 'function') ? getChatContext() : {};

        const resp = await fetch(`${API_BASE}/chat`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                user_message: msg,
                exercise: ctx.exercise || null,
                rep_count: ctx.rep_count || '',
                quality_score: ctx.quality_score || '',
                joint_angle: ctx.joint_angle || '',
                posture_feedback: ctx.posture_feedback || '',
            })
        });

        if (typeof removeTypingIndicator === 'function') {
            removeTypingIndicator('floatingChatMessages');
        }

        let reply = "I'm having trouble responding. Try the full AI Assistant page for more help.";
        if (resp.ok) {
            const data = await resp.json();
            reply = data.response || reply;
        }

        // Format and display bot reply
        const formatted = (typeof formatChatMarkdown === 'function') ? formatChatMarkdown(reply) : reply;
        const botDiv = document.createElement('div');
        botDiv.className = 'message bot-message';
        botDiv.innerHTML = `<div class="msg-avatar"><i class="fas fa-robot"></i></div><div class="message-content">${formatted}</div>`;
        container.appendChild(botDiv);
        container.scrollTop = container.scrollHeight;

        // Optional speech
        if (typeof speakChatResponse === 'function') {
            speakChatResponse(reply);
        }
    } catch (e) {
        if (typeof removeTypingIndicator === 'function') {
            removeTypingIndicator('floatingChatMessages');
        }
        console.log('Floating chat error:', e.message);
        const errorDiv = document.createElement('div');
        errorDiv.className = 'message bot-message';
        errorDiv.innerHTML = `<div class="msg-avatar"><i class="fas fa-robot"></i></div><div class="message-content"><p>Sorry, I couldn't connect to the server. Please check your connection.</p></div>`;
        container.appendChild(errorDiv);
        container.scrollTop = container.scrollHeight;
    }

    // Update suggestions after first message
    updateFCSuggestions(msg);
}

/**
 * Send a quick preset message from floating chat suggestion chips.
 */
function fcQuickMessage(msg) {
    const input = document.getElementById('floatingChatInput');
    if (input) input.value = msg;
    sendFloatingChat();
}

/**
 * Clear the floating chat message history.
 */
function clearFloatingChat() {
    const container = document.getElementById('floatingChatMessages');
    if (container) {
        container.innerHTML = `
            <div class="message bot-message">
                <div class="msg-avatar"><i class="fas fa-robot"></i></div>
                <div class="message-content"><p>Chat cleared. How can I help you?</p></div>
            </div>
        `;
    }
}

/**
 * Update suggestion chips based on conversation context.
 */
function updateFCSuggestions(lastMsg) {
    const sugContainer = document.getElementById('fcSuggestions');
    if (!sugContainer) return;

    const ctx = (typeof getChatContext === 'function') ? getChatContext() : {};
    const suggestions = [];

    if (ctx.exercise) {
        suggestions.push({ label: `How to do ${ctx.exercise}?`, msg: `How do I perform ${ctx.exercise}?` });
        suggestions.push({ label: 'Common mistakes', msg: `What are common mistakes in ${ctx.exercise}?` });
    }
    if (ctx.quality_score && parseFloat(ctx.quality_score) < 70) {
        suggestions.push({ label: 'Improve my score', msg: 'How can I improve my quality score?' });
    }
    // Always include some general options
    suggestions.push({ label: 'Safety Tips', msg: 'Give me a safety tip' });
    suggestions.push({ label: 'Motivate me', msg: 'I need some motivation' });

    // Limit to 4
    const limited = suggestions.slice(0, 4);
    sugContainer.innerHTML = limited.map(s =>
        `<button class="fc-sug-chip" onclick="fcQuickMessage('${s.msg.replace(/'/g, "\\'")}')">${s.label}</button>`
    ).join('');
}

/**
 * Voice input for the floating chat widget.
 */
let fcVoiceRecognition = null;

function toggleFCVoiceInput() {
    const btn = document.getElementById('fcVoiceBtn');
    if (!('webkitSpeechRecognition' in window || 'SpeechRecognition' in window)) {
        fcQuickMessage('Voice input is not supported in this browser');
        return;
    }
    if (fcVoiceRecognition) {
        fcVoiceRecognition.stop();
        fcVoiceRecognition = null;
        if (btn) btn.classList.remove('listening');
        return;
    }
    const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
    fcVoiceRecognition = new SR();
    fcVoiceRecognition.lang = 'en-US';
    fcVoiceRecognition.continuous = false;
    fcVoiceRecognition.interimResults = false;
    if (btn) btn.classList.add('listening');

    fcVoiceRecognition.onresult = (event) => {
        const transcript = event.results[0][0].transcript;
        const input = document.getElementById('floatingChatInput');
        if (input) input.value = transcript;
        sendFloatingChat();
    };
    fcVoiceRecognition.onend = () => {
        fcVoiceRecognition = null;
        if (btn) btn.classList.remove('listening');
    };
    fcVoiceRecognition.onerror = () => {
        fcVoiceRecognition = null;
        if (btn) btn.classList.remove('listening');
    };
    fcVoiceRecognition.start();
}

/* ── User Dropdown ── */
function initUserDropdown() {
    const menu = document.getElementById('userMenu');
    const dropdown = document.getElementById('userDropdown');
    if (!menu || !dropdown) return;

    // Toggle on click instead of pure hover (better for accessibility)
    menu.addEventListener('click', (e) => {
        e.stopPropagation();
        const isOpen = dropdown.style.display === 'block';
        dropdown.style.display = isOpen ? 'none' : 'block';
    });

    document.addEventListener('click', () => {
        if (dropdown) dropdown.style.display = 'none';
    });
}

/* ── Global Search ── */
function initGlobalSearch() {
    const search = document.getElementById('globalSearch');
    if (!search) return;

    // Create search results dropdown
    const resultsDiv = document.createElement('div');
    resultsDiv.className = 'search-results';
    resultsDiv.id = 'searchResults';
    search.parentElement.appendChild(resultsDiv);

    // All searchable items
    const searchIndex = [
        // Pages
        { label: 'Home', icon: 'fa-home', action: () => showPage('home'), category: 'Pages' },
        { label: 'Dashboard', icon: 'fa-th-large', action: () => showPage('dashboard'), category: 'Pages' },
        { label: 'Exercises', icon: 'fa-dumbbell', action: () => showPage('exercises'), category: 'Pages' },
        { label: 'Reports & Analytics', icon: 'fa-chart-line', action: () => showPage('reports'), category: 'Pages' },
        { label: 'Rehab Plan', icon: 'fa-clipboard-list', action: () => showPage('rehabPlan'), category: 'Pages' },
        { label: 'AI Assistant / Chatbot', icon: 'fa-robot', action: () => showPage('chatbot'), category: 'Pages' },
        { label: 'Settings', icon: 'fa-cog', action: () => showPage('settings'), category: 'Pages' },
        // Exercise Categories
        { label: 'Neck Exercises', icon: 'fa-head-side-mask', action: () => { if(typeof loadCategoryExercises==='function') loadCategoryExercises('Neck'); }, category: 'Categories' },
        { label: 'Shoulder Exercises', icon: 'fa-hand-rock', action: () => { if(typeof loadCategoryExercises==='function') loadCategoryExercises('Shoulder'); }, category: 'Categories' },
        { label: 'Elbow Exercises', icon: 'fa-hand-fist', action: () => { if(typeof loadCategoryExercises==='function') loadCategoryExercises('Elbow'); }, category: 'Categories' },
        { label: 'Wrist Exercises', icon: 'fa-hand', action: () => { if(typeof loadCategoryExercises==='function') loadCategoryExercises('Wrist'); }, category: 'Categories' },
        { label: 'Hip Exercises', icon: 'fa-person-walking', action: () => { if(typeof loadCategoryExercises==='function') loadCategoryExercises('Hip'); }, category: 'Categories' },
        { label: 'Knee Exercises', icon: 'fa-bone', action: () => { if(typeof loadCategoryExercises==='function') loadCategoryExercises('Knee'); }, category: 'Categories' },
        { label: 'Ankle Exercises', icon: 'fa-shoe-prints', action: () => { if(typeof loadCategoryExercises==='function') loadCategoryExercises('Ankle'); }, category: 'Categories' },
        { label: 'Squat Exercises', icon: 'fa-person-arrow-down-to-line', action: () => { if(typeof loadCategoryExercises==='function') loadCategoryExercises('Squat'); }, category: 'Categories' },
        // Features
        { label: 'Voice Assistant', icon: 'fa-microphone', action: () => { toggleVoiceHelper(); }, category: 'Features' },
        { label: 'Login', icon: 'fa-sign-in-alt', action: () => { if(typeof showLoginModal==='function') showLoginModal(); }, category: 'Account' },
        { label: 'Register / Sign Up', icon: 'fa-user-plus', action: () => { if(typeof showRegisterModal==='function') showRegisterModal(); }, category: 'Account' },
        { label: 'All Exercises List', icon: 'fa-list', action: () => { if(typeof loadAllExercises==='function') loadAllExercises(); showPage('allExercises'); }, category: 'Pages' },
        { label: 'Progress Tracking', icon: 'fa-chart-bar', action: () => showPage('reports'), category: 'Features' },
        { label: 'Recovery Report', icon: 'fa-file-medical-alt', action: () => showPage('reports'), category: 'Features' },
        { label: 'Range of Motion', icon: 'fa-ruler-combined', action: () => showPage('dashboard'), category: 'Features' },
        { label: 'Session History', icon: 'fa-history', action: () => showPage('dashboard'), category: 'Features' },
    ];

    let selectedIdx = -1;

    search.addEventListener('input', () => {
        const q = search.value.trim().toLowerCase();
        if (!q) { resultsDiv.classList.remove('open'); return; }

        const matches = searchIndex.filter(item =>
            item.label.toLowerCase().includes(q) || item.category.toLowerCase().includes(q)
        );

        if (matches.length === 0) {
            resultsDiv.innerHTML = '<div class="sr-empty">No results found</div>';
        } else {
            let html = '';
            let lastCat = '';
            matches.forEach((m, i) => {
                if (m.category !== lastCat) {
                    lastCat = m.category;
                    html += `<div class="sr-section">${m.category}</div>`;
                }
                html += `<div class="sr-item" data-idx="${i}"><i class="fas ${m.icon}"></i><span>${highlightMatch(m.label, q)}</span></div>`;
            });
            resultsDiv.innerHTML = html;

            // Add click handlers
            resultsDiv.querySelectorAll('.sr-item').forEach((el, i) => {
                el.addEventListener('click', () => {
                    matches[i].action();
                    search.value = '';
                    resultsDiv.classList.remove('open');
                });
            });
        }
        resultsDiv.classList.add('open');
        selectedIdx = -1;
    });

    // Keyboard navigation
    search.addEventListener('keydown', (e) => {
        const items = resultsDiv.querySelectorAll('.sr-item');
        if (!items.length) return;

        if (e.key === 'ArrowDown') {
            e.preventDefault();
            selectedIdx = Math.min(selectedIdx + 1, items.length - 1);
            items.forEach((el, i) => el.style.background = i === selectedIdx ? 'var(--primary-bg)' : '');
        } else if (e.key === 'ArrowUp') {
            e.preventDefault();
            selectedIdx = Math.max(selectedIdx - 1, 0);
            items.forEach((el, i) => el.style.background = i === selectedIdx ? 'var(--primary-bg)' : '');
        } else if (e.key === 'Enter') {
            e.preventDefault();
            if (selectedIdx >= 0 && items[selectedIdx]) {
                items[selectedIdx].click();
            }
        } else if (e.key === 'Escape') {
            resultsDiv.classList.remove('open');
            search.blur();
        }
    });

    // Close on click outside
    document.addEventListener('click', (e) => {
        if (!search.parentElement.contains(e.target)) {
            resultsDiv.classList.remove('open');
        }
    });

    search.addEventListener('focus', () => {
        if (search.value.trim()) search.dispatchEvent(new Event('input'));
    });
}

function highlightMatch(text, query) {
    const idx = text.toLowerCase().indexOf(query);
    if (idx === -1) return text;
    return text.slice(0, idx) + '<strong>' + text.slice(idx, idx + query.length) + '</strong>' + text.slice(idx + query.length);
}

/* ── Quick Message Helper ── */
function sendQuickMessage(msg) {
    const input = document.getElementById('chatInput');
    if (input) {
        input.value = msg;
        if (typeof sendChatMessage === 'function') {
            sendChatMessage();
        }
    }
}

/* ── Generate PDF Report ── */
function generatePDFReport() {
    // currentUser & authToken are declared with 'let' in script.js so
    // check via typeof to avoid ReferenceError, fall back to localStorage
    const user  = (typeof currentUser  !== 'undefined' && currentUser)  || JSON.parse(localStorage.getItem('currentUser') || 'null');
    const token = (typeof authToken    !== 'undefined' && authToken)    || localStorage.getItem('authToken');
    if (!user || !token) {
        showToast('Please log in to download your report.', 'warning');
        return;
    }

    showToast('Generating PDF report…', 'info');

    // Gather data from the Reports page DOM
    const totalSessions = document.getElementById('rptTotalSessions')?.textContent || '--';
    const daysActive    = document.getElementById('rptDaysActive')?.textContent || '--';
    const qualityAvg    = document.getElementById('rptQualityAvg')?.textContent || '--';

    // Grab AI report sections
    const reportBody = document.getElementById('aiReportBody');
    const sections = reportBody ? reportBody.querySelectorAll('.air-section') : [];

    try {
        const { jsPDF } = window.jspdf;
        const doc = new jsPDF({ orientation: 'portrait', unit: 'mm', format: 'a4' });

        const pageW = doc.internal.pageSize.getWidth();
        const margin = 15;
        let y = 20;

        // Helper: add text with auto page-break
        const addLine = (text, fontSize, isBold, color) => {
            if (y > 275) { doc.addPage(); y = 20; }
            doc.setFontSize(fontSize || 12);
            doc.setFont('helvetica', isBold ? 'bold' : 'normal');
            if (color) doc.setTextColor(...color); else doc.setTextColor(30, 30, 30);
            doc.text(text, margin, y);
            y += fontSize ? fontSize * 0.5 + 2 : 8;
        };

        const addWrapped = (text, fontSize) => {
            doc.setFontSize(fontSize || 11);
            doc.setFont('helvetica', 'normal');
            doc.setTextColor(50, 50, 50);
            const lines = doc.splitTextToSize(text, pageW - margin * 2);
            lines.forEach(line => {
                if (y > 275) { doc.addPage(); y = 20; }
                doc.text(line, margin, y);
                y += 5.5;
            });
            y += 2;
        };

        // Header
        doc.setFillColor(102, 126, 234);
        doc.rect(0, 0, pageW, 35, 'F');
        doc.setTextColor(255, 255, 255);
        doc.setFontSize(20);
        doc.setFont('helvetica', 'bold');
        doc.text('Physiotherapy Recovery Report', margin, 18);
        doc.setFontSize(10);
        doc.setFont('helvetica', 'normal');
        const userName = user?.username || user?.email || 'User';
        doc.text(`Patient: ${userName}  |  Generated: ${new Date().toLocaleDateString('en-IN', { day:'2-digit', month:'short', year:'numeric' })}`, margin, 28);
        y = 45;

        // Summary cards
        addLine('Summary', 14, true, [102, 126, 234]);
        y += 2;
        doc.setDrawColor(220, 220, 220);
        doc.line(margin, y, pageW - margin, y);
        y += 6;
        addLine(`Total Sessions:    ${totalSessions}`, 12, false);
        addLine(`Days Active:       ${daysActive}`, 12, false);
        addLine(`Quality Average:   ${qualityAvg}`, 12, false);
        y += 6;

        // AI Report sections
        sections.forEach(section => {
            const heading = section.querySelector('h4')?.textContent || '';
            addLine(heading, 13, true, [102, 126, 234]);
            y += 1;

            // Paragraphs
            section.querySelectorAll('p').forEach(p => {
                addWrapped(p.textContent.trim(), 11);
            });

            // List items
            const listItems = section.querySelectorAll('li');
            listItems.forEach(li => {
                const txt = li.textContent.trim();
                if (y > 275) { doc.addPage(); y = 20; }
                doc.setFontSize(11);
                doc.setFont('helvetica', 'normal');
                doc.setTextColor(50, 50, 50);
                const lines = doc.splitTextToSize('• ' + txt, pageW - margin * 2 - 5);
                lines.forEach(line => {
                    if (y > 275) { doc.addPage(); y = 20; }
                    doc.text(line, margin + 3, y);
                    y += 5.5;
                });
            });
            y += 4;
        });

        // Charts — embed as images if available
        const chartIds = ['recoveryProgressChart', 'exerciseDistributionChart'];
        chartIds.forEach(id => {
            const canvas = document.getElementById(id);
            if (canvas && canvas.toDataURL) {
                try {
                    if (y > 180) { doc.addPage(); y = 20; }
                    const imgData = canvas.toDataURL('image/png', 1.0);
                    const chartW = pageW - margin * 2;
                    const chartH = 70;
                    doc.addImage(imgData, 'PNG', margin, y, chartW, chartH);
                    y += chartH + 8;
                } catch (e) {
                    console.warn('Could not embed chart', id, e);
                }
            }
        });

        // Footer
        const pageCount = doc.internal.getNumberOfPages();
        for (let i = 1; i <= pageCount; i++) {
            doc.setPage(i);
            doc.setFontSize(8);
            doc.setTextColor(150, 150, 150);
            doc.text(`PhysioTrack Pro — Page ${i} of ${pageCount}`, margin, 290);
        }

        doc.save(`PhysioTrack_Report_${new Date().toISOString().slice(0,10)}.pdf`);
        showToast('PDF report downloaded successfully!', 'success');
    } catch (err) {
        console.error('PDF generation error:', err);
        showToast('Failed to generate PDF. Please try again.', 'error');
    }
}

/* ── Toast System ── */
function showToast(message, type = 'info') {
    const container = document.getElementById('toastContainer');
    if (!container) return;

    const icons = {
        success: 'fa-check-circle',
        error: 'fa-times-circle',
        info: 'fa-info-circle',
        warning: 'fa-exclamation-triangle'
    };

    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.innerHTML = `<i class="fas ${icons[type] || icons.info}"></i><span>${message}</span>`;
    container.appendChild(toast);

    setTimeout(() => {
        toast.style.animation = 'toastOut 0.3s ease forwards';
        setTimeout(() => toast.remove(), 300);
    }, 4000);
}

/* ── Notifications System ── */
function initNotifications() {
    const btn = document.getElementById('notificationBtn');
    const dropdown = document.getElementById('notifDropdown');
    const badge = document.getElementById('notifBadge');
    const clearBtn = document.getElementById('clearAllNotifs');

    if (!btn || !dropdown) return;

    // Toggle dropdown - only when clicking bell icon or badge, not dropdown contents
    btn.addEventListener('click', (e) => {
        // Don't toggle when clicking inside the dropdown itself
        if (dropdown.contains(e.target)) return;
        e.stopPropagation();
        dropdown.classList.toggle('open');
        // Close user dropdown if open
        const userDD = document.getElementById('userDropdown');
        if (userDD) userDD.style.display = 'none';
    });

    // Notification item clicks
    dropdown.querySelectorAll('.notif-item').forEach(item => {
        item.addEventListener('click', () => {
            const action = item.dataset.action;
            if (action && typeof showPage === 'function') {
                showPage(action);
            }
            item.classList.remove('unread');
            updateNotifBadge();
            dropdown.classList.remove('open');
        });
    });

    // Clear all
    if (clearBtn) {
        clearBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            const list = document.getElementById('notifList');
            if (list) list.innerHTML = '<div class="notif-empty"><i class="fas fa-bell-slash"></i><p>No new notifications</p></div>';
            if (badge) badge.style.display = 'none';
        });
    }

    // Close on click outside
    document.addEventListener('click', (e) => {
        if (!btn.contains(e.target)) {
            dropdown.classList.remove('open');
        }
    });

    function updateNotifBadge() {
        const unread = dropdown.querySelectorAll('.notif-item.unread').length;
        if (badge) {
            badge.textContent = unread;
            badge.style.display = unread > 0 ? 'flex' : 'none';
        }
    }
}

/* ── Voice Assistant Toggle ── */
function initVoiceToggle() {
    const btn = document.getElementById('voiceToggleBtn');
    if (!btn) return;

    btn.addEventListener('click', () => {
        toggleVoiceHelper();
    });
}

function toggleVoiceHelper() {
    const btn = document.getElementById('voiceToggleBtn');
    if (typeof toggleVoiceAssistant === 'function') {
        toggleVoiceAssistant();
    } else if (typeof voiceAssistant !== 'undefined') {
        voiceAssistant.enabled = !voiceAssistant.enabled;
    }

    // Update visual state
    const isEnabled = (typeof voiceAssistant !== 'undefined') ? voiceAssistant.enabled : false;
    if (btn) {
        btn.classList.toggle('voice-active', isEnabled);
        btn.title = isEnabled ? 'Voice Assistant: ON' : 'Voice Assistant: OFF';
    }
    showToast(isEnabled ? 'Voice Assistant enabled' : 'Voice Assistant disabled', isEnabled ? 'success' : 'info');
}

/* ── Auth Enhancements (interactive login/register) ── */
function initAuthEnhancements() {
    // Password strength meter for registration
    const regPwd = document.getElementById('regPassword');
    const strengthDiv = document.getElementById('passwordStrength');
    if (regPwd && strengthDiv) {
        regPwd.addEventListener('input', () => {
            const val = regPwd.value;
            const strength = getPasswordStrength(val);
            strengthDiv.className = 'password-strength ' + strength.cls;
            const psText = document.getElementById('psText');
            if (psText) psText.textContent = val.length > 0 ? strength.text : '';
        });
    }

    // Live inline validation
    setupFieldValidation('username', (v) => v.length >= 3 ? '' : 'Username must be at least 3 characters', 'loginUsernameError');
    setupFieldValidation('password', (v) => v.length >= 6 ? '' : 'Password must be at least 6 characters', 'loginPasswordError');
    setupFieldValidation('regUsername', (v) => v.length >= 3 ? '' : 'Username must be at least 3 characters', 'regUsernameError');
    setupFieldValidation('regEmail', (v) => /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(v) ? '' : 'Please enter a valid email', 'regEmailError');
    setupFieldValidation('regPassword', (v) => v.length >= 6 ? '' : 'Password must be at least 6 characters', 'regPasswordError');
}

function setupFieldValidation(inputId, validator, errorId) {
    const input = document.getElementById(inputId);
    const error = document.getElementById(errorId);
    if (!input || !error) return;

    input.addEventListener('blur', () => {
        if (input.value.trim().length === 0) {
            input.classList.remove('input-valid', 'input-invalid');
            error.textContent = '';
            return;
        }
        const msg = validator(input.value.trim());
        if (msg) {
            input.classList.remove('input-valid');
            input.classList.add('input-invalid');
            error.textContent = msg;
        } else {
            input.classList.remove('input-invalid');
            input.classList.add('input-valid');
            error.textContent = '';
        }
    });

    input.addEventListener('input', () => {
        if (input.classList.contains('input-invalid')) {
            const msg = validator(input.value.trim());
            if (!msg) {
                input.classList.remove('input-invalid');
                input.classList.add('input-valid');
                error.textContent = '';
            }
        }
    });
}

function getPasswordStrength(pwd) {
    if (!pwd) return { cls: '', text: '' };
    let score = 0;
    if (pwd.length >= 6) score++;
    if (pwd.length >= 10) score++;
    if (/[A-Z]/.test(pwd)) score++;
    if (/[0-9]/.test(pwd)) score++;
    if (/[^A-Za-z0-9]/.test(pwd)) score++;

    if (score <= 1) return { cls: 'ps-weak', text: 'Weak' };
    if (score === 2) return { cls: 'ps-fair', text: 'Fair' };
    if (score === 3) return { cls: 'ps-good', text: 'Good' };
    return { cls: 'ps-strong', text: 'Strong' };
}

/* ── Password Visibility Toggle ── */
function togglePasswordVisibility(btn) {
    const input = btn.previousElementSibling;
    if (!input) return;
    const isPassword = input.type === 'password';
    input.type = isPassword ? 'text' : 'password';
    btn.innerHTML = isPassword ? '<i class="fas fa-eye-slash"></i>' : '<i class="fas fa-eye"></i>';
}

/* ── Sync auth UI on load ── */
function syncAuthUI() {
    const interval = setInterval(() => {
        const sidebarName = document.querySelector('.sidebar-user-name');
        const topName = document.getElementById('topbarUserName');
        const loginBtn = document.getElementById('loginBtn');
        const registerNavBtn = document.getElementById('registerNavBtn');
        const logoutBtn = document.getElementById('logoutBtn');

        if (typeof currentUser !== 'undefined' && currentUser) {
            const name = currentUser.username || currentUser.full_name || 'User';
            if (sidebarName) sidebarName.textContent = name;
            if (topName) topName.textContent = name;
            if (loginBtn) loginBtn.style.display = 'none';
            if (registerNavBtn) registerNavBtn.style.display = 'none';
            if (logoutBtn) logoutBtn.style.display = 'flex';
            clearInterval(interval);
        } else {
            if (sidebarName) sidebarName.textContent = 'Guest';
            if (topName) topName.textContent = 'Guest';
            if (loginBtn) loginBtn.style.display = 'flex';
            if (registerNavBtn) registerNavBtn.style.display = 'flex';
            if (logoutBtn) logoutBtn.style.display = 'none';
        }
    }, 500);

    // Stop after 10s
    setTimeout(() => clearInterval(interval), 10000);
}

/* ── Escape HTML helper ── */
function escapeHTML(str) {
    const div = document.createElement('div');
    div.textContent = str;
    return div.innerHTML;
}

/* ── Sync sidebar active state with showPage ── */
(function patchShowPage() {
    const orig = window.showPage;
    if (typeof orig !== 'function') {
        // script.js hasn't loaded yet, retry
        setTimeout(patchShowPage, 300);
        return;
    }
    window.showPage = function (pageName) {
        orig(pageName);
        // Update sidebar active
        document.querySelectorAll('.sidebar-nav .nav-item').forEach(item => {
            item.classList.remove('active');
            if (item.dataset.page === pageName) item.classList.add('active');
        });
    };
})();
