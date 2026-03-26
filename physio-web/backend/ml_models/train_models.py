"""
Training script for exercise classification models
Uses UI-PMRD and KIMORE dataset patterns for training
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ml_models.exercise_classifier import ExerciseClassifier
import logging

def main():
    """Main training function"""
    print("🚀 Starting ML Model Training for Exercise Classification...")
    print("📊 Using UI-PMRD and KIMORE dataset patterns...")
    
    # Initialize classifier
    classifier = ExerciseClassifier()
    
    # Train models
    print("🏋️ Training models on exercise biomechanics data...")
    classifier.train_models()
    
    print("✅ Training completed!")
    print("🎯 Models ready for exercise detection and form analysis")

if __name__ == "__main__":
    main()
