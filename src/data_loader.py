import kagglehub
import pandas as pd
import os
import shutil

def download_and_load_data(config):
    """
    Download dataset using kagglehub and load the CSV file into a pandas DataFrame.
    """
    # Download latest version
    print("Downloading dataset from Kaggle...")
    path = kagglehub.dataset_download("alitaqishah/blood-cell-anomaly-detection-2025")
    print(f"Path to downloaded dataset files: {path}")
    
    # The expected file name based on user feedback
    expected_filename = "blood_cell_anomaly_detection.csv"
    downloaded_csv_path = os.path.join(path, expected_filename)
    
    # Expected output path from config
    raw_data_dir = os.path.dirname(config['data']['input']['path'])
    os.makedirs(raw_data_dir, exist_ok=True)
    
    target_csv_path = config['data']['input']['path']
    
    if os.path.exists(downloaded_csv_path):
        print(f"Copying {downloaded_csv_path} to {target_csv_path}")
        shutil.copy2(downloaded_csv_path, target_csv_path)
    else:
        # If the filename is different, try to find a CSV
        csv_files = [f for f in os.listdir(path) if f.endswith('.csv')]
        if csv_files:
            found_csv = os.path.join(path, csv_files[0])
            print(f"Expected {expected_filename} not found. Found {csv_files[0]}. Copying to {target_csv_path}")
            shutil.copy2(found_csv, target_csv_path)
        else:
            raise FileNotFoundError(f"No CSV file found in downloaded dataset path: {path}")
            
    print(f"Loading data from {target_csv_path}...")
    df = pd.read_csv(target_csv_path)
    print(f"Data loaded successfully. Shape: {df.shape}")
    
    return df
