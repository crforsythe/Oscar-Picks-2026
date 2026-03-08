import streamlit as st
from utils import init_connection

supabase = init_connection()

st.title("🗳️ Make Your Picks")

user_id = st.session_state.user_id

@st.cache_data(ttl=300)
def fetch_data():
    categories = supabase.table("categories").select("*").execute().data
    nominees = supabase.table("nominees").select("*").execute().data
    return categories, nominees

def get_category_group(cat_name):
    cat_name = cat_name.lower()
    if any(x in cat_name for x in ["picture", "directing", "international feature", "animated feature", "documentary feature"]):
        return "General Awards"
    elif "actor" in cat_name or "actress" in cat_name:
        return "Acting Awards"
    elif "writing" in cat_name:
        return "Writing Awards"
    else:
        return "Other & Technical"

try:
    categories, nominees = fetch_data()
    # Fetch user picks (don't cache this as it changes often)
    user_picks = supabase.table("picks").select("*").eq("user_id", user_id).execute().data
except Exception as e:
    st.error(f"Error fetching data: {e}")
    st.stop()

# Organize data
noms_by_cat = {}
for nom in nominees:
    noms_by_cat.setdefault(nom["category_id"], []).append(nom)
    
current_picks_dict = {p["category_id"]: p["nominee_id"] for p in user_picks}

# Group categories
grouped_categories = {
    "General Awards": [],
    "Acting Awards": [],
    "Writing Awards": [],
    "Other & Technical": []
}

# Sort by point value descending first
categories_sorted = sorted(categories, key=lambda x: x["point_value"], reverse=True)
for cat in categories_sorted:
    grp = get_category_group(cat["name"])
    grouped_categories[grp].append(cat)

tab_names = list(grouped_categories.keys())
tabs = st.tabs(tab_names)

# We will collect all form inputs into session state first or use a single form.
# A single form spanning multiple tabs works in Streamlit!
with st.form("picks_form"):
    new_picks = {}
    
    for tab_idx, grp_name in enumerate(tab_names):
        with tabs[tab_idx]:
            for cat in grouped_categories[grp_name]:
                cat_id = cat["id"]
                points = cat["point_value"]
                st.markdown(f"**{cat['name']}** <span style='color: gray; font-size: 0.9em;'>(*{points} pts*)</span>", unsafe_allow_html=True)
                
                cat_noms = noms_by_cat.get(cat_id, [])
                if not cat_noms:
                    st.write("No nominees found.")
                    continue
                
                # Fetch existing picks for this user/category
                existing_pick = next((p for p in user_picks if p["category_id"] == cat_id), None)
                current_will_win_id = existing_pick["nominee_id"] if existing_pick else None
                current_want_win_id = existing_pick["want_nominee_id"] if existing_pick else None
                
                # Setup display options
                nom_options = ["--- No Pick ---"]
                for n in cat_noms:
                    display = n["name"]
                    if n["movie"] and n["name"] != n["movie"]:
                        display += f" ({n['movie']})"
                    nom_options.append(display)
                
                # Default selection (Will Win)
                default_will_idx = 0
                for idx, n in enumerate(cat_noms):
                    if n["id"] == current_will_win_id:
                        default_will_idx = idx + 1
                        break
                        
                # Default selection (Want to Win)
                default_want_idx = 0
                for idx, n in enumerate(cat_noms):
                    if n["id"] == current_want_win_id:
                        default_want_idx = idx + 1
                        break
                        
                col1, col2 = st.columns(2)
                with col1:
                    will_win_str = st.selectbox(
                        "Who will win?",
                        options=nom_options,
                        index=default_will_idx,
                        key=f"will_{cat_id}"
                    )
                with col2:
                    want_win_str = st.selectbox(
                        "Who should win?",
                        options=nom_options,
                        index=default_want_idx,
                        key=f"want_{cat_id}"
                    )
                
                will_nom_id = None
                want_nom_id = None
                
                if will_win_str != "--- No Pick ---":
                    idx = nom_options.index(will_win_str) - 1
                    will_nom_id = cat_noms[idx]["id"]
                    
                if want_win_str != "--- No Pick ---":
                    idx = nom_options.index(want_win_str) - 1
                    want_nom_id = cat_noms[idx]["id"]
                    
                new_picks[cat_id] = {
                    "nominee_id": will_nom_id,
                    "want_nominee_id": want_nom_id
                }
                
                st.markdown("---")
                
    # Floating save button at the bottom of the form
    st.markdown("<br>", unsafe_allow_html=True)
    submitted_picks = st.form_submit_button("Save All Picks", type="primary", use_container_width=True)

    if submitted_picks:
        try:
            supabase.table("picks").delete().eq("user_id", user_id).execute()
            
            bulk_insert = []
            for cat_id, picks in new_picks.items():
                if picks["nominee_id"] is not None or picks["want_nominee_id"] is not None:
                    bulk_insert.append({
                        "user_id": user_id, 
                        "category_id": cat_id, 
                        "nominee_id": picks["nominee_id"],
                        "want_nominee_id": picks["want_nominee_id"]
                    })
            
            if bulk_insert:
                supabase.table("picks").insert(bulk_insert).execute()
                
            st.success("Your picks have been saved successfully!")
            st.balloons()
        except Exception as e:
            st.error(f"Error saving picks: {e}")
