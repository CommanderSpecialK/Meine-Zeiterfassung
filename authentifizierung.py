import streamlit as st

def check_password_and_user():
    """Prüft das Passwort und bietet eine Dropdown-Auswahl für Mitarbeiter."""
    if "password_correct" not in st.session_state:
        st.title("🔒 Login & Anmeldung")
        
        # --- MITARBEITER LISTE ---
        mitarbeiter_liste = [
            "-- Bitte Namen wählen --",
            "Kogler",
            "Maringer",
            "Ganglberger"
        ]
        
        # Dropdown statt Freitextfeld
        user_wahl = st.selectbox("Wer bist du?", mitarbeiter_liste)
        
        # Passwort abfragen
        st.text_input("Bitte gib das App-Passwort ein:", type="password", key="password_entry")
        
        if st.button("Einloggen", use_container_width=True):
            if user_wahl == "-- Bitte Namen wählen --":
                st.error("Bitte wähle zuerst deinen Namen aus der Liste aus!")
            elif st.session_state["password_entry"] == st.secrets["APP_PASSWORD"]:
                st.session_state["password_correct"] = True
                st.session_state["current_user"] = user_wahl
                st.rerun()
            else:
                st.error("Falsches Passwort!")
        return False
    return st.session_state["password_correct"]
