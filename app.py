import streamlit as st
import pandas as pd
import os
from datetime import datetime
import plotly.express as px

# Set page config
st.set_page_config(page_title="Salon Polish Tracker", layout="wide")

# --- CLEAN THEME (No code leaks!) ---
st.markdown("""
    <style>
    html, body, [class*="css"], p, div, label {
        font-size: 0.95rem !important;
        color: #5D544C !important;
        font-family: sans-serif;
    }
    .stApp {
        background-color: #F3ECE1 !important;
        padding: 10px !important;
    }
    input, textarea, select {
        padding: 5px !important;
        border: 1px solid #D1C2A5 !important;
        border-radius: 4px !important;
        background-color: #FFFFFF !important;
    }
    .stButton>button {
        background-color: #E2A765 !important;
        color: #FFFFFF !important;
        border-radius: 4px !important;
        padding: 5px 10px !important;
    }
    [data-testid="stExpander"] {
        background-color: #FFFFFF !important;
        border: 1px solid #E5A398 !important;
    }
    h1 { color: #D97466 !important; text-align: center; }
    h2 { color: #E5A398 !important; }
    </style>
    """, unsafe_allow_html=True)

st.title("💅 Salon Nail Polish Tracker")

# --- DATABASE SETUP ---
for file, cols in {
    "gel_inventory.csv": ["Polish Name", "Uses", "Quantity", "Fluid Level"],
    "regular_inventory.csv": ["Polish Name", "Uses", "Quantity", "Fluid Level"],
    "client_history.csv": ["Date", "Client Name", "Polish Type", "Polish Name", "Notes"]
}.items():
    if not os.path.exists(file):
        pd.DataFrame(columns=cols).to_csv(file, index=False)

def load_data(file):
    df = pd.read_csv(file)
    if "Fluid Level" not in df.columns and file != "client_history.csv":
        df["Fluid Level"] = "Full"
    return df

def save_data(df, file):
    if "Polish Name" in df.columns:
        df = df.sort_values(by="Polish Name")
    df.to_csv(file, index=False)

# --- APP TABS ---
tab1, tab2, tab3, tab4 = st.tabs(["✨ Gel Polish", "🎨 Regular Polish", "👥 Client Notes", "📈 Analytics"])

# --- POLISH TAB DESIGN ---
def render_polish_tab(inventory_file, polish_type_label):
    df = load_data(inventory_file)
    if not df.empty:
        df = df.sort_values(by="Polish Name").reset_index(drop=True)
    
    with st.expander(f"➕ Add New {polish_type_label} Polish"):
        with st.form(key=f"add_form_{inventory_file}", clear_on_submit=True):
            new_name = st.text_input("Color Name").strip()
            new_qty = st.number_input("Qty", min_value=1, value=1)
            if st.form_submit_button("Add"):
                if new_name and new_name not in df["Polish Name"].values:
                    new_row = pd.DataFrame([[new_name, 0, new_qty, "Full"]], columns=["Polish Name", "Uses", "Quantity", "Fluid Level"])
                    df = pd.concat([df, new_row], ignore_index=True)
                    save_data(df, inventory_file)
                    st.rerun()

    # --- SINGLE CLEAN TABLE ---
    if not df.empty:
        for idx, row in df.iterrows():
            col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
            safe_key = str(row["Polish Name"]).replace(" ", "_")
            
            col1.write(f"**{row['Polish Name']}**")
            col2.write(f"Uses: {int(row['Uses'])}")
            
            if col3.button("Use", key=f"use_{inventory_file}_{safe_key}"):
                df.at[idx, "Uses"] += 1
                save_data(df, inventory_file)
                st.rerun()
            
            if col4.button("🗑️", key=f"del_{inventory_file}_{safe_key}"):
                df = df.drop(idx)
                save_data(df, inventory_file)
                st.rerun()
            st.markdown("---")
    else:
        st.info(f"No {polish_type_label.lower()} polishes added yet.")

with tab1:
    render_polish_tab("gel_inventory.csv", "Gel")

with tab2:
    render_polish_tab("regular_inventory.csv", "Regular")

# --- CLIENT NOTES TAB ---
with tab3:
    st.header("👥 Client Histories")
    clients_df = load_data("client_history.csv")
    gel_df = load_data("gel_inventory.csv")
    reg_df = load_data("regular_inventory.csv")
    all_colors = sorted(list(gel_df["Polish Name"].values) + list(reg_df["Polish Name"].values))
    
    with st.form("client_form"):
        c_name = st.text_input("Client Name")
        p_type = st.selectbox("Polish Type", ["Gel", "Regular", "Other"])
        p_color = st.selectbox("Polish Color", [""] + all_colors)
        c_notes = st.text_area("Notes")
        if st.form_submit_button("Save Entry"):
            if c_name:
                new_row = pd.DataFrame([[datetime.today().strftime('%Y-%m-%d'), c_name, p_type, p_color, c_notes]], 
                                       columns=["Date", "Client Name", "Polish Type", "Polish Name", "Notes"])
                clients_df = pd.concat([clients_df, new_row], ignore_index=True)
                save_data(clients_df, "client_history.csv")
                st.rerun()

# --- ANALYTICS ---
with tab4:
    st.header("📈 Usage Charts")
    gel_df = load_data("gel_inventory.csv")
    if not gel_df.empty and gel_df["Uses"].sum() > 0:
        fig = px.pie(gel_df[gel_df["Uses"] > 0], values='Uses', names='Polish Name', color_discrete_sequence=['#6A8E87', '#D97466', '#E2A765'])
        st.plotly_chart(fig, use_container_width=True)