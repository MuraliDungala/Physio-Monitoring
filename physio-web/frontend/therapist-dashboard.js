/**
 * PhysioMonitor Therapist Dashboard
 * Features:
 * - Patient list management
 * - Progress monitoring
 * - Exercise assignment
 * - Performance insights
 */

class TherapistDashboard {
    constructor() {
        this.patients = [];
        this.selectedPatient = null;
        this.userRole = this.getUserRole();
        
        this.init();
    }
    
    /**
     * Initialize therapist dashboard
     */
    init() {
        if (this.userRole !== 'therapist') {
            console.log('User is not a therapist');
            return;
        }
        
        this.setupEventListeners();
        this.loadPatients();
    }
    
    /**
     * Get user role from localStorage
     */
    getUserRole() {
        try {
            const userStr = localStorage.getItem('currentUser');
            const user = userStr ? JSON.parse(userStr) : null;
            return user?.role || 'patient';
        } catch (e) {
            return 'patient';
        }
    }
    
    /**
     * Setup event listeners
     */
    setupEventListeners() {
        const assignBtn = document.getElementById('assignExerciseBtn');
        if (assignBtn) {
            assignBtn.addEventListener('click', () => this.showAssignDialog());
        }
        
        const updatePlanBtn = document.getElementById('updatePlanBtn');
        if (updatePlanBtn) {
            updatePlanBtn.addEventListener('click', () => this.showUpdatePlanDialog());
        }
    }
    
