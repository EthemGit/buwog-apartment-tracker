import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
from datetime import datetime

# --- CONFIGURATION ---
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
DATA_FILE = os.path.join(BASE_DIR, "data", "apartments_history.csv")
PLOT_DIR = os.path.join(BASE_DIR, "plots")

# TRAFFIC LIGHT PALETTE
COLORS = {
    'Available': '#2ecc71', # Green
    'Reserved':  '#f39c12', # Orange
    'Occupied':  '#e74c3c'  # Red
}

def generate_plots():
    if not os.path.exists(DATA_FILE):
        print("No data file found. Run scraper.py first.")
        return

    df = pd.read_csv(DATA_FILE)
    df['Date_Checked'] = pd.to_datetime(df['Date_Checked'])
    
    if not os.path.exists(PLOT_DIR):
        os.makedirs(PLOT_DIR)

    sns.set_theme(style="whitegrid")
    
    # --- PLOT 1: Occupancy Trend (Three Lines) ---
    plt.figure(figsize=(10, 6))
    
    occupancy = df.groupby(['Date_Checked', 'Status']).size().unstack(fill_value=0)
    
    # Plot each status if it exists in the data
    for status, color in COLORS.items():
        if status in occupancy.columns:
            sns.lineplot(data=occupancy, x=occupancy.index, y=status, 
                         marker='o', label=f'{status} Units', color=color, linewidth=2.5)
        
    plt.title('Apartment Status Over Time', fontsize=14)
    plt.ylabel('Number of Apartments')
    plt.xlabel('')
    plt.xticks(rotation=45)
    plt.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(PLOT_DIR, f"occupancy_trend_{datetime.now().date()}.png"))
    print("Saved Occupancy Plot.")

    # --- PLOT 2: Price Swarm Plot (Only Available Units) ---
    # We exclude Reserved because they usually have no price
    latest_date = df['Date_Checked'].max()
    available_df = df[(df['Status'] == 'Available') & (df['Date_Checked'] == latest_date)]
    
    if not available_df.empty:
        plt.figure(figsize=(10, 6))
        sns.swarmplot(data=available_df, x='Rooms', y='Total_Rent', hue='Floor', size=7, palette='viridis')
        plt.title(f'Current Rent Prices (Available Units as of {latest_date.date()})', fontsize=14)
        plt.ylabel('Total Rent (€)')
        plt.xlabel('Number of Rooms')
        plt.legend(title='Floor', bbox_to_anchor=(1.05, 1), loc='upper left')
        plt.tight_layout()
        plt.savefig(os.path.join(PLOT_DIR, f"rent_distribution_{datetime.now().date()}.png"))
        print("Saved Price Distribution Plot.")

    # --- PLOT 3: Total Count Bar Chart (Stacked or Grouped) ---
    latest_df = df[df['Date_Checked'] == latest_date]
    
    if not latest_df.empty:
        plt.figure(figsize=(12, 7))
        
        # Countplot automatically handles the hue for us
        ax = sns.countplot(data=latest_df, x='Rooms', hue='Status', palette=COLORS)
        
        plt.title(f'Total Apartments by Room Count (As of {latest_date.date()})', fontsize=14)
        plt.ylabel('Count')
        
        # Add summary text box
        summary_text = f"Status Summary ({latest_date.date()}):\n"
        counts = latest_df['Status'].value_counts()
        for status in ['Available', 'Reserved', 'Occupied']:
            count = counts.get(status, 0)
            summary_text += f"{status}: {count}\n"

        plt.text(0.02, 0.95, summary_text, transform=plt.gca().transAxes, 
                 fontsize=11, verticalalignment='top', 
                 bbox=dict(boxstyle='round', facecolor='white', alpha=0.9))

        plt.tight_layout()
        plt.savefig(os.path.join(PLOT_DIR, f"room_counts_{datetime.now().date()}.png"))
        print("Saved Room Count Plot.")

    # --- PLOT 4: Average Rent Evolution Over Time (RESTORED) ---
    # Filter only available apartments
    history_available = df[df['Status'] == 'Available']

    if not history_available.empty:
        plt.figure(figsize=(10, 6))
        
        # Calculate average rent per date and room count
        avg_rent_history = history_available.groupby(['Date_Checked', 'Rooms'])['Total_Rent'].mean().reset_index()
        
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