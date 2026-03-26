"""
Complete ML Training and Evaluation Pipeline
Integrates KIMORE and UI-PMRD datasets for comprehensive model training
"""

import os
import sys
import argparse
import logging
from pathlib import Path

# Add paths for imports
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from ml_training.train_models import PhysioMLTrainer
from ml_training.dataset_loader import DatasetLoader
from ml_training.model_evaluation import ModelEvaluator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('ml_training.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def main():
    parser = argparse.ArgumentParser(description='Train and evaluate physiotherapy exercise recognition models')
    parser.add_argument('--kimore-path', type=str, default=None, help='Path to KIMORE dataset')
    parser.add_argument('--ui-pmrd-path', type=str, default=None, help='Path to UI-PMRD dataset')
    parser.add_argument('--output-dir', type=str, default='./models', help='Output directory for models')
    parser.add_argument('--evaluate-only', action='store_true', help='Only evaluate existing models')
    parser.add_argument('--test-data', type=str, default=None, help='Path to test dataset for evaluation')
    
    args = parser.parse_args()
    
    # Create output directory
    output_dir = Path(args.output_dir)
    output_dir.mkdir(exist_ok=True)
    
    logger.info("Starting ML Training and Evaluation Pipeline")
    logger.info(f"Output directory: {output_dir}")
    
    if args.evaluate_only:
        # Evaluation only mode
        logger.info("Running evaluation only mode...")
        
        evaluator = ModelEvaluator()
        
        # Load test data
        if args.test_data:
            loader = DatasetLoader()
            
            if 'kimore' in args.test_data.lower():
                X_test, y_test, metadata = loader.load_kimore_dataset(args.test_data)
            elif 'ui-pmrd' in args.test_data.lower():
                X_test, y_test, metadata = loader.load_ui_pmrd_dataset(args.test_data)
            else:
                logger.error("Unsupported test dataset format")
                return
            
            # Preprocess for MediaPipe
            X_test = loader.preprocess_for_mediapipe(X_test, metadata)
            
            # Load and evaluate models
            loaded_models = evaluator.load_and_evaluate_saved_models(str(output_dir), X_test, y_test)
            
            # Generate comprehensive report
            evaluator.generate_evaluation_report(str(output_dir / "evaluation"))
            
        else:
            logger.error("Test data path required for evaluation-only mode")
    
    else:
        # Training mode
        logger.info("Running training mode...")
        
        # Initialize trainer
        trainer = PhysioMLTrainer()
        
        # Train models with datasets
        results = trainer.train_all_models(
            kimore_path=args.kimore_path,
            ui_pmrd_path=args.ui_pmrd_path
        )
        
        logger.info("Training completed!")
        logger.info("Model Results:")
        for model_name, accuracy in results.items():
            logger.info(f"  {model_name}: {accuracy:.4f}")
        
        # Evaluate models (if test data provided)
        if args.test_data:
            logger.info("Evaluating models on test data...")
            
            evaluator = ModelEvaluator()
            loader = DatasetLoader()
            
            if 'kimore' in args.test_data.lower():
                X_test, y_test, metadata = loader.load_kimore_dataset(args.test_data)
            elif 'ui-pmrd' in args.test_data.lower():
                X_test, y_test, metadata = loader.load_ui_pmrd_dataset(args.test_data)
            else:
                logger.error("Unsupported test dataset format")
                return
            
            # Preprocess for MediaPipe
            X_test = loader.preprocess_for_mediapipe(X_test, metadata)
            
            # Load trained models and evaluate
            loaded_models = evaluator.load_and_evaluate_saved_models(str(output_dir), X_test, y_test)
            
            # Generate comprehensive report
            evaluator.generate_evaluation_report(str(output_dir / "evaluation"))
        
        logger.info("Pipeline completed successfully!")

if __name__ == "__main__":
    main()
