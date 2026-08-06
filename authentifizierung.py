import streamlit as st

def check_password_and_user():
    """Prüft das Passwort und speichert das Mitarbeiter-Kürzel."""
    if "password_correct" not in st.session_state:
        st.title("🔒 Login & Anmeldung")
        st.text_input("Dein Name oder Kürzel (z.B. M. Mustermann):", key="user_name")
        st.text_input("Bitte gib das App-Passwort ein:", type="password", key="password_entry")
        
        if st.button("Einloggen", use_container_width=True):
            if not st.session_state["user_name"].strip():
                st.error("Bitte gib zuerst deinen Namen ein!")
            elif st.session_state["password_entry"] == st.secrets["APP_PASSWORD"]:
                st.session_state["password_correct"] = True
                st.session_state["current_user"] = st.session_state["user_name"].strip()
                st.rerun()
            else:
                st.error("Falsches Passwort!")
        return False
    return st.session_state["password_correct"]
