import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
from datetime import datetime

# --- CONFIGURATION ---
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
DATA_FILE = os.path.join(BASE_DIR, "data", "apartments_history.csv")
PLOT_DIR = os.path.join(BASE_DIR, "plots")

def generate_plots():
    if not os.path.exists(DATA_FILE):
        print("No data file found. Run scraper.py first.")
        return

    # Load Data
    df = pd.read_csv(DATA_FILE)
    df['Date_Checked'] = pd.to_datetime(df['Date_Checked'])
    
    # Ensure Plot Directory Exists
    if not os.path.exists(PLOT_DIR):
        os.makedirs(PLOT_DIR)

    # Set Style
    sns.set_theme(style="whitegrid")
    
    # --- PLOT 1: Occupancy Over Time ---
    plt.figure(figsize=(10, 6))
    
    # Group by Date and Status
    occupancy = df.groupby(['Date_Checked', 'Status']).size().unstack(fill_value=0)
    
    if 'Available' in occupancy.columns:
        sns.lineplot(data=occupancy, x=occupancy.index, y='Available', marker='o', label='Available Units', color='green')
    if 'Occupied' in occupancy.columns:
        sns.lineplot(data=occupancy, x=occupancy.index, y='Occupied', marker='o', label='Rented Units', color='red')
        
    plt.title('Apartment Availability Over Time')
    plt.ylabel('Number of Apartments')
    plt.xlabel('Date')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(os.path.join(PLOT_DIR, f"occupancy_trend_{datetime.now().date()}.png"))
    print("Saved Occupancy Plot.")

    # --- PLOT 2: Price Distribution (Available Units) ---
    # Only useful if we have available units
    available_df = df[df['Status'] == 'Available']
    
    if not available_df.empty:
        plt.figure(figsize=(10, 6))
        sns.boxplot(data=available_df, x='Rooms', y='Total_Rent')
        plt.title('Rent Price Distribution by Room Count')
        plt.ylabel('Total Rent (€)')
        plt.savefig(os.path.join(PLOT_DIR, f"rent_distribution_{datetime.now().date()}.png"))
        print("Saved Price Distribution Plot.")
    
    plt.close('all')

if __name__ == "__main__":
    generate_plots()
    