import streamlit as st
import pandas as pd
from utils import init_connection

supabase = init_connection()

st.title("📋 My Summary")

user_id = st.session_state.user_id

@st.cache_data(ttl=300)
def fetch_base_data():
    categories = supabase.table("categories").select("*").execute().data
    nominees = supabase.table("nominees").select("*").execute().data
    return categories, nominees

try:
    categories, nominees = fetch_base_data()
    user_picks = supabase.table("picks").select("*").eq("user_id", user_id).execute().data
except Exception as e:
    st.error(f"Error fetching data: {e}")
    st.stop()

if not user_picks:
    st.info("You haven't saved any picks yet. Go to the 'Make Picks' page to get started!")
else:
    # Organize data
    noms_by_cat = {}
    for nom in nominees:
        noms_by_cat.setdefault(nom["category_id"], []).append(nom)
        
    current_picks_dict = {p["category_id"]: p["nominee_id"] for p in user_picks}
    current_want_picks_dict = {p["category_id"]: p["want_nominee_id"] for p in user_picks}
    categories_sorted = sorted(categories, key=lambda x: x["point_value"], reverse=True)

    summary_data = []
    
    # Calculate completion and score
    total_cats = len(categories)
    # Count a category as completed if at least one pick is made
    completed_cats = len(set(current_picks_dict.keys()) | set(current_want_picks_dict.keys()))
    
    st.progress(completed_cats / total_cats, text=f"Progress: {completed_cats}/{total_cats} Categories Picked")
    st.markdown("<br>", unsafe_allow_html=True)
    
    total_score = 0
    possible_score = 0 # points from decided categories that user picked
    
    for cat in categories_sorted:
        cat_id = cat["id"]
        
        pick_id = current_picks_dict.get(cat_id)
        want_pick_id = current_want_picks_dict.get(cat_id)
        
        if pick_id or want_pick_id:
            cat_noms = noms_by_cat.get(cat_id, [])
            
            # Will Win String
            display_will = "---"
            if pick_id:
                nom_name = next((n['name'] for n in cat_noms if n['id'] == pick_id), "Unknown")
                nom_movie = next((n['movie'] for n in cat_noms if n['id'] == pick_id), "")
                display_will = nom_name
                if nom_movie and nom_name != nom_movie:
                    display_will += f" ({nom_movie})"
                    
            # Should Win String
            display_want = "---"
            if want_pick_id:
                want_name = next((n['name'] for n in cat_noms if n['id'] == want_pick_id), "Unknown")
                want_movie = next((n['movie'] for n in cat_noms if n['id'] == want_pick_id), "")
                display_want = want_name
                if want_movie and want_name != want_movie:
                    display_want += f" ({want_movie})"
                
            status_will = "⏳ Pending"
            points_earned = 0
            
            actual_winner_id = cat.get("winner_id")
            
            TIE_CATEGORY_ID = "aebe81d6-36d2-4266-a9d2-d37d977cce9f"
            TIE_WINNERS = ["d2efbd9c-878f-478d-9d9f-73055bbb4cbf", "52586d8f-62cb-47ca-9e0d-559f7cca9e05"]
            is_tied_category = cat_id == TIE_CATEGORY_ID
            
            if (actual_winner_id or is_tied_category) and pick_id:
                possible_score += cat["point_value"]
                is_correct = False
                if is_tied_category:
                    is_correct = pick_id in TIE_WINNERS
                else:
                    is_correct = pick_id == actual_winner_id
                    
                if is_correct:
                    status_will = "✅ Correct"
                    points_earned = cat["point_value"]
                    total_score += points_earned
                else:
                    status_will = "❌ Incorrect"
                    
            # We only score the "Will Win" choice as per standard Oscar pool rules
            summary_data.append({
                "Category": cat["name"],
                "Who You Think Will Win": display_will,
                "Who You Think Should Win": display_want,
                "Points Value": cat["point_value"],
                "Status (Will Win)": status_will,
                "Earned": f"+{points_earned}" if points_earned > 0 else "-"
            })

    if possible_score > 0:
        st.metric("Total Score", f"{total_score} / {possible_score} pts")
    else:
        st.metric("Total Score", "0 pts", help="Points are awarded when official winners are announced.")

    if summary_data:
        df = pd.DataFrame(summary_data)
        st.dataframe(
            df, 
            use_container_width=True, 
            hide_index=True,
            column_config={
                "Status": st.column_config.TextColumn("Status", width="small")
            }
        )
