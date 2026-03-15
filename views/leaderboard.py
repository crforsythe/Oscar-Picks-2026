import streamlit as st
import pandas as pd
from utils import init_connection

supabase = init_connection()

st.title("📊 Global Leaderboard")

@st.cache_data(ttl=60)
def fetch_leaderboard_data():
    users = supabase.table("users").select("*").execute().data
    categories = supabase.table("categories").select("*").execute().data
    picks = supabase.table("picks").select("*").execute().data
    nominees = supabase.table("nominees").select("*").execute().data
    return users, categories, picks, nominees

try:
    users, categories, picks, nominees = fetch_leaderboard_data()
except Exception as e:
    st.error(f"Error fetching data: {e}")
    st.stop()

if not users:
    st.info("No users have registered yet.")
    st.stop()

# Aggregate results
user_dict = {u["id"]: u["name"] for u in users}
cat_dict = {c["id"]: c for c in categories}

results = []
for user_id, user_name in user_dict.items():
    user_picks = [p for p in picks if p["user_id"] == user_id]
    
    will_points = 0
    want_points = 0
    will_correct = 0
    want_correct = 0
    
    for p in user_picks:
        cat = cat_dict.get(p["category_id"])
        if not cat or not cat.get("winner_id"):
            continue
            
        points_val = cat.get("point_value", 0)
        actual_winner = cat["winner_id"]
        
        if p.get("nominee_id") == actual_winner:
            will_points += points_val
            will_correct += 1
            
        if p.get("want_nominee_id") == actual_winner:
            want_points += points_val
            want_correct += 1
            
    results.append({
        "User": user_name,
        "Will Win Points": will_points,
        "Should Win Points": want_points,
        "Will Win Correct": will_correct,
        "Should Win Correct": want_correct
    })

df = pd.DataFrame(results)

if df.empty or df[["Will Win Points", "Should Win Points", "Will Win Correct", "Should Win Correct"]].sum().sum() == 0:
    st.info("No points have been scored yet. Admin must set official winners before charts appear.")
else:
    import plotly.express as px

    # Let's assign a consistent color to each user
    unique_users = df["User"].unique()
    # We use a built-in plotly qualitative palette, looping it if there are many users
    color_sequence = px.colors.qualitative.Bold + px.colors.qualitative.Pastel + px.colors.qualitative.Dark2
    user_color_map = {user: color_sequence[i % len(color_sequence)] for i, user in enumerate(unique_users)}

    # Helper function to render a plotly bar chart
    def render_bar_chart(data, x_col, y_col, title):
        fig = px.bar(
            data, 
            x=x_col, 
            y=y_col, 
            color="User", 
            color_discrete_map=user_color_map,
            title=title
        )
        # Hide the legend to save space since colors are consistent and labels are on the axis
        fig.update_layout(showlegend=False, xaxis_title=None)
        st.plotly_chart(fig, use_container_width=True)

    # Create a 2x2 Grid using Streamlit columns
    col1, col2 = st.columns(2)
    
    with col1:
        # 1. Points for "Will Win"
        df_will_pts = df[["User", "Will Win Points"]].sort_values(by="Will Win Points", ascending=False)
        render_bar_chart(df_will_pts, "User", "Will Win Points", "1) 'Will Win' Points")
        
        st.markdown("<br><br>", unsafe_allow_html=True)
        
        # 3. Correct Guesses for "Will Win"
        df_will_corr = df[["User", "Will Win Correct"]].sort_values(by="Will Win Correct", ascending=False)
        render_bar_chart(df_will_corr, "User", "Will Win Correct", "3) 'Will Win' Correct Picks")

    with col2:
        # 2. Points for "Should Win"
        df_want_pts = df[["User", "Should Win Points"]].sort_values(by="Should Win Points", ascending=False)
        render_bar_chart(df_want_pts, "User", "Should Win Points", "2) 'Should Win' Points")
        
        st.markdown("<br><br>", unsafe_allow_html=True)
        
        # 4. Correct Guesses for "Should Win"
        df_want_corr = df[["User", "Should Win Correct"]].sort_values(by="Should Win Correct", ascending=False)
        render_bar_chart(df_want_corr, "User", "Should Win Correct", "4) 'Should Win' Correct Picks")

    st.markdown("---")
    st.subheader("👀 Everyone's Picks")
    
    pick_type = st.radio("Select Pick Type", ["Will Win", "Should Win"], horizontal=True)
    
    nom_dict = {n["id"]: n for n in nominees}
    user_names = list(user_dict.values())
    
    table_data = []
    
    # Sort categories by point value descending
    for cat in sorted(categories, key=lambda x: x["point_value"], reverse=True):
        row = {"Category": f"{cat['name']} ({cat['point_value']} pts)"}
        winner_id = cat.get("winner_id")
        
        for user_id, user_name in user_dict.items():
            user_pick = next((p for p in picks if p["user_id"] == user_id and p["category_id"] == cat["id"]), None)
            
            if user_pick:
                if pick_type == "Will Win":
                    nom_id = user_pick.get("nominee_id")
                else:
                    nom_id = user_pick.get("want_nominee_id")
                    
                if nom_id:
                    nom = nom_dict.get(nom_id)
                    nom_name = nom["name"] if nom else "Unknown"
                    if nom and nom.get("movie") and nom["name"] != nom["movie"]:
                        nom_name += f" ({nom['movie']})"
                        
                    is_correct = winner_id is not None and nom_id == winner_id
                    is_incorrect = winner_id is not None and nom_id != winner_id
                    
                    if is_correct:
                        row[user_name] = f"✅ {nom_name}"
                    elif is_incorrect:
                        row[user_name] = f"❌ {nom_name}"
                    else:
                        row[user_name] = f"⏳ {nom_name}"
                else:
                    row[user_name] = "---"
            else:
                row[user_name] = "---"
                
        table_data.append(row)
        
    picks_df = pd.DataFrame(table_data)
    
    def color_cells(val):
        if isinstance(val, str):
            if val.startswith("✅"):
                return 'background-color: rgba(40, 167, 69, 0.2)'
            elif val.startswith("❌"):
                return 'background-color: rgba(220, 53, 69, 0.2)'
        return ''
        
    if hasattr(picks_df.style, 'map'):
        styled_df = picks_df.style.map(color_cells, subset=user_names)
    else:
        styled_df = picks_df.style.applymap(color_cells, subset=user_names)
        
    st.dataframe(styled_df, use_container_width=True, hide_index=True)
