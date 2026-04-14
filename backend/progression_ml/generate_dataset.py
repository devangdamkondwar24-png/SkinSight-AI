import pandas as pd
import numpy as np
import os

# Set seed for reproducibility
np.random.seed(42)

NUM_SAMPLES = 10500

def generate_dataset():
    """Generates a synthetic longitudinal dataset for skin condition progression."""
    
    # 1. Base Features (Current State)
    # Age: Normal distribution around 25, clamped to 15-60
    age = np.clip(np.random.normal(25, 8, NUM_SAMPLES), 15, 60).astype(int)
    
    # Skin Type: Categorical
    skin_types = ['Dry', 'Oily', 'Combination', 'Normal', 'Sensitive']
    skin_type = np.random.choice(skin_types, NUM_SAMPLES, p=[0.2, 0.3, 0.3, 0.1, 0.1])
    
    # Current Severity: Mild (40%), Moderate (40%), Severe (20%)
    current_severity = np.random.choice(['Mild', 'Moderate', 'Severe'], NUM_SAMPLES, p=[0.4, 0.4, 0.2])
    
    # Current Lesion Count depending on severity
    current_lesion_count = np.zeros(NUM_SAMPLES, dtype=int)
    for i in range(NUM_SAMPLES):
        if current_severity[i] == 'Mild':
            current_lesion_count[i] = int(np.clip(np.random.normal(5, 3), 1, 12))
        elif current_severity[i] == 'Moderate':
            current_lesion_count[i] = int(np.clip(np.random.normal(18, 5), 13, 30))
        else: # Severe
            current_lesion_count[i] = int(np.clip(np.random.normal(45, 15), 31, 80))
            
    # Pigmentation Percentage (overall surface redness/spots)
    pigmentation_percentage = np.clip(np.random.normal(current_lesion_count * 0.8 + 10, 10), 0, 100).astype(float)
    
    # Zone Distribution (highest severity zone)
    zones = ['forehead', 'cheeks', 'chin', 'nose']
    primary_zone = np.random.choice(zones, NUM_SAMPLES, p=[0.2, 0.4, 0.3, 0.1])

    # 2. Progression Simulation (Probabilistic Logic, NOT hardcoded fixed rules)
    # Target variables representing "Short Term (2-4 weeks)" and "Long Term (8-12 weeks)"
    
    short_term_lesion_count = np.zeros(NUM_SAMPLES, dtype=int)
    long_term_lesion_count = np.zeros(NUM_SAMPLES, dtype=int)
    
    short_term_severity = np.empty(NUM_SAMPLES, dtype=object)
    long_term_severity = np.empty(NUM_SAMPLES, dtype=object)

    for i in range(NUM_SAMPLES):
        # Base recovery factors (introducing randomness)
        # Younger age slightly correlates with faster recovery
        age_factor = max(0.8, min(1.2, age[i] / 30.0)) 
        
        # Skin type recovery factors (Sensitive/Oily might have slightly higher variance)
        st_factor = 1.0
        if skin_type[i] == 'Sensitive': st_factor = 1.1
        if skin_type[i] == 'Normal': st_factor = 0.9
        
        # Short Term Improvement: usually drops by 30-60%, with gaussian noise
        st_improvement_rate = np.clip(np.random.normal(0.45, 0.15), 0.1, 0.8)
        # Apply factors
        st_actual_rate = np.clip(st_improvement_rate * age_factor * st_factor, 0.1, 0.9)
        
        st_lesions = current_lesion_count[i] * (1 - st_actual_rate)
        # Add random noise +/- 2 lesions
        st_lesions = np.clip(st_lesions + np.random.normal(0, 2), 0, 100)
        short_term_lesion_count[i] = int(round(st_lesions))
        
        # Long Term Improvement: usually drops by 80-100% from current
        lt_improvement_rate = np.clip(np.random.normal(0.90, 0.10), 0.5, 1.0)
        lt_actual_rate = np.clip(lt_improvement_rate * age_factor * st_factor, 0.4, 1.0)
        
        lt_lesions = current_lesion_count[i] * (1 - lt_actual_rate)
        lt_lesions = np.clip(lt_lesions + np.random.normal(0, 1.5), 0, 100)
        long_term_lesion_count[i] = int(round(lt_lesions))

        # Assign Severity based on count to create consistency, but with some border overlap noise
        def map_severity(count):
            noisy_count = count + np.random.normal(0, 1.5)
            if noisy_count <= 2: return 'Clear'
            elif noisy_count <= 12: return 'Mild'
            elif noisy_count <= 30: return 'Moderate'
            else: return 'Severe'
            
        short_term_severity[i] = map_severity(short_term_lesion_count[i])
        long_term_severity[i] = map_severity(long_term_lesion_count[i])

    # 3. Create DataFrame
    df = pd.DataFrame({
        'age': age,
        'skin_type': skin_type,
        'current_severity': current_severity,
        'current_lesion_count': current_lesion_count,
        'pigmentation_percentage': pigmentation_percentage,
        'primary_zone': primary_zone,
        'short_term_lesion_count': short_term_lesion_count,
        'short_term_severity': short_term_severity,
        'long_term_lesion_count': long_term_lesion_count,
        'long_term_severity': long_term_severity
    })
    
    # Save to CSV
    os.makedirs(os.path.dirname(os.path.abspath(__file__)), exist_ok=True)
    csv_path = os.path.join(os.path.dirname(__file__), 'progression_dataset.csv')
    df.to_csv(csv_path, index=False)
    print(f"[SUCCESS] Generated synthetic dataset with {len(df)} samples at {csv_path}")
    print(df.head())

if __name__ == "__main__":
    generate_dataset()
