/**
 * PhysioMonitor ML Injury Risk Prediction
 * Uses biomechanical data to predict injury risk
 * Based on: Joint angles, Movement patterns, Quality score
 */

class InjuryRiskPredictor {
    constructor() {
        this.riskThresholds = {
            high: 0.7,
            medium: 0.4,
            low: 0
        };
        
        this.riskFactors = [
            'poor_posture',
            'excessive_angle',
            'high_fatigue',
            'rapid_movements',
            'joint_stress',
            'imbalance'
        ];
        
        this.bodyPartRisks = {
            shoulder: { angle_max: 170, angle_min: 10, quality_min: 60 },
            elbow: { angle_max: 160, angle_min: 5, quality_min: 55 },
            knee: { angle_max: 120, angle_min: 10, quality_min: 65 },
            hip: { angle_max: 140, angle_min: 0, quality_min: 60 },
            neck: { angle_max: 80, angle_min: 0, quality_min: 70 },
            wrist: { angle_max: 100, angle_min: 0, quality_min: 50 },
            ankle: { angle_max: 120, angle_min: 0, quality_min: 60 },
            back: { angle_max: 45, angle_min: 0, quality_min: 65 }
        };
    }
    
    /**
     * Predict injury risk based on session data
     * @param {object} sessionData - Session metrics
     * @returns {object} Risk assessment
     */
    predictRisk(sessionData = {}) {
        const {
            exerciseName = 'unknown',
            bodyPart = 'shoulder',
            jointAngle = 90,
            qualityScore = 70,
            reps = 10,
            duration = 60,
            speed = 'normal',
            previousDays = []
        } = sessionData;
        
        let riskScore = 0;
        const activeFactors = [];
        
        // 1. Joint Angle Analysis
        const angleRisk = this.analyzeJointAngle(bodyPart, jointAngle);
        riskScore += angleRisk.score * 0.3;
        if (angleRisk.isAbnormal) {
            activeFactors.push({
                factor: 'excessive_angle',
                severity: angleRisk.severity,
                message: `Joint angle ${jointAngle}° is abnormal for ${bodyPart}`
            });
        }
        
        // 2. Quality Score Analysis
        const qualityRisk = this.analyzeQuality(bodyPart, qualityScore);
        riskScore += qualityRisk.score * 0.25;
        if (qualityRisk.isPoor) {
            activeFactors.push({
                factor: 'poor_posture',
                severity: qualityRisk.severity,
                message: `Form quality is low (${qualityScore}%), increasing injury risk`
            });
        }
        
        // 3. Fatigue Analysis
        const fatigueRisk = this.analyzeFatigue(reps, duration, speed);
        riskScore += fatigueRisk.score * 0.2;
        if (fatigueRisk.isHigh) {
            activeFactors.push({
                factor: 'high_fatigue',
                severity: fatigueRisk.severity,
                message: 'High fatigue level detected'
            });
        }
        
        // 4. Pattern Analysis (from historical data)
        const patternRisk = this.analyzePatterns(previousDays, exerciseName);
        riskScore += patternRisk.score * 0.15;
        if (patternRisk.hasWarning) {
            activeFactors.push({
                factor: patternRisk.factor,
                severity: patternRisk.severity,
                message: patternRisk.message
            });
        }
        
        // Normalize risk score to 0-1
        const normalizedRisk = Math.min(1, Math.max(0, riskScore));
        
        return {
            riskScore: normalizedRisk,
            riskLevel: this.getRiskLevel(normalizedRisk),
            activeFactors,
            recommendations: this.generateRecommendations(
                normalizedRisk,
                bodyPart,
                activeFactors
            ),
            timestamp: new Date()
        };
    }
    
    /**
     * Analyze joint angle risk
     */
    analyzeJointAngle(bodyPart, angle) {
        const limits = this.bodyPartRisks[bodyPart] || this.bodyPartRisks.shoulder;
        
        if (angle > limits.angle_max || angle < limits.angle_min) {
            const deviation = Math.max(
                angle - limits.angle_max,
                limits.angle_min - angle
            );
            
            const severity = Math.min(1, deviation / 30); // 30° = extreme
            
            return {
                score: Math.min(1, severity * 1.5),
                isAbnormal: true,
                severity: severity > 0.7 ? 'high' : 'medium'
            };
        }
        
        return {
            score: 0,
            isAbnormal: false,
            severity: 'low'
        };
    }
    
    /**
     * Analyze quality score risk
     */
    analyzeQuality(bodyPart, qualityScore) {
        const limits = this.bodyPartRisks[bodyPart] || this.bodyPartRisks.shoulder;
        const minQuality = limits.quality_min;
        
        if (qualityScore < minQuality) {
            const deficit = minQuality - qualityScore;
            const severity = Math.min(1, deficit / 40); // 40% = extreme
            
            return {
                score: Math.min(1, severity * 1.2),
                isPoor: true,
                severity: severity > 0.7 ? 'high' : 'medium'
            };
        }
        
        return {
            score: Math.max(0, (100 - qualityScore) / 100 * 0.3),
            isPoor: false,
            severity: 'low'
        };
    }
    
