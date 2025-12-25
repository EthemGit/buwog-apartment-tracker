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
    # Only show *most recent* available apartments in the dot plot. Otherwise after 10 weeks the swarm plot will sho
    # 10 dots for the same apartment. Only applies to "Status" charts (Swarm/Box-plot) because in the "Trend" charts
    # we want explicitly to use all history.
    latest_date = df['Date_Checked'].max() 
    available_df = df[(df['Status'] == 'Available') & (df['Date_Checked'] == latest_date)]
    
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
    
    # --- PLOT 3: Total Count by Room Number (With Delta Annotations) ---
    # Get the two most recent dates
    sorted_dates = sorted(df['Date_Checked'].unique())
    
    if len(sorted_dates) >= 1:
        latest_date = sorted_dates[-1]
        
        # Filter for latest data
        latest_df = df[df['Date_Checked'] == latest_date]
        
        plt.figure(figsize=(12, 7))
        ax = sns.countplot(data=latest_df, x='Rooms', hue='Status', 
                           palette={'Available': '#2ecc71', 'Occupied': '#e74c3c'})
        
        plt.title(f'Total Apartments by Room Count (As of {latest_date.date()})', fontsize=14)
        plt.ylabel('Count')
        
        # --- LOGIC FOR DELTA (+2/-1) ANNOTATION ---
        if len(sorted_dates) >= 2:
            prev_date = sorted_dates[-2]
            prev_df = df[df['Date_Checked'] == prev_date]
            
            # Calculate counts for current and previous
            curr_counts = latest_df.groupby(['Rooms', 'Status']).size()
            prev_counts = prev_df.groupby(['Rooms', 'Status']).size()
            
            # Iterate over the bars to add text
            for p in ax.patches:
                # We need to guess which category (Rooms/Status) this bar belongs to based on geometry
                # This is tricky in Seaborn, but we can do a coordinate match or simpler:
                # Just calculate the differences and print them as a subtitle or legend for clarity.
                pass
            
            # A cleaner way than hacking bar coordinates: 
            # Print a text summary box on the chart
            summary_text = "Changes since last run:\n"
            
            # Check 2, 3, 4 rooms
            for r in sorted(latest_df['Rooms'].unique()):
                for s in ['Available', 'Occupied']:
                    try:
                        c = curr_counts.get((r, s), 0)
                        p = prev_counts.get((r, s), 0)
                        diff = c - p
                        if diff != 0:
                            sign = "+" if diff > 0 else ""
                            summary_text += f"{r} Rooms ({s}): {c} ({sign}{diff})\n"
                    except:
                        pass
            
            # Add text box to the plot
            plt.text(0.02, 0.95, summary_text, transform=plt.gca().transAxes, 
                     fontsize=10, verticalalignment='top', 
                     bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))

        plt.tight_layout()
        plt.savefig(os.path.join(PLOT_DIR, f"room_counts_delta_{datetime.now().date()}.png"))
        print("Saved Room Count Delta Plot.")

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
