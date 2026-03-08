import streamlit as st
from utils import init_connection

supabase = init_connection()

st.title("🏆 2026 Oscars Predictions")
st.subheader("Login to your account or create a new one to start making picks.")

try:
    response = supabase.table("users").select("*").execute()
    users = response.data
    user_names = [u["name"] for u in users]
except Exception as e:
    st.error(f"Error connecting to database: {e}")
    users = []
    user_names = []

col1, col2 = st.columns(2)

with col1:
    with st.container(border=True):
        st.markdown("### Existing Users")
        selected_user = st.selectbox("Select your name", ["-- Select User --"] + user_names)
        if st.button("Log In", type="primary", use_container_width=True):
            if selected_user != "-- Select User --":
                user_id = next(u["id"] for u in users if u["name"] == selected_user)
                st.session_state.user_id = user_id
                st.session_state.user_name = selected_user
                st.rerun()
            else:
                st.warning("Please select a user.")

with col2:
    with st.container(border=True):
        st.markdown("### New Account")
        with st.form("new_user_form", clear_on_submit=True):
            new_user_name = st.text_input("New User Name")
            submitted = st.form_submit_button("Create & Log In", use_container_width=True)
            if submitted:
                if new_user_name:
                    if new_user_name in user_names:
                        st.error("User already exists!")
                    else:
                        try:
                            res = supabase.table("users").insert({"name": new_user_name}).execute()
                            user_id = res.data[0]["id"]
                            st.session_state.user_id = user_id
                            st.session_state.user_name = new_user_name
                            st.success(f"User '{new_user_name}' created!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error creating user: {e}")
                else:
                    st.warning("Please enter a name.")
