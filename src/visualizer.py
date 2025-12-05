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

    # Set Global Style
    sns.set_theme(style="whitegrid")
    
    # --- PLOT 1: Occupancy Over Time ---
    plt.figure(figsize=(10, 6))
    
    # Group by Date and Status
    occupancy = df.groupby(['Date_Checked', 'Status']).size().unstack(fill_value=0)
    
    if 'Available' in occupancy.columns:
        sns.lineplot(data=occupancy, x=occupancy.index, y='Available', marker='o', label='Available Units', color='#2ecc71', linewidth=2.5)
    if 'Occupied' in occupancy.columns:
        sns.lineplot(data=occupancy, x=occupancy.index, y='Occupied', marker='o', label='Rented Units', color='#e74c3c', linewidth=2.5)
        
    plt.title('Apartment Availability Over Time', fontsize=14)
    plt.ylabel('Number of Apartments')
    plt.xlabel('') # Date is obvious, empty label is cleaner
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(os.path.join(PLOT_DIR, f"occupancy_trend_{datetime.now().date()}.png"))
    print("Saved Occupancy Plot.")

    # --- PLOT 2: Price Distribution (Swarm Plot) ---
    # Only useful if we have available units
    available_df = df[df['Status'] == 'Available']
    
    if not available_df.empty:
        plt.figure(figsize=(10, 6))
        
        # Swarmplot: Draws a dot for every apartment.
        # hue='Floor': Colors the dots based on which floor they are on.
        sns.swarmplot(
            data=available_df, 
            x='Rooms', 
            y='Total_Rent', 
            hue='Floor',      # Color coded by floor
            size=7,           # Size of the dots
            palette='viridis' # Color scheme
        )
        
        plt.title('Current Rent Prices (Every Dot is an Apartment)', fontsize=14)
        plt.ylabel('Total Rent (€)')
        plt.xlabel('Number of Rooms')
        
        # Move the legend outside the plot so it doesn't cover dots
        plt.legend(title='Floor', bbox_to_anchor=(1.05, 1), loc='upper left')
        
        plt.tight_layout()
        plt.savefig(os.path.join(PLOT_DIR, f"rent_distribution_{datetime.now().date()}.png"))
        print("Saved Price Distribution Plot.")
    
    # --- PLOT 3: Total Count by Room Number (Available vs Occupied) ---
    plt.figure(figsize=(10, 6))
    sns.countplot(data=df, x='Rooms', hue='Status', palette={'Available': '#2ecc71', 'Occupied': '#e74c3c'})
    plt.title('Total Number of Apartments by Room Count')
    plt.ylabel('Count')
    plt.savefig(os.path.join(PLOT_DIR, f"room_counts_{datetime.now().date()}.png"))
    print("Saved Room Count Plot.")

    # --- PLOT 4: Average Rent Evolution Over Time ---
    # Filter only available apartments
    available_df = df[df['Status'] == 'Available']

    if not available_df.empty:
        plt.figure(figsize=(10, 6))
        
        # Calculate average rent per date and room count
        # reset_index() flattens the table so seaborn can use it easily
        avg_rent_history = available_df.groupby(['Date_Checked', 'Rooms'])['Total_Rent'].mean().reset_index()
        
        # Plot lines
        # hue='Rooms' creates a separate colored line for 2 Zimmer, 3 Zimmer, etc.
        sns.lineplot(
            data=avg_rent_history, 
            x='Date_Checked', 
            y='Total_Rent', 
            hue='Rooms', 
            marker='o', 
            palette='tab10',
            linewidth=2.5
        )
        
        plt.title('Average Rent Price Evolution')
        plt.ylabel('Average Total Rent (€)')
        plt.xlabel('Date')
        plt.legend(title='Room Count')
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        plt.savefig(os.path.join(PLOT_DIR, f"avg_rent_history_{datetime.now().date()}.png"))
        print("Saved Average Rent History Plot.")

    plt.close('all')

if __name__ == "__main__":
    generate_plots()
