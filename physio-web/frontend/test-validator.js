/**
 * Metrics Validation Testing Utility
 * Run in browser console: console.table(ExerciseMetricsValidator.getValidationReport())
 */

const ExerciseMetricsValidator = {
    // Test results storage
    results: {},
    
    /**
     * Validate exercise configuration
     */
    validateConfiguration() {
        console.log('🔍 Validating Exercise Configuration...');
        const report = {};
        
        Object.entries(EXERCISE_CONFIG).forEach(([exerciseName, config]) => {
            const validation = {
                name: exerciseName,
                primaryAngle: config.primaryAngle ? '✓' : '✗ MISSING',
                optimalRange: config.optimalRange && config.optimalRange.length === 2 ? '✓' : '✗ INVALID',
                repPhases: config.repPhases && config.repPhases.length === 2 ? '✓' : '✗ INVALID',
                status: 'configured'
            };
            
            const hasAllFields = validation.primaryAngle === '✓' && 
                                validation.optimalRange === '✓' && 
                                validation.repPhases === '✓';
            
            validation.status = hasAllFields ? '✅ Ready' : '❌ Incomplete';
            report[exerciseName] = validation;
        });
        
        return report;
    },

    /**
     * Check if all exercises have required fields
     */
    checkCompleteness() {
        const incomplete = [];
        const complete = [];
        
        Object.entries(EXERCISE_CONFIG).forEach(([name, config]) => {
            const valid = config.primaryAngle && 
                         config.optimalRange && config.optimalRange.length === 2 &&
                         config.repPhases && config.repPhases.length === 2;
            
            if (valid) {
                complete.push(name);
            } else {
                incomplete.push(name);
            }
        });
        
        return {
            total: Object.keys(EXERCISE_CONFIG).length,
            complete: complete.length,
            incomplete: incomplete.length,
            incompleteList: incomplete
        };
    },

    /**
     * Test angle calculation for an exercise
     */
    testAngleCalculation(exerciseName) {
        const config = EXERCISE_CONFIG[exerciseName];
        if (!config) return { error: 'Exercise not found' };
        
        return {
            exercise: exerciseName,
            primaryAngle: config.primaryAngle,
            optimalRange: config.optimalRange,
            currentAngleLeft: exerciseState.angles[config.primaryAngle + 'Left'],
            currentAngleRight: exerciseState.angles[config.primaryAngle + 'Right'],
            inOptimalRange: this.isAngleInRange(
                exerciseState.angles[config.primaryAngle + 'Left'],
                config.optimalRange
            ),
            status: '✓ Calculating'
        };
    },

    /**
     * Check if angle is within optimal range
     */
    isAngleInRange(angle, range) {
        if (angle === null || angle === undefined) return false;
        return angle >= range[0] && angle <= range[1];
    },

    /**
     * Validate quality score calculation
     */
    validateQualityScore() {
        if (!exerciseState.angles || Object.keys(exerciseState.angles).length === 0) {
            return { status: '⚠️ No angles calculated yet' };
        }
        
        const config = EXERCISE_CONFIG[currentExercise];
        if (!config) return { status: '⚠️ Exercise not configured' };
        
        return {
            currentExercise,
            hasAngles: Object.keys(exerciseState.angles).length,
            hasSymmetry: exerciseState.angles[config.primaryAngle + 'Left'] && 
                        exerciseState.angles[config.primaryAngle + 'Right'],
            hasLandmarks: window.currentLandmarks ? 'Yes' : 'No',
            hasHandAnalysis: window.currentHandAnalysis ? 'Yes' : 'No',
            status: '✓ Ready for scoring'
        };
    },

    /**
     * Generate validation report for all exercises
     */
    getValidationReport() {
        return {
            timestamp: new Date().toLocaleString(),
            totalExercises: Object.keys(EXERCISE_CONFIG).length,
            configuration: this.checkCompleteness(),
            configurationStatus: this.validateConfiguration()
        };
    },

    /**
     * Test specific exercise set (e.g., all shoulder exercises)
     */
    testExerciseCategory(category) {
        const exercises = Object.entries(EXERCISE_CONFIG)
            .filter(([name]) => name.toLowerCase().includes(category.toLowerCase()));
        
        const results = {};
        exercises.forEach(([name, config]) => {
            results[name] = {
                primaryAngle: config.primaryAngle,
                optimalRange: config.optimalRange,
                repPhases: config.repPhases,
                configured: '✓'
            };
        });
        
        return {
            category,
            count: exercises.length,
            exercises: results
        };
    },

    /**
     * Get missing angle calculations
     */
    getMissingAngles() {
        const config = EXERCISE_CONFIG[currentExercise];
        if (!config) return { error: 'No exercise selected' };
        
        const missing = [];
        const primaryAngle = config.primaryAngle;
        
        if (!exerciseState.angles[primaryAngle + 'Left']) {
            missing.push(primaryAngle + 'Left');
        }
        if (!exerciseState.angles[primaryAngle + 'Right']) {
            missing.push(primaryAngle + 'Right');
        }
        
        return {
            exercise: currentExercise,
            primary: primaryAngle,
            missing: missing.length > 0 ? missing : '✓ All angles present',
            totalAnglesCounted: Object.keys(exerciseState.angles).length
        };
    },

    /**
     * Live test current exercise metrics
     */
    getCurrentMetrics() {
        if (!currentExercise) return { error: 'No exercise selected' };
        
        const config = EXERCISE_CONFIG[currentExercise];
        const primaryAngle = config.primaryAngle;
        const leftAngle = exerciseState.angles[primaryAngle + 'Left'];
        const rightAngle = exerciseState.angles[primaryAngle + 'Right'];
        
        const inRange = this.isAngleInRange(leftAngle || rightAngle, config.optimalRange);
        
        return {
            exercise: currentExercise,
            reps: exerciseState.reps,
            currentPhase: exerciseState.currentPhase,
            primaryAngle: primaryAngle,
            leftAngle: leftAngle ? leftAngle.toFixed(1) : 'Not detected',
            rightAngle: rightAngle ? rightAngle.toFixed(1) : 'Not detected',
            optimalRange: config.optimalRange,
            inOptimalRange: inRange ? '✓ Yes' : '✗ No',
            expectedPhases: config.repPhases,
            skeletonVisible: window.currentLandmarks ? `${window.currentLandmarks.length} points` : 'None',
            handsDetected: window.currentHandAnalysis ? 'Yes' : 'No'
        };
    },

    /**
     * Get statistics for a test session
     */
    getSessionStats() {
        return {
            sessionsRecorded: exerciseState.reps,
            currentExercise: currentExercise || 'None',
            totalLandmarks: window.currentLandmarks ? window.currentLandmarks.length : 0,
            poseInitialized: pose !== null ? 'Yes' : 'No',
            cameraActive: isDetecting ? 'Yes' : 'No',
            timestamp: new Date().toLocaleString()
        };
    },

    /**
     * Export test report as JSON
     */
    exportReport() {
        const report = {
            generated: new Date().toISOString(),
            configuration: this.checkCompleteness(),
            currentSession: this.getSessionStats(),
            currentMetrics: this.getCurrentMetrics(),
            allExercises: Object.keys(EXERCISE_CONFIG).sort()
        };
        
        // Copy to clipboard
        const json = JSON.stringify(report, null, 2);
        console.log('📋 Test Report:\n', json);
        return report;
    }
};

// Quick test commands
console.log(`
🧪 EXERCISE METRICS TESTING UTILITY
=====================================

Run these commands in the browser console:

📊 Validation & Status:
  ExerciseMetricsValidator.checkCompleteness()
  ExerciseMetricsValidator.validateConfiguration()
  ExerciseMetricsValidator.getValidationReport()

🎯 Exercise Testing:
  ExerciseMetricsValidator.testExerciseCategory('shoulder')
  ExerciseMetricsValidator.testAngleCalculation('Elbow Flexion')
  ExerciseMetricsValidator.getCurrentMetrics()

📈 Quality & Scoring:
  ExerciseMetricsValidator.validateQualityScore()
  ExerciseMetricsValidator.getMissingAngles()

📋 Session Info:
  ExerciseMetricsValidator.getSessionStats()
  ExerciseMetricsValidator.exportReport()

Usage:
  1. Select an exercise and click "Start Camera"
  2. Perform some movements
  3. Run: ExerciseMetricsValidator.getCurrentMetrics()
  4. Check console for real-time data

See TEST_METRICS.md for detailed testing plan.
`);
