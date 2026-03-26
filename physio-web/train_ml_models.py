#!/usr/bin/env python3
"""
ML Model Training Launcher
Quick script to train ML models for the physiotherapy system
"""

import os
import sys
import subprocess
from pathlib import Path

def main():
    print("🤖 ML Model Training for Physiotherapy Monitoring System")
    print("=" * 60)
    
    # Check if backend directory exists
    backend_dir = Path("backend")
    if not backend_dir.exists():
        print("❌ Backend directory not found!")
        print("Please run this script from the physio-web root directory")
        sys.exit(1)
    
    # Change to backend directory
    os.chdir(backend_dir)
    
    print("📦 Installing ML training dependencies...")
    
    # Install additional ML dependencies if needed
    ml_packages = ["pandas", "matplotlib", "seaborn", "h5py"]
    for package in ml_packages:
        try:
            __import__(package)
            print(f"✅ {package} already installed")
        except ImportError:
            print(f"📦 Installing {package}...")
            subprocess.run([sys.executable, "-m", "pip", "install", package])
    
    print("\n🚀 Starting ML model training...")
    print("This will train SVM, Random Forest, and MLP models")
    print("Using synthetic KIMORE and UI-PMRD datasets\n")
    
    try:
        # Run the training script
        result = subprocess.run([sys.executable, "train_models.py"], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Training completed successfully!")
            print("\n" + result.stdout)
            
            # Check if models were created
            models_dir = Path("../models/exercise_recognition")
            if models_dir.exists():
                model_files = list(models_dir.glob("*.pkl"))
                if model_files:
                    print(f"\n💾 {len(model_files)} model(s) created:")
                    for model_file in model_files:
                        print(f"  - {model_file.name}")
                else:
                    print("\n⚠️  No model files found - training may have failed")
            else:
                print("\n⚠️  Models directory not created")
                
        else:
            print("❌ Training failed!")
            print("Error output:")
            print(result.stderr)
            sys.exit(1)
            
    except Exception as e:
        print(f"❌ Error running training: {e}")
        sys.exit(1)
    
    print("\n🎯 Next Steps:")
    print("1. Start the system: python start.py")
    print("2. The trained models will be used for exercise recognition")
    print("3. Check models/ directory for trained model files")
    print("4. View training_results.json for training details")

if __name__ == "__main__":
    main()
