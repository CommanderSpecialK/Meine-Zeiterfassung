import streamlit as st

def check_password_and_user():
    """Prüft das Passwort und bietet eine Dropdown-Auswahl für Mitarbeiter."""
    if "password_correct" not in st.session_state:
        st.title("🔒 Login & Anmeldung")
        
        # --- MITARBEITER LISTE ---
        mitarbeiter_liste = [
            "-- Bitte Namen wählen --",
            "Kogler",  # <--- ADMIN USER!
            "Maringer",
            "Ganglberger"
        ]
        
        user_wahl = st.selectbox("Wer bist du?", mitarbeiter_liste)
        st.text_input("Bitte gib das App-Passwort ein:", type="password", key="password_entry")
        
        if st.button("Einloggen", use_container_width=True):
            if user_wahl == "-- Bitte Namen wählen --":
                st.error("Bitte wähle zuerst deinen Namen aus der Liste aus!")
            elif st.session_state["password_entry"] == st.secrets["APP_PASSWORD"]:
                st.session_state["password_correct"] = True
                st.session_state["current_user"] = user_wahl
                
                # Prüfen, ob der ausgewählte Name der Admin ist
                st.session_state["is_admin"] = (user_wahl == "Kogler") # <--- Hier exakt denselben Admin-Namen eintragen!
                st.rerun()
            else:
                st.error("Falsches Passwort!")
        return False
    return st.session_state["password_correct"]
