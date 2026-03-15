import streamlit as st
import pandas as pd
from utils import init_connection

supabase = init_connection()

st.title("🛡️ Admin: Set Winners")

# Very basic admin gate (for a real app, use auth roles)
admin_code = st.text_input("Admin Code", type="password")
if admin_code != st.secrets.get("admin_code", "oscaradmin"):
    st.warning("Please enter the admin code to access this page.")
    st.stop()
    
st.success("Admin access granted!")

@st.cache_data(ttl=60)
def fetch_base_data():
    categories = supabase.table("categories").select("*").execute().data
    nominees = supabase.table("nominees").select("*").execute().data
    return categories, nominees

try:
    categories, nominees = fetch_base_data()
except Exception as e:
    st.error(f"Error fetching data: {e}")
    st.stop()

# Organize data
noms_by_cat = {}
for nom in nominees:
    noms_by_cat.setdefault(nom["category_id"], []).append(nom)

categories_sorted = sorted(categories, key=lambda x: x["point_value"], reverse=True)

with st.form("admin_winners_form"):
    st.write("Select the official winner for each category.")
    new_winners = {}
    
    for cat in categories_sorted:
        cat_id = cat["id"]
        current_winner_id = cat.get("winner_id")
        
        cat_noms = noms_by_cat.get(cat_id, [])
        if not cat_noms:
            continue
            
        nom_options = ["-- Not yet announced --"]
        default_idx = 0
        
        for idx, n in enumerate(cat_noms):
            display = n["name"]
            if n["movie"] and n["name"] != n["movie"]:
                display += f" ({n['movie']})"
            nom_options.append(display)
            
            if n["id"] == current_winner_id:
                default_idx = idx + 1 # +1 because of the Not Yet Announced option
                
        selected_nom_str = st.selectbox(
            f"{cat['name']} ({cat['point_value']} pts)",
            options=nom_options,
            index=default_idx,
            key=f"admin_{cat_id}"
        )
        
        if selected_nom_str != "-- Not yet announced --":
            selected_idx = nom_options.index(selected_nom_str) - 1
            new_winners[cat_id] = cat_noms[selected_idx]["id"]
        else:
            new_winners[cat_id] = None
            
    submitted = st.form_submit_button("Save Official Winners", type="primary")
    
    if submitted:
        try:
            for cat_id, winner_id in new_winners.items():
                supabase.table("categories").update({"winner_id": winner_id}).eq("id", cat_id).execute()
            st.success("Official winners have been updated!")
            fetch_base_data.clear() # clear cache so summary updates
            from views.leaderboard import fetch_leaderboard_data
            try:
                fetch_leaderboard_data.clear()
            except:
                pass
            from views.summary import fetch_base_data as summary_fetch_base_data
            try:
                summary_fetch_base_data.clear()
            except:
                pass
            st.balloons()
        except Exception as e:
            st.error(f"Error saving winners: {e}")
