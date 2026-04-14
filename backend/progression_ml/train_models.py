import pandas as pd
import numpy as np
import os
import joblib
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.metrics import mean_absolute_error, accuracy_score, classification_report

def train_and_save_models():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    dataset_path = os.path.join(base_dir, 'progression_dataset.csv')
    models_dir = os.path.join(base_dir, 'models')
    
    if not os.path.exists(dataset_path):
        print(f"[ERROR] Dataset not found at {dataset_path}. Run generate_dataset.py first.")
        return

    os.makedirs(models_dir, exist_ok=True)
    
    print("[INFO] Loading dataset...")
    df = pd.read_csv(dataset_path)
    
    # 1. Preprocessing
    print("[INFO] Preprocessing data...")
    # Encode categorical features
    le_skin_type = LabelEncoder()
    df['skin_type_encoded'] = le_skin_type.fit_transform(df['skin_type'])
    
    le_severity = LabelEncoder()
    # Ensure consistent ordering for severity encoding if needed, though LabelEncoder is alphabetical
    # Let's map it manually to ensure ordinality makes sense if we ever need it, but for RandomForest nominal is fine.
    # However we are using an encoder for inputs.
    severity_order = ['Clear', 'Mild', 'Moderate', 'Severe']
    le_severity.fit(severity_order)
    df['current_severity_encoded'] = le_severity.transform(df['current_severity'])
    
    le_zone = LabelEncoder()
    df['primary_zone_encoded'] = le_zone.fit_transform(df['primary_zone'])

    # 2. Define Features (X)
    feature_cols = [
        'age', 
        'skin_type_encoded', 
        'current_severity_encoded', 
        'current_lesion_count', 
        'pigmentation_percentage', 
        'primary_zone_encoded'
    ]
    X = df[feature_cols]
    
    # Scale numerical features (important for general practice, though less critical for trees)
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    # 3. Define Targets (y)
    y_st_lesions = df['short_term_lesion_count']
    y_st_severity = df['short_term_severity']
    y_lt_lesions = df['long_term_lesion_count']
    y_lt_severity = df['long_term_severity']
    
    # 4. Train-Test Split (Targeting Short-Term Lesions just to get consistent indices)
    X_train, X_test, indices_train, indices_test = train_test_split(
        X_scaled, np.arange(len(df)), test_size=0.2, random_state=42
    )

    print("[INFO] Training Short-Term Models...")
    # -- Short Term Models --
    st_regressor = RandomForestRegressor(n_estimators=100, random_state=42, n_jobs=-1)
    st_regressor.fit(X_train, y_st_lesions.iloc[indices_train])
    
    st_classifier = RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1)
    st_classifier.fit(X_train, y_st_severity.iloc[indices_train])
    
    print("[INFO] Training Long-Term Models...")
    # -- Long Term Models --
    lt_regressor = RandomForestRegressor(n_estimators=100, random_state=42, n_jobs=-1)
    lt_regressor.fit(X_train, y_lt_lesions.iloc[indices_train])
    
    lt_classifier = RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1)
    lt_classifier.fit(X_train, y_lt_severity.iloc[indices_train])
    
    # 5. Evaluation
    print("========================================")
    print("MODEL EVALUATION RESULTS")
    print("========================================")
    
    # Eval Short Term
    st_lesion_preds = st_regressor.predict(X_test)
    st_mae = mean_absolute_error(y_st_lesions.iloc[indices_test], st_lesion_preds)
    print(f"Short-Term Lesion Count (Regressor) MAE: {st_mae:.2f}")
    
    st_sev_preds = st_classifier.predict(X_test)
    st_acc = accuracy_score(y_st_severity.iloc[indices_test], st_sev_preds)
    print(f"Short-Term Severity (Classifier) Accuracy: {st_acc:.2%}")
    
    # Eval Long Term
    lt_lesion_preds = lt_regressor.predict(X_test)
    lt_mae = mean_absolute_error(y_lt_lesions.iloc[indices_test], lt_lesion_preds)
    print(f"Long-Term Lesion Count (Regressor) MAE:   {lt_mae:.2f}")
    
    lt_sev_preds = lt_classifier.predict(X_test)
    lt_acc = accuracy_score(y_lt_severity.iloc[indices_test], lt_sev_preds)
    print(f"Long-Term Severity (Classifier) Accuracy:  {lt_acc:.2%}")
    print("========================================")
    
    # 6. Save Artifacts for FastAPI
    print("[INFO] Saving models and encoders...")
    
    # Save Encoders and Scaler
    joblib.dump(le_skin_type, os.path.join(models_dir, 'le_skin_type.pkl'))
    joblib.dump(le_severity, os.path.join(models_dir, 'le_severity.pkl'))
    joblib.dump(le_zone, os.path.join(models_dir, 'le_zone.pkl'))
    joblib.dump(scaler, os.path.join(models_dir, 'scaler.pkl'))
    
    # Save Models
    joblib.dump(st_regressor, os.path.join(models_dir, 'short_term_regressor.pkl'))
    joblib.dump(st_classifier, os.path.join(models_dir, 'short_term_classifier.pkl'))
    joblib.dump(lt_regressor, os.path.join(models_dir, 'long_term_regressor.pkl'))
    joblib.dump(lt_classifier, os.path.join(models_dir, 'long_term_classifier.pkl'))
    
    print("[SUCCESS] All models saved to backend/progression_ml/models/")

if __name__ == "__main__":
    train_and_save_models()