    /**
     * Load patients list
     */
    async loadPatients() {
        try {
            loadingManager.startLoading(i18n.t('loading'));
            
            const response = await fetch(API_BASE + '/therapist/patients', {
                method: 'GET',
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('authToken')}`
                }
            });
            
            const data = await response.json();
            this.patients = data.patients || [];
            this.renderPatientList();
            
            loadingManager.stopLoading();
        } catch (error) {
            console.error('Error loading patients:', error);
            loadingManager.stopLoading();
        }
    }
    
    /**
     * Render patient list
     */
    renderPatientList() {
        const patientList = document.getElementById('patientList');
        if (!patientList) return;
        
        patientList.innerHTML = this.patients.map(patient => `
            <div class="patient-card" data-patient-id="${patient.id}">
                <div class="patient-avatar">
                    <i class="fas fa-user"></i>
                </div>
                <div class="patient-info">
                    <h3>${patient.full_name}</h3>
                    <p>${patient.email}</p>
                    <div class="patient-stats">
                        <span><i class="fas fa-dumbbell"></i> ${patient.sessions_count} sessions</span>
                        <span><i class="fas fa-chart-line"></i> ${patient.avg_quality}% quality</span>
                    </div>
                </div>
                <button class="btn btn-sm btn-primary" onclick="therapistDashboard.selectPatient(${patient.id})">
                    View Progress
                </button>
            </div>
        `).join('');
        
        // Add click handlers
        document.querySelectorAll('.patient-card').forEach(card => {
            card.addEventListener('click', (e) => {
                const patientId = card.dataset.patientId;
                this.selectPatient(parseInt(patientId));
            });
        });
    }
    
    /**
     * Select a patient to view details
     */
    async selectPatient(patientId) {
        this.selectedPatient = this.patients.find(p => p.id === patientId);
        
        if (!this.selectedPatient) return;
        
        // Load patient details
        await this.loadPatientDetails(patientId);
        
        // Update UI
        this.renderPatientDetails();
    }
    
    /**
     * Load detailed patient data
     */
    async loadPatientDetails(patientId) {
        try {
            const response = await fetch(
                API_BASE + `/therapist/patients/${patientId}/progress`,
                {
                    headers: {
                        'Authorization': `Bearer ${localStorage.getItem('authToken')}`
                    }
                }
            );
            
            const data = await response.json();
            this.selectedPatient = {
                ...this.selectedPatient,
                ...data
            };
        } catch (error) {
            console.error('Error loading patient details:', error);
        }
    }
    
    /**
     * Render patient details
     */
    renderPatientDetails() {
        if (!this.selectedPatient) return;
        
        const patient = this.selectedPatient;
        const container = document.getElementById('patientDetailsPanel');
        if (!container) return;
        
        container.innerHTML = `
            <div class="patient-header">
                <h2>${patient.full_name}</h2>
                <span class="badge">${patient.age || 'N/A'} years</span>
            </div>
            
            <div class="patient-metrics">
                <div class="metric-card">
                    <h4>Sessions</h4>
                    <p class="metric-value">${patient.sessions_count || 0}</p>
                </div>
                <div class="metric-card">
                    <h4>Total Reps</h4>
                    <p class="metric-value">${patient.total_reps || 0}</p>
                </div>
                <div class="metric-card">
                    <h4>Avg Quality</h4>
                    <p class="metric-value">${(patient.avg_quality || 0).toFixed(1)}%</p>
                </div>
                <div class="metric-card">
                    <h4>Days Active</h4>
                    <p class="metric-value">${patient.days_active || 0}</p>
                </div>
            </div>
            
            <div class="patient-exercises">
                <h3>Exercise History</h3>
                ${this.renderExerciseHistory(patient.exercise_history || [])}
            </div>
            
            <div class="patient-actions">
                <button class="btn btn-primary" id="assignExerciseBtn">
                    <i class="fas fa-plus"></i> Assign Exercise
                </button>
                <button class="btn btn-secondary" id="updatePlanBtn">
                    <i class="fas fa-edit"></i> Update Plan
                </button>
                <button class="btn btn-danger" id="sendMessageBtn">
                    <i class="fas fa-paper-plane"></i> Send Message
                </button>
            </div>
        `;
        
        this.setupEventListeners();
    }
    
    /**
     * Render exercise history
     */
    renderExerciseHistory(exercises) {
        if (!exercises || exercises.length === 0) {
            return '<p class="no-data">No exercises yet</p>';
        }
        
        return `
            <table class="exercise-table">
                <thead>
                    <tr>
                        <th>Exercise</th>
                        <th>Reps</th>
                        <th>Quality</th>
                        <th>Date</th>
                    </tr>
                </thead>
                <tbody>
                    ${exercises.slice(0, 10).map(ex => `
                        <tr>
                            <td>${ex.name}</td>
                            <td>${ex.reps}</td>
                            <td><span class="quality-badge ${ex.quality > 70 ? 'good' : 'poor'}">${ex.quality}%</span></td>
                            <td>${new Date(ex.date).toLocaleDateString()}</td>
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        `;
    }
    
    /**
     * Show assign exercise dialog
     */
    showAssignDialog() {
        if (!this.selectedPatient) {
            alert('Please select a patient first');
            return;
        }
        
        const dialog = document.createElement('div');
        dialog.className = 'modal-dialog';
        dialog.innerHTML = `
            <div class="modal-content">
                <div class="modal-header">
                    <h3>Assign Exercise</h3>
                    <button class="close-btn">&times;</button>
                </div>
                <div class="modal-body">
                    <div class="form-group">
                        <label>Select Exercise</label>
                        <select id="exerciseSelect">
                            <option>Shoulder Flexion</option>
                            <option>Shoulder Abduction</option>
                            <option>Knee Extension</option>
                            <option>Hip Abduction</option>
                            <option>Neck Rotation</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label>Target Reps</label>
                        <input type="number" id="targetReps" value="10">
                    </div>
                    <div class="form-group">
                        <label>Instructions</label>
                        <textarea id="instructions" placeholder="Enter special instructions..."></textarea>
                    </div>
                </div>
                <div class="modal-footer">
                    <button class="btn btn-secondary close-btn">Cancel</button>
                    <button class="btn btn-primary assign-submit-btn">Assign</button>
                </div>
            </div>
        `;
        
        document.body.appendChild(dialog);
        
        dialog.querySelector('.close-btn').addEventListener('click', () => dialog.remove());
        dialog.querySelector('.assign-submit-btn').addEventListener('click', 
            () => this.submitAssignment(dialog));
    }
    
    /**
     * Submit exercise assignment
     */
    async submitAssignment(dialog) {
        const exercise = dialog.querySelector('#exerciseSelect').value;
        const reps = dialog.querySelector('#targetReps').value;
        const instructions = dialog.querySelector('#instructions').value;
        
        try {
            const response = await fetch(API_BASE + '/therapist/assign-exercise', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${localStorage.getItem('authToken')}`
                },
                body: JSON.stringify({
                    patient_id: this.selectedPatient.id,
                    exercise_name: exercise,
                    target_reps: parseInt(reps),
                    instructions
                })
            });
            
            if (response.ok) {
                alert(i18n.t('success') + ': Exercise assigned');
                dialog.remove();
            }
        } catch (error) {
            console.error('Error assigning exercise:', error);
        }
    }
    
    /**
     * Show update plan dialog
     */
    showUpdatePlanDialog() {
        if (!this.selectedPatient) {
            alert('Please select a patient first');
            return;
        }
        
        alert('Plan update feature coming soon');
    }
}

// Create globally accessible instance
const therapistDashboard = new TherapistDashboard();

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = therapistDashboard;
}
