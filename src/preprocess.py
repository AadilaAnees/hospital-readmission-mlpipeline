import pandas as pd
import numpy as np

def map_icd9_to_category(code):
    if pd.isna(code) or str(code).strip() == '?' or str(code).strip() == '':
        return 'Other'
    code_str = str(code).strip()
    if code_str.startswith('250'):
        return 'Diabetes'
    if not code_str[0].isdigit():
        return 'Other'
    try:
        prefix = int(float(code_str.split('.')[0]))
    except ValueError:
        return 'Other'
        
    if 390 <= prefix <= 459 or prefix == 785:
        return 'Circulatory'
    elif 460 <= prefix <= 519 or prefix == 786:
        return 'Respiratory'
    elif 520 <= prefix <= 579 or prefix == 787:
        return 'Digestive'
    elif 140 <= prefix <= 239:
        return 'Neoplasms'
    elif 580 <= prefix <= 629 or prefix == 788:
        return 'Genitourinary'
    elif 710 <= prefix <= 739:
        return 'Musculoskeletal'
    elif 800 <= prefix <= 999:
        return 'Injury'
    else:
        return 'Other'

def clean_data(raw_df):
    df_clean = raw_df.copy()
    
    # 1. Replace all '?' with NaN
    df_clean = df_clean.replace('?', np.nan)
    
    # 2. Create the binary target column (<30 = 1, else = 0)
    df_clean['target'] = (df_clean['readmitted'] == '<30').astype(int)
    
    # 3. Handle patient deduplication safely
    df_clean = df_clean.drop_duplicates(subset='patient_nbr', keep='first')
    
    # 4. Filter out hospice/expired rows
    hospice_expired_ids = [11, 13, 14, 19, 20, 21, 28]
    df_clean = df_clean[~df_clean['discharge_disposition_id'].isin(hospice_expired_ids)]
    
    # 5. Drop unnecessary columns entirely
    cols_to_drop = ['encounter_id', 'patient_nbr', 'examide', 'citoglipton', 'weight', 'payer_code', 'readmitted']
    df_clean = df_clean.drop(columns=[c for c in cols_to_drop if c in df_clean.columns])
    
    # 6. Cap num_medications at 60
    df_clean['num_medications'] = df_clean['num_medications'].clip(upper=60)
    
    # 7. Map medical_specialty NaN to "Unknown"
    df_clean['medical_specialty'] = df_clean['medical_specialty'].fillna('Unknown')
    
    # 8. Engineer ICD-9 buckets
    df_clean['diag_1_clean'] = df_clean['diag_1'].apply(map_icd9_to_category)
    df_clean['diag_2_clean'] = df_clean['diag_2'].apply(map_icd9_to_category)
    df_clean['diag_3_clean'] = df_clean['diag_3'].apply(map_icd9_to_category)
    df_clean = df_clean.drop(columns=['diag_1', 'diag_2', 'diag_3'])
    
    # 9. Engineer total_prior_visits
    df_clean['total_prior_visits'] = (
        df_clean['number_inpatient'] + 
        df_clean['number_emergency'] + 
        df_clean['number_outpatient']
    )
    
    return df_clean

