import pandas as pd
import requests
from io import StringIO
from datetime import datetime
import os

# --- CONFIGURATION ---
URL = "https://eutighofer-tor.buwog.com/"
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
CSV_FILE = os.path.join(DATA_DIR, "apartments_history.csv")

def clean_currency(value):
    """Converts string currency (1.200,00 €) to float (1200.00)."""
    if pd.isna(value) or isinstance(value, (int, float)):
        return value
    clean_str = str(value).replace('€', '').replace('.', '').replace(',', '.').strip()
    try:
        return float(clean_str)
    except ValueError:
        return None

def fetch_data():
    """Fetches data from the website and returns a DataFrame."""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    print(f"[{datetime.now()}] Fetching data from {URL}...")
    try:
        response = requests.get(URL, headers=headers)
        response.raise_for_status()
        
        # Parse tables
        tables = pd.read_html(StringIO(response.text), decimal=',', thousands='.')
        if not tables:
            print("No tables found.")
            return None
            
        # Combine all room categories
        df = pd.concat(tables, ignore_index=True)
        return df
        
    except Exception as e:
        print(f"Error fetching data: {e}")
        return None

def process_data(df):
    """Cleans and adds timestamp to the data."""
    # Add Timestamp
    df['Date_Checked'] = datetime.now().strftime("%Y-%m-%d")
    
    # Determine Status
    df['Status'] = df['Gesamtmiete'].apply(lambda x: 'Occupied' if 'vermietet' in str(x).lower() else 'Available')
    
    # Clean Numerical Columns
    df['Grundmiete_Num'] = df['Grundmiete'].apply(clean_currency)
    df['Gesamtmiete_Num'] = df['Gesamtmiete'].apply(clean_currency)
    df['Area_m2'] = df['ca. Fläche'].astype(str).str.replace(' m2', '').str.replace(',', '.').astype(float)
    
    # Select and rename columns for clarity
    cols = ['Date_Checked', 'Whg.-Nr.', 'Zi.', 'Area_m2', 'Etage', 'Status', 'Grundmiete_Num', 'Gesamtmiete_Num']
    final_df = df[cols].rename(columns={
        'Whg.-Nr.': 'Apartment_ID',
        'Zi.': 'Rooms',
        'Etage': 'Floor',
        'Grundmiete_Num': 'Base_Rent',
        'Gesamtmiete_Num': 'Total_Rent'
    })
    
    return final_df

def save_data(new_data):
    """Appends new data to the CSV file."""
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
        
    # Check if file exists to handle headers
    header = not os.path.exists(CSV_FILE)
    
    new_data.to_csv(CSV_FILE, mode='a', header=header, index=False)
    print(f"Success! Appended {len(new_data)} rows to {CSV_FILE}")

if __name__ == "__main__":
    df_raw = fetch_data()
    if df_raw is not None:
        df_clean = process_data(df_raw)
        save_data(df_clean)
        