    /**
     * Analyze fatigue risk
     */
    analyzeFatigue(reps, durationSeconds, speed = 'normal') {
        const durationMinutes = durationSeconds / 60;
        const repsPerMinute = reps / Math.max(1, durationMinutes);
        
        // High fatigue if: many reps in short time OR long duration
        let fatigueScore = 0;
        
        if (repsPerMinute > 3) {
            fatigueScore += (repsPerMinute - 3) / 5; // Fast pace
        }
        
        if (durationMinutes > 15) {
            fatigueScore += (durationMinutes - 15) / 30; // Long duration
        }
        
        if (speed === 'fast') {
            fatigueScore += 0.2;
        }
        
        const normalizedScore = Math.min(1, fatigueScore);
        
        return {
            score: normalizedScore,
            isHigh: normalizedScore > 0.5,
            severity: normalizedScore > 0.7 ? 'high' : normalizedScore > 0.4 ? 'medium' : 'low'
        };
    }
    
    /**
     * Analyze historical patterns
     */
    analyzePatterns(previousDays = [], exerciseName = '') {
        if (previousDays.length < 2) {
            return {
                score: 0,
                hasWarning: false,
                factor: null,
                message: null
            };
        }
        
        // Check for overuse (same exercise too frequently)
        const sameExerciseCount = previousDays.filter(
            day => day.exercises?.some(ex => ex.name === exerciseName)
        ).length;
        
        if (sameExerciseCount > 3) {
            return {
                score: 0.3,
                hasWarning: true,
                factor: 'overuse',
                severity: 'medium',
                message: `${exerciseName} has been done frequently. Allow recovery time.`
            };
        }
        
        // Check for intensity escalation
        const recentReps = previousDays.slice(0, 3).map(d => 
            d.exercises?.reduce((sum, e) => sum + (e.reps || 0), 0) || 0
        );
        
        if (recentReps.length > 1) {
            const avgRecent = recentReps.reduce((a, b) => a + b) / recentReps.length;
            const increase = ((recentReps[0] - avgRecent) / avgRecent) * 100;
            
            if (increase > 50) {
                return {
                    score: 0.2,
                    hasWarning: true,
                    factor: 'rapid_escalation',
                    severity: 'medium',
                    message: 'Significant increase in intensity. Maintain gradual progression.'
                };
            }
        }
        
        return {
            score: 0,
            hasWarning: false,
            factor: null,
            message: null
        };
    }
    
    /**
     * Get risk level text
     */
    getRiskLevel(riskScore) {
        if (riskScore >= this.riskThresholds.high) {
            return 'HIGH';
        } else if (riskScore >= this.riskThresholds.medium) {
            return 'MEDIUM';
        } else {
            return 'LOW';
        }
    }
    
    /**
     * Generate recommendations
     */
    generateRecommendations(riskScore, bodyPart, activeFactors) {
        const recommendations = [];
        
        if (riskScore >= this.riskThresholds.high) {
            recommendations.push(
                '⚠️ High injury risk detected. Consider taking a break.',
                `✓ Focus on form quality for ${bodyPart}`,
                '✓ Reduce reps and increase recovery time',
                '✓ Consult with your physiotherapist'
            );
        } else if (riskScore >= this.riskThresholds.medium) {
            recommendations.push(
                '⚠️ Moderate injury risk. Proceed with caution.',
                'Focus on proper technique over quantity',
                'Increase rest periods between sets',
                'Monitor for pain or discomfort'
            );
        } else {
            recommendations.push(
                '✓ Low risk. Form looks good!',
                'You can increase intensity gradually',
                'Continue with proper technique',
                'Track your progress'
            );
        }
        
        // Add specific recommendations for active factors
        activeFactors.forEach(factor => {
            if (factor.factor === 'poor_posture') {
                recommendations.push('📹 Watch your form in the mirror or video');
            } else if (factor.factor === 'excessive_angle') {
                recommendations.push(`📐 Reduce joint angle for ${bodyPart}`);
            } else if (factor.factor === 'high_fatigue') {
                recommendations.push('⏸️ Take a longer rest or reduce reps');
            } else if (factor.factor === 'overuse') {
                recommendations.push('🔄 Alternate with other exercises');
            }
        });
        
        return recommendations;
    }
    
    /**
     * Get risk color for UI
     */
    getRiskColor(riskScore) {
        if (riskScore >= this.riskThresholds.high) {
            return '#ef4444'; // Red
        } else if (riskScore >= this.riskThresholds.medium) {
            return '#f59e0b'; // Amber
        } else {
            return '#10b981'; // Green
        }
    }
}

// Create globally accessible instance
const injuryPredictor = new InjuryRiskPredictor();

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = injuryPredictor;
}
