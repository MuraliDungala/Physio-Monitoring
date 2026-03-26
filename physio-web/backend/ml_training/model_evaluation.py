"""
Model Evaluation and Validation for Physiotherapy Exercise Recognition
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    confusion_matrix, classification_report, roc_auc_score,
    precision_recall_curve, roc_curve
)
from sklearn.model_selection import cross_val_score, learning_curve
import joblib
import json
import logging
from typing import Dict, List, Tuple, Any
from pathlib import Path

logger = logging.getLogger(__name__)

class ModelEvaluator:
    """
    Comprehensive model evaluation for physiotherapy exercise recognition
    """
    
    def __init__(self):
        self.evaluation_results = {}
        self.model_metrics = {}
        
    def evaluate_model_comprehensive(self, model, X_test: np.ndarray, y_test: np.ndarray, 
                                  model_name: str, label_encoder=None) -> Dict:
        """
        Comprehensive evaluation of a trained model
        """
        logger.info(f"Evaluating {model_name} model...")
        
        # Basic predictions
        y_pred = model.predict(X_test)
        y_pred_proba = None
        
        # Get probabilities if available
        if hasattr(model, 'predict_proba'):
            y_pred_proba = model.predict_proba(X_test)
        
        # Basic metrics
        accuracy = accuracy_score(y_test, y_pred)
        precision = precision_score(y_test, y_pred, average='weighted', zero_division=0)
        recall = recall_score(y_test, y_pred, average='weighted', zero_division=0)
        f1 = f1_score(y_test, y_pred, average='weighted', zero_division=0)
        
        # Per-class metrics
        precision_per_class = precision_score(y_test, y_pred, average=None, zero_division=0)
        recall_per_class = recall_score(y_test, y_pred, average=None, zero_division=0)
        f1_per_class = f1_score(y_test, y_pred, average=None, zero_division=0)
        
        # Confusion matrix
        cm = confusion_matrix(y_test, y_pred)
        
        # Cross-validation
        cv_scores = cross_val_score(model, X_test, y_test, cv=5, scoring='accuracy')
        
        # Learning curve
        train_sizes, train_scores, val_scores = learning_curve(
            model, X_test, y_test, cv=5, n_jobs=-1, 
            train_sizes=np.linspace(0.1, 1.0, 10)
        )
        
        # Compile results
        results = {
            'model_name': model_name,
            'accuracy': accuracy,
            'precision_weighted': precision,
            'recall_weighted': recall,
            'f1_weighted': f1,
            'precision_per_class': precision_per_class.tolist(),
            'recall_per_class': recall_per_class.tolist(),
            'f1_per_class': f1_per_class.tolist(),
            'confusion_matrix': cm.tolist(),
            'cv_scores': cv_scores.tolist(),
            'cv_mean': cv_scores.mean(),
            'cv_std': cv_scores.std(),
            'learning_curve': {
                'train_sizes': train_sizes.tolist(),
                'train_scores_mean': train_scores.mean(axis=1).tolist(),
                'train_scores_std': train_scores.std(axis=1).tolist(),
                'val_scores_mean': val_scores.mean(axis=1).tolist(),
                'val_scores_std': val_scores.std(axis=1).tolist()
            }
        }
        
        # Add class names if available
        if label_encoder:
            results['class_names'] = label_encoder.classes_.tolist()
        
        # Add ROC AUC for multi-class if probabilities available
        if y_pred_proba is not None and len(np.unique(y_test)) > 2:
            try:
                roc_auc = roc_auc_score(y_test, y_pred_proba, multi_class='ovr', average='weighted')
                results['roc_auc'] = roc_auc
            except Exception as e:
                logger.warning(f"Could not compute ROC AUC: {e}")
        
        self.evaluation_results[model_name] = results
        logger.info(f"{model_name} evaluation completed. Accuracy: {accuracy:.4f}")
        
        return results
    
    def compare_models(self, models_dict: Dict[str, Any], X_test: np.ndarray, 
                      y_test: np.ndarray, label_encoder=None) -> pd.DataFrame:
        """
        Compare multiple models side by side
        """
        comparison_data = []
        
        for model_name, model in models_dict.items():
            results = self.evaluate_model_comprehensive(model, X_test, y_test, model_name, label_encoder)
            
            comparison_data.append({
                'Model': model_name,
                'Accuracy': results['accuracy'],
                'Precision': results['precision_weighted'],
                'Recall': results['recall_weighted'],
                'F1-Score': results['f1_weighted'],
                'CV-Mean': results['cv_mean'],
                'CV-Std': results['cv_std']
            })
        
        comparison_df = pd.DataFrame(comparison_data)
        comparison_df = comparison_df.sort_values('Accuracy', ascending=False)
        
        logger.info("Model comparison completed")
        logger.info(comparison_df.to_string())
        
        return comparison_df
    
    def plot_confusion_matrix(self, model_name: str, save_path: str = None):
        """
        Plot confusion matrix for a model
        """
        if model_name not in self.evaluation_results:
            logger.error(f"No evaluation results found for {model_name}")
            return
        
        results = self.evaluation_results[model_name]
        cm = np.array(results['confusion_matrix'])
        class_names = results.get('class_names', None)
        
        plt.figure(figsize=(10, 8))
        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
                   xticklabels=class_names, yticklabels=class_names)
        plt.title(f'Confusion Matrix - {model_name}')
        plt.xlabel('Predicted')
        plt.ylabel('Actual')
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            logger.info(f"Confusion matrix saved to {save_path}")
        
        plt.show()
    
    def plot_learning_curves(self, model_name: str, save_path: str = None):
        """
        Plot learning curves for a model
        """
        if model_name not in self.evaluation_results:
            logger.error(f"No evaluation results found for {model_name}")
            return
        
        results = self.evaluation_results[model_name]
        lc = results['learning_curve']
        
        train_sizes = lc['train_sizes']
        train_mean = lc['train_scores_mean']
        train_std = lc['train_scores_std']
        val_mean = lc['val_scores_mean']
        val_std = lc['val_scores_std']
        
        plt.figure(figsize=(10, 6))
        
        # Plot training scores
        plt.plot(train_sizes, train_mean, 'o-', color='blue', label='Training Score')
        plt.fill_between(train_sizes, 
                         np.array(train_mean) - np.array(train_std),
                         np.array(train_mean) + np.array(train_std),
                         alpha=0.1, color='blue')
        
        # Plot validation scores
        plt.plot(train_sizes, val_mean, 'o-', color='red', label='Validation Score')
        plt.fill_between(train_sizes,
                         np.array(val_mean) - np.array(val_std),
                         np.array(val_mean) + np.array(val_std),
                         alpha=0.1, color='red')
        
        plt.title(f'Learning Curves - {model_name}')
        plt.xlabel('Training Set Size')
        plt.ylabel('Score')
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            logger.info(f"Learning curves saved to {save_path}")
        
        plt.show()
    
    def plot_model_comparison(self, comparison_df: pd.DataFrame, save_path: str = None):
        """
        Plot model comparison chart
        """
        metrics = ['Accuracy', 'Precision', 'Recall', 'F1-Score']
        
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        axes = axes.ravel()
        
        for i, metric in enumerate(metrics):
            ax = axes[i]
            bars = ax.bar(comparison_df['Model'], comparison_df[metric])
            ax.set_title(f'{metric} Comparison')
            ax.set_ylabel(metric)
            ax.tick_params(axis='x', rotation=45)
            
            # Add value labels on bars
            for bar, value in zip(bars, comparison_df[metric]):
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height + 0.01,
                       f'{value:.3f}', ha='center', va='bottom')
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            logger.info(f"Model comparison chart saved to {save_path}")
        
        plt.show()
    
    def analyze_exercise_performance(self, model_name: str, label_encoder=None) -> Dict:
        """
        Analyze performance per exercise type
        """
        if model_name not in self.evaluation_results:
            logger.error(f"No evaluation results found for {model_name}")
            return {}
        
        results = self.evaluation_results[model_name]
        
        if not label_encoder:
            logger.warning("No label encoder provided, using numeric class names")
            class_names = [f"Class_{i}" for i in range(len(results['precision_per_class']))]
        else:
            class_names = label_encoder.classes_
        
        exercise_performance = {}
        
        for i, class_name in enumerate(class_names):
            if i < len(results['precision_per_class']):
                exercise_performance[class_name] = {
                    'precision': results['precision_per_class'][i],
                    'recall': results['recall_per_class'][i],
                    'f1_score': results['f1_per_class'][i]
                }
        
        # Find best and worst performing exercises
        if exercise_performance:
            best_exercise = max(exercise_performance.keys(), 
                              key=lambda x: exercise_performance[x]['f1_score'])
            worst_exercise = min(exercise_performance.keys(), 
                               key=lambda x: exercise_performance[x]['f1_score'])
            
            analysis = {
                'exercise_performance': exercise_performance,
                'best_exercise': {
                    'name': best_exercise,
                    'metrics': exercise_performance[best_exercise]
                },
                'worst_exercise': {
                    'name': worst_exercise,
                    'metrics': exercise_performance[worst_exercise]
                },
                'average_f1': np.mean([perf['f1_score'] for perf in exercise_performance.values()])
            }
            
            logger.info(f"Best performing exercise: {best_exercise}")
            logger.info(f"Worst performing exercise: {worst_exercise}")
            
            return analysis
        
        return {}
    
    def generate_evaluation_report(self, output_dir: str = "evaluation_reports"):
        """
        Generate comprehensive evaluation report
        """
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        report = {
            'evaluation_summary': {
                'models_evaluated': list(self.evaluation_results.keys()),
                'evaluation_date': str(pd.Timestamp.now()),
                'total_models': len(self.evaluation_results)
            },
            'detailed_results': self.evaluation_results
        }
        
        # Save detailed report
        report_path = output_path / "evaluation_report.json"
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        logger.info(f"Evaluation report saved to {report_path}")
        
        # Generate plots for each model
        for model_name in self.evaluation_results.keys():
            model_dir = output_path / model_name
            model_dir.mkdir(exist_ok=True)
            
            # Plot confusion matrix
            self.plot_confusion_matrix(model_name, 
                                      save_path=str(model_dir / "confusion_matrix.png"))
            
            # Plot learning curves
            self.plot_learning_curves(model_name, 
                                     save_path=str(model_dir / "learning_curves.png"))
        
        # Generate model comparison if multiple models
        if len(self.evaluation_results) > 1:
            comparison_data = []
            for model_name, results in self.evaluation_results.items():
                comparison_data.append({
                    'Model': model_name,
                    'Accuracy': results['accuracy'],
                    'Precision': results['precision_weighted'],
                    'Recall': results['recall_weighted'],
                    'F1-Score': results['f1_weighted']
                })
            
            comparison_df = pd.DataFrame(comparison_data)
            self.plot_model_comparison(comparison_df, 
                                     save_path=str(output_path / "model_comparison.png"))
        
        logger.info(f"Evaluation report and plots generated in {output_path}")
        
        return report_path
    
    def load_and_evaluate_saved_models(self, models_dir: str, X_test: np.ndarray, 
                                     y_test: np.ndarray) -> Dict:
        """
        Load saved models and evaluate them
        """
        models_path = Path(models_dir)
        loaded_models = {}
        
        # Load all saved models
        for model_file in models_path.glob("**/*.pkl"):
            try:
                model_data = joblib.load(model_file)
                model_name = model_file.stem
                
                if isinstance(model_data, dict) and 'model' in model_data:
                    model = model_data['model']
                    label_encoder = model_data.get('label_encoder', None)
                else:
                    model = model_data
                    label_encoder = None
                
                loaded_models[model_name] = model
                
                # Evaluate the loaded model
                self.evaluate_model_comprehensive(model, X_test, y_test, model_name, label_encoder)
                
                logger.info(f"Loaded and evaluated model: {model_name}")
                
            except Exception as e:
                logger.error(f"Error loading model {model_file}: {e}")
        
        return loaded_models
    
    def real_time_performance_monitoring(self, model, X_stream: np.ndarray, 
                                       y_true_stream: np.ndarray, window_size: int = 100):
        """
        Monitor model performance in real-time scenarios
        """
        logger.info("Starting real-time performance monitoring...")
        
        performance_history = {
            'timestamps': [],
            'accuracy': [],
            'precision': [],
            'recall': [],
            'f1_score': []
        }
        
        for i in range(window_size, len(X_stream)):
            # Get window of data
            X_window = X_stream[i-window_size:i]
            y_window = y_true_stream[i-window_size:i]
            
            # Make predictions
            y_pred = model.predict(X_window)
            
            # Calculate metrics
            acc = accuracy_score(y_window, y_pred)
            prec = precision_score(y_window, y_pred, average='weighted', zero_division=0)
            rec = recall_score(y_window, y_pred, average='weighted', zero_division=0)
            f1 = f1_score(y_window, y_pred, average='weighted', zero_division=0)
            
            # Store results
            performance_history['timestamps'].append(i)
            performance_history['accuracy'].append(acc)
            performance_history['precision'].append(prec)
            performance_history['recall'].append(rec)
            performance_history['f1_score'].append(f1)
            
            # Log performance every 100 samples
            if i % 100 == 0:
                logger.info(f"Sample {i}: Accuracy={acc:.3f}, F1={f1:.3f}")
        
        # Plot performance over time
        plt.figure(figsize=(12, 8))
        
        plt.subplot(2, 2, 1)
        plt.plot(performance_history['timestamps'], performance_history['accuracy'])
        plt.title('Accuracy Over Time')
        plt.xlabel('Sample')
        plt.ylabel('Accuracy')
        
        plt.subplot(2, 2, 2)
        plt.plot(performance_history['timestamps'], performance_history['precision'])
        plt.title('Precision Over Time')
        plt.xlabel('Sample')
        plt.ylabel('Precision')
        
        plt.subplot(2, 2, 3)
        plt.plot(performance_history['timestamps'], performance_history['recall'])
        plt.title('Recall Over Time')
        plt.xlabel('Sample')
        plt.ylabel('Recall')
        
        plt.subplot(2, 2, 4)
        plt.plot(performance_history['timestamps'], performance_history['f1_score'])
        plt.title('F1-Score Over Time')
        plt.xlabel('Sample')
        plt.ylabel('F1-Score')
        
        plt.tight_layout()
        plt.show()
        
        return performance_history
