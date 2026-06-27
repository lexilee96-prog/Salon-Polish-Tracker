import streamlit as st
import pandas as pd
import os
from datetime import datetime
import plotly.express as px

# Set page config
st.set_page_config(page_title="Salon Polish Tracker", layout="wide")

# --- RETRO BOHO COLOR THEME, LIGHT TEXT & LARGE PRINT CSS ---
st.markdown("""
    <style>
    /* Global Background and Fonts */
    html, body, [class*="css"], p, div, label {
        font-size: 1.25rem !important;
        color: #5D544C !important; /* Soft earthy charcoal for gentle reading */
        font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
    }
    .stApp {
        background-color: #F3ECE1 !important; /* Beautiful soft warm cream base */
    }
    
    /* Input Fields, Text Areas, and Dropdowns */
    input, textarea, select, div[data-baseweb="select"] {
        background-color: #FFFFFF !important;
        color: #5D544C !important; 
        border: 2px solid #D1C2A5 !important; 
        border-radius: 6px !important;
    }
    
    /* FIXING DROPDOWN BARS */
    div[data-baseweb="select"] > div {
        background-color: #FFFFFF !important;
        color: #5D544C !important;
    }
    
    /* FIXING EXPANDER BARS */
    .streamlit-expanderHeader, [data-testid="stExpander"] {
        background-color: #FFFFFF !important;
        border: 1px solid #E5A398 !important;
        border-radius: 8px !important;
    }
    
    /* Main Headings */
    h1 { font-size: 3.5rem !important; color: #D97466 !important; font-weight: bold; text-align: center; margin-bottom: 2rem; } 
    h2 { font-size: 2.4rem !important; color: #E5A398 !important; border-bottom: 2px solid #E5A398; padding-bottom: 5px; } 
    h3 { font-size: 1.9rem !important; color: #6A8E87 !important; } 
    
    /* Tab Design */
    button[data-baseweb="tab"] {
        font-size: 1.5rem !important;
        color: #8C969E !important;
        padding: 12px 24px !important;
    }
    button[data-baseweb="tab"][aria-selected="true"] {
        color: #D97466 !important; 
        border-bottom-color: #D97466 !important;
        font-weight: bold !important;
    }

    /* Buttons Styling */
    .stButton>button {
        font-size: 1.25rem !important;
        background-color: #E2A765 !important; 
        color: #FFFFFF !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 0.5rem 1.5rem !important;
        box-shadow: 0px 3px 6px rgba(0,0,0,0.05);
    }
    .stButton>button:hover {
        background-color: #6A8E87 !important; 
        color: #FFFFFF !important;
    }
    
    /* Plus/Minus stepper button overrides */
    button[tabindex="0"] {
        color: #5D544C !important;
    }
    
    /* Horizontal lines styling */
    hr {
        border-color: #E5A398 !important;
        opacity: 0.4;
    }
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
    
    with st.expander(f"➕ Add New {polish_type_label} Polish Color"):
        with st.form(key=f"add_form_{inventory_file}", clear_on_submit=True):
            new_name = st.text_input(f"New {polish_type_label} Color Name").strip()
            new_qty = st.number_input("Starting Quantity", min_value=1, value=1)
            submit_button = st.form_submit_button(f"Add {polish_type_label}")
            
            if submit_button:
                if new_name and new_name not in df["Polish Name"].values:
                    new_row = pd.DataFrame([[new_name, 0, new_qty, "Full"]], columns=["Polish Name", "Uses", "Quantity", "Fluid Level"])
                    df = pd.concat([df, new_row], ignore_index=True)
                    save_data(df, inventory_file)
                    st.success(f"Added {new_name} successfully!")
                elif new_name:
                    st.warning("This color already exists!")

    if not df.empty:
        df = df.sort_values(by="Polish Name").reset_index(drop=True)
        st.subheader("Current Inventory")
        
        # Table Headers
        h_col1, h_col2, h_col3, h_col4, h_col5, h_col6 = st.columns([2.5, 2, 1.5, 1, 1, 0.8])
        h_col1.markdown("**Color Name**")
        h_col2.markdown("**Status Warning**")
        h_col3.markdown("**Bottle Fullness**")
        h_col4.markdown("**Log Use**")
        h_col5.markdown("**Stock Qty**")
        h_col6.markdown("**Actions**")
        st.markdown("---")

        for idx, row in df.iterrows():
            col_name, col_status, col_level, col_use, col_qty, col_del = st.columns([2.5, 2, 1.5, 1, 1, 0.8])
            
            # --- THE FIX: Use color name as memory key ---
            safe_key = str(row["Polish Name"]).replace(" ", "_")
            
            # 1. Inline Name Editor
            edited_name = col_name.text_input(
                "Edit Name", 
                value=row["Polish Name"], 
                key=f"name_{inventory_file}_{safe_key}", 
                label_visibility="collapsed"
            )
            if edited_name != row["Polish Name"] and edited_name.strip() != "":
                df.at[idx, "Polish Name"] = edited_name.strip()
                save_data(df, inventory_file)
                st.rerun()
            
            # 2. Fluid Level Dropdown & Status Color Matching
            current_level = row["Fluid Level"] if pd.notna(row["Fluid Level"]) else "Full"
            level_options = ["Full", "Half Full", "Nearly Empty", "Empty"]
            default_idx = level_options.index(current_level) if current_level in level_options else 0
            
            chosen_level = col_level.selectbox(
                "Level", 
                options=level_options, 
                index=default_idx, 
                key=f"level_{inventory_file}_{safe_key}",
                label_visibility="collapsed"
            )
            
            if chosen_level != current_level:
                df.at[idx, "Fluid Level"] = chosen_level
                if chosen_level == "Full":
                    df.at[idx, "Uses"] = 0
                save_data(df, inventory_file)
                st.rerun()

            # 3. Dynamic Warning Flags
            is_high_use = row["Uses"] >= 25
            
            if chosen_level == "Full":
                if is_high_use:
                    col_status.markdown("<span style='color:#D97466; font-weight:bold;'>🔴 High Use Warning (Full)</span>", unsafe_allow_html=True)
                else:
                    col_status.markdown("<span style='color:#6A8E87; font-weight:bold;'>🟢 Full OK</span>", unsafe_allow_html=True)
            elif chosen_level == "Half Full":
                col_status.markdown("<span style='color:#E2A765; font-weight:bold;'>🟡 Half Full</span>", unsafe_allow_html=True)
            elif chosen_level == "Nearly Empty":
                col_status.markdown("<span style='color:#D97466; font-weight:bold;'>🔴 Nearly Empty (Reorder!)</span>", unsafe_allow_html=True)
            elif chosen_level == "Empty":
                col_status.markdown("<span style='color:#7F7F7F; font-weight:bold;'>⚪ Empty / Out</span>", unsafe_allow_html=True)
            
            # 4. Use Button
            if col_use.button("Use", key=f"use_{inventory_file}_{safe_key}"):
                df.at[idx, "Uses"] += 1
                save_data(df, inventory_file)
                st.rerun()
                
            # 5. Quantity Input
            qty_val = col_qty.number_input("Qty", min_value=0, value=int(row["Quantity"]), key=f"qty_{inventory_file}_{safe_key}", label_visibility="collapsed")
            if qty_val != row["Quantity"]:
                df.at[idx, "Quantity"] = qty_val
                save_data(df, inventory_file)
                st.rerun()
                
            # 6. Delete Button
            if col_del.button("🗑️", key=f"del_{inventory_file}_{safe_key}"):
                df = df.drop(idx)
                save_data(df, inventory_file)
                st.rerun()
            
            st.markdown("<hr style='margin:0.4rem 0;' />", unsafe_allow_html=True)
    else:
        st.info(f"No {polish_type_label.lower()} polishes added yet.")

with tab1:
    render_polish_tab("gel_inventory.csv", "Gel")

with tab2:
    render_polish_tab("regular_inventory.csv", "Regular")

# --- CLIENT NOTES TAB ---
with tab3:
    st.header("👥 Client Histories & Upcoming Notes")
    
    clients_df = load_data("client_history.csv")
    gel_df = load_data("gel_inventory.csv")
    reg_df = load_data("regular_inventory.csv")
    
    all_colors = sorted(list(gel_df["Polish Name"].values) + list(reg_df["Polish Name"].values))
    
    col_form, col_history = st.columns([1, 1])
    
    with col_form:
        st.subheader("📝 Log New Appointment / Note")
        c_name = st.text_input("Client Name", key="client_name_input").strip()
        p_type = st.selectbox("Polish Type Used", ["Gel", "Regular", "None/Other"])
        p_color = st.selectbox("Polish Color Select", [""] + all_colors)
        c_notes = st.text_area("Notes (Reminders, preferences, or issues)")
        
        if st.button("Save Client Entry"):
            if c_name:
                today_str = datetime.today().strftime('%Y-%m-%d')
                new_client_row = pd.DataFrame([[today_str, c_name, p_type, p_color, c_notes]], 
                                              columns=["Date", "Client Name", "Polish Type", "Polish Name", "Notes"])
                clients_df = pd.concat([clients_df, new_client_row], ignore_index=True)
                save_data(clients_df, "client_history.csv")
                st.success(f"History updated for {c_name}!")
                st.rerun()
            else:
                st.error("Please provide a Client Name.")
                
    with col_history:
        st.subheader("📋 Client Directory")
        
        if not clients_df.empty:
            unique_clients = sorted(list(clients_df["Client Name"].unique()))
            selected_client = st.selectbox("Select a client from your list to view history:", ["-- Choose a Client --"] + unique_clients)
            
            st.markdown("**OR search manually:**")
            search_name = st.text_input("Type name here...").strip()
            
            final_search = search_name if search_name else (selected_client if selected_client != "-- Choose a Client --" else "")
            
            if final_search:
                st.markdown(f"### History for {final_search}")
                filtered_df = clients_df[clients_df["Client Name"].str.contains(final_search, case=False, na=False)]
                if not filtered_df.empty:
                    for _, c_row in filtered_df.iloc[::-1].iterrows():
                        st.markdown(f"📅 **Date:** {c_row['Date']}")
                        st.markdown(f"💅 **Polish:** {c_row['Polish Type']} — {c_row['Polish Name']}")
                        st.markdown(f"📝 **Notes:** {c_row['Notes']}")
                        st.markdown("<hr />", unsafe_allow_html=True)
                else:
                    st.info("No history entries match that name.")
        else:
            st.info("No clients saved in the system yet.")

# --- NEW ANALYTICS TAB WITH PIE CHARTS ---
with tab4:
    st.header("📈 Polish Usage Charts & Trends")
    
    gel_df = load_data("gel_inventory.csv")
    reg_df = load_data("regular_inventory.csv")
    
    col_chart1, col_chart2 = st.columns(2)
    
    boho_colors = ['#6A8E87', '#D97466', '#E2A765', '#E5A398', '#D1C2A5']
    
    with col_chart1:
        st.subheader("✨ Top Gel Polish Usage Breakdown")
        if not gel_df.empty and gel_df["Uses"].sum() > 0:
            fig_gel = px.pie(
                gel_df[gel_df["Uses"] > 0], 
                values='Uses', 
                names='Polish Name', 
                color_discrete_sequence=boho_colors
            )
            fig_gel.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig_gel, use_container_width=True)
        else:
            st.info("No Gel usage logs to map yet.")
            
    with col_chart2:
        st.subheader("🎨 Top Regular Polish Usage Breakdown")
        if not reg_df.empty and reg_df["Uses"].sum() > 0:
            fig_reg = px.pie(
                reg_df[reg_df["Uses"] > 0], 
                values='Uses', 
                names='Polish Name', 
                color_discrete_sequence=boho_colors
            )
            fig_reg.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig_reg, use_container_width=True)
        else:
            st.info("No Regular usage logs to map yet.")