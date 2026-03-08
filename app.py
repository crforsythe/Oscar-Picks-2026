import streamlit as st

st.set_page_config(page_title="2026 Oscars Predictions", page_icon="🏆", layout="wide")

if "user_id" not in st.session_state:
    st.session_state.user_id = None
if "user_name" not in st.session_state:
    st.session_state.user_name = None

def logout():
    st.session_state.user_id = None
    st.session_state.user_name = None
    st.rerun()

login = st.Page("views/login.py", title="Log in", icon="🔐")
picks = st.Page("views/picks.py", title="Make Picks", icon="🗳️")
summary = st.Page("views/summary.py", title="My Summary", icon="📋")
leaderboard = st.Page("views/leaderboard.py", title="Leaderboard", icon="📊")
admin = st.Page("views/admin.py", title="Admin", icon="🛡️")

if st.session_state.user_id is None:
    pg = st.navigation([login])
else:
    st.sidebar.markdown(f"**Logged in as:** {st.session_state.user_name}")
    if st.sidebar.button("Log out"):
        logout()
    pg = st.navigation([picks, summary, leaderboard, admin])

pg.run()
