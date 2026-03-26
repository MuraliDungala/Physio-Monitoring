#!/usr/bin/env python3
"""
Quick Model Training Script
Trains ML models for physiotherapy exercise recognition
"""

import os
import sys
import logging

# Add current directory to path
sys.path.append(os.path.dirname(__file__))

from ml_training.train_models import main

if __name__ == "__main__":
    print("🤖 Training ML Models for Physiotherapy Exercise Recognition")
    print("=" * 60)
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    try:
        # Run training
        trainer, results = main()
        
        print("\n" + "=" * 60)
        print("🎉 Training Completed Successfully!")
        print("=" * 60)
        
        print("\n📊 Model Results:")
        for model_name, accuracy in results.items():
            print(f"  {model_name.upper()}: {accuracy:.4f} accuracy")
        
        print("\n💾 Models saved to: ./models/exercise_recognition/")
        print("📈 Training report saved to: ./models/training_results.json")
        print("\n🚀 Ready to use in the Physiotherapy Monitoring System!")
        
    except Exception as e:
        print(f"❌ Training failed: {e}")
        sys.exit(1)
