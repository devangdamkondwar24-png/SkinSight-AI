import os
import joblib
import numpy as np
import pandas as pd

class ProgressionService:
    def __init__(self):
        self.models_dir = os.path.join(os.path.dirname(__file__), '..', 'progression_ml', 'models')
        self._load_artifacts()

    def _load_artifacts(self):
        """Load all pre-trained models and encoders."""
        try:
            self.scaler = joblib.load(os.path.join(self.models_dir, 'scaler.pkl'))
            self.le_skin_type = joblib.load(os.path.join(self.models_dir, 'le_skin_type.pkl'))
            self.le_severity = joblib.load(os.path.join(self.models_dir, 'le_severity.pkl'))
            self.le_zone = joblib.load(os.path.join(self.models_dir, 'le_zone.pkl'))

            self.st_regressor = joblib.load(os.path.join(self.models_dir, 'short_term_regressor.pkl'))
            self.st_classifier = joblib.load(os.path.join(self.models_dir, 'short_term_classifier.pkl'))
            self.lt_regressor = joblib.load(os.path.join(self.models_dir, 'long_term_regressor.pkl'))
            self.lt_classifier = joblib.load(os.path.join(self.models_dir, 'long_term_classifier.pkl'))
            self.is_loaded = True
        except Exception as e:
            print(f"Error loading ML models: {e}")
            self.is_loaded = False

    def predict(self, lesion_count: int, severity: str, pigmentation: float, age: int, skin_type: str, primary_zone: str = 'cheeks') -> dict:
        """
        Uses trained ML models to predict future skin conditions.
        No hardcoded logic allows the model weights to dictate the progression entirely.
        """
        if not self.is_loaded:
            return {
                "error": "ML models not loaded. Please run train_models.py first."
            }
            
        try:
            # 1. Prepare Input Features
            # Handle unknown labels gracefully if needed, but assuming standard inputs
            
            # encode string values
            try:
                skin_enc = self.le_skin_type.transform([skin_type])[0]
            except ValueError:
                # Default to Normal if unseen
                skin_enc = self.le_skin_type.transform(['Normal'])[0]
                
            try:    
                sev_enc = self.le_severity.transform([severity])[0]
            except ValueError:
                sev_enc = self.le_severity.transform(['Mild'])[0]
                
            try:    
                zone_enc = self.le_zone.transform([primary_zone])[0]
            except ValueError:
                zone_enc = self.le_zone.transform(['cheeks'])[0]
                
            # Feature order must precisely match training script:
            # ['age', 'skin_type_encoded', 'current_severity_encoded', 'current_lesion_count', 'pigmentation_percentage', 'primary_zone_encoded']
            features = pd.DataFrame([[
                age,
                skin_enc,
                sev_enc,
                lesion_count,
                pigmentation,
                zone_enc
            ]], columns=[
                'age', 'skin_type_encoded', 'current_severity_encoded', 
                'current_lesion_count', 'pigmentation_percentage', 'primary_zone_encoded'
            ])
            
            # Scale features
            features_scaled = self.scaler.transform(features)
            
            # 2. Inference
            st_lesion_pred = int(round(self.st_regressor.predict(features_scaled)[0]))
            st_sev_pred = self.st_classifier.predict(features_scaled)[0]
            
            lt_lesion_pred = int(round(self.lt_regressor.predict(features_scaled)[0]))
            lt_sev_pred = self.lt_classifier.predict(features_scaled)[0]
            
            # Ensure predictions don't mathematically fall below 0
            st_lesion_pred = max(0, st_lesion_pred)
            lt_lesion_pred = max(0, lt_lesion_pred)
            
            return {
                "short_term": {
                    "lesion_count_prediction": st_lesion_pred,
                    "severity_prediction": st_sev_pred
                },
                "long_term": {
                    "lesion_count_prediction": lt_lesion_pred,
                    "severity_prediction": lt_sev_pred
                }
            }
            
        except Exception as e:
            return {"error": str(e)}

# Singleton instance for FastAPI dependency injection
progression_service = ProgressionService()
