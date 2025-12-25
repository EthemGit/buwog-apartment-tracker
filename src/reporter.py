import pandas as pd
import matplotlib.pyplot as plt
import os
from pandas.plotting import table

"""Goal of this file is to improve insights what changed compared to last week.
This analysis answers two questions
    1) "Who left?" --> Which IDs changed from Available to Occupied
    2) "Who changed price?" --> Same ID, same status, but different Price. The goal is to differentiate between
            a) lower average price because an apartment was rented and
            b) project owner lowered/ increased price due to market forces

Tries to generate 2 images:
    Image 1(RENTED_since_..png). Overview over rented apartments since last week. No new rentings => empty table
    Image 2(PRICE_CHANGES_...png). Table only showing apartments that are still available => price changed because
        landlord changed it due to market forces. No price changes => no image. No image => no price changes.
"""

# --- CONFIGURATION ---
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
DATA_FILE = os.path.join(BASE_DIR, "data", "apartments_history.csv")
REPORT_DIR = os.path.join(BASE_DIR, "reports")

if not os.path.exists(REPORT_DIR):
    os.makedirs(REPORT_DIR)

def get_last_known_price(df, apartment_id):
    """
    Searches the entire history of an apartment to find the most recent valid price.
    """
    apt_history = df[df['Apartment_ID'] == apartment_id]
    valid_history = apt_history.dropna(subset=['Total_Rent'])
    
    if not valid_history.empty:
        price = valid_history.iloc[-1]['Total_Rent']
        return f"{price:.2f} €"
    else:
        return "Unknown"

def generate_report():
    if not os.path.exists(DATA_FILE):
        print("No data file found.")
        return

    df = pd.read_csv(DATA_FILE)
    df['Date_Checked'] = pd.to_datetime(df['Date_Checked'])
    
    dates = sorted(df['Date_Checked'].unique())
    if len(dates) < 2:
        print("Not enough history to generate a comparison report.")
        return

    curr_date = dates[-1]
    prev_date = dates[-2]
    
    print(f"Comparing {prev_date.date()} vs {curr_date.date()}...")

    curr_df = df[df['Date_Checked'] == curr_date].set_index('Apartment_ID')
    prev_df = df[df['Date_Checked'] == prev_date].set_index('Apartment_ID')

    # --- 1. FIND NEWLY RENTED APARTMENTS ---
    prev_available = prev_df[prev_df['Status'] == 'Available'].index
    
    just_rented = []
    for aid in prev_available:
        is_rented_now = False
        if aid in curr_df.index:
            if curr_df.loc[aid, 'Status'] == 'Occupied':
                is_rented_now = True
        elif aid not in curr_df.index:
            is_rented_now = True

        if is_rented_now:
            data = prev_df.loc[aid]
            price_str = get_last_known_price(df, aid)
            
            just_rented.append({
                'ID': aid,
                'Rooms': data['Rooms'],
                'Floor': data['Floor'],
                'Last Price': price_str,
                'Area': f"{data['Area_m2']} m²"
            })

    # --- 2. FIND PRICE CHANGES ---
    price_changes = []
    common_available = prev_df[prev_df['Status'] == 'Available'].index.intersection(curr_df[curr_df['Status'] == 'Available'].index)
    
    for aid in common_available:
        old_p = prev_df.loc[aid, 'Total_Rent']
        new_p = curr_df.loc[aid, 'Total_Rent']
        
        if pd.notna(old_p) and pd.notna(new_p):
            if abs(new_p - old_p) > 1.0: 
                diff = new_p - old_p
                price_changes.append({
                    'ID': aid,
                    'Rooms': curr_df.loc[aid, 'Rooms'],
                    'Old Price': f"{old_p:.2f} €",
                    'New Price': f"{new_p:.2f} €",
                    'Change': f"{diff:+.2f} €"
                })

    # --- 3. SAVE AS IMAGES ---
    save_table_image(just_rented, f"RENTED_since_{prev_date.date()}.png", "Apartments Rented Since Last Run")
    save_table_image(price_changes, f"PRICE_CHANGES_{curr_date.date()}.png", "Price Adjustments (Repricing)")

def save_table_image(data_list, filename, title):
    if not data_list:
        print(f"No data for: {title}")
        return

    df_viz = pd.DataFrame(data_list)
    
    # Calculate plot size
    plt.figure(figsize=(10, len(df_viz) * 0.5 + 1.5))
    ax = plt.subplot(111, frame_on=False) 
    ax.xaxis.set_visible(False) 
    ax.yaxis.set_visible(False) 
    
    # Use Matplotlib's native table function (Fixes the TypeError and removes index)
    tbl = ax.table(
        cellText=df_viz.values,
        colLabels=df_viz.columns,
        loc='center',
        cellLoc='center'
    )
    
    # Styling
    tbl.auto_set_font_size(False)
    tbl.set_fontsize(11)
    tbl.scale(1.2, 1.5) # Increase row height
    
    # Bold Headers and optional coloring
    for (row, col), cell in tbl.get_celld().items():
        if row == 0:
            cell.set_text_props(weight='bold')
            cell.set_facecolor('#f2f2f2') # Light gray header
    
    plt.title(title, fontsize=14, pad=10, weight='bold')
    plt.tight_layout()
    plt.savefig(os.path.join(REPORT_DIR, filename), bbox_inches='tight', dpi=150)
    plt.close()
    print(f"Saved report: {filename}")

if __name__ == "__main__":
    generate_report()