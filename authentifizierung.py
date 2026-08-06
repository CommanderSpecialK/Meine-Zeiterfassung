import streamlit as st

def check_password_and_user():
    """Prüft das Passwort und unterscheidet zwischen Mitarbeiter und Admin."""
    if "password_correct" not in st.session_state:
        st.title("🔒 Login & Anmeldung")
        
        # --- MITARBEITER LISTE ---
        mitarbeiter_liste = [
            "-- Bitte Namen wählen --",
            "Kogler (Admin)",  # <--- Trage hier deinen exakten Namen ein!
            "Ganglberger",
            "Maringer"
        ]
        
        user_wahl = st.selectbox("Wer bist du?", mitarbeiter_liste)
        st.text_input("Bitte gib dein Passwort ein:", type="password", key="password_entry")
        
        if st.button("Einloggen", use_container_width=True):
            if user_wahl == "-- Bitte Namen wählen --":
                st.error("Bitte wähle zuerst deinen Namen aus der Liste aus!")
            else:
                # Prüfen, ob der ausgewählte Name der Admin ist
                is_admin_user = (user_wahl == "Kogler (Admin)")
                
                if is_admin_user:
                    # Admin benötigt das ADMIN_PASSWORD
                    if st.session_state["password_entry"] == st.secrets["ADMIN_PASSWORD"]:
                        st.session_state["password_correct"] = True
                        st.session_state["current_user"] = user_wahl
                        st.session_state["is_admin"] = True
                        st.rerun()
                    else:
                        st.error("Falsches Admin-Passwort!")
                else:
                    # Normale Mitarbeiter benötigen das APP_PASSWORD
                    if st.session_state["password_entry"] == st.secrets["APP_PASSWORD"]:
                        st.session_state["password_correct"] = True
                        st.session_state["current_user"] = user_wahl
                        st.session_state["is_admin"] = False
                        st.rerun()
                    else:
                        st.error("Falsches Mitarbeiter-Passwort!")
        return False
    return st.session_state["password_correct"]

