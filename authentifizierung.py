import streamlit as st

def check_password_and_user():
    """Prüft das Passwort und bietet eine Dropdown-Auswahl für Mitarbeiter (Enter-Taste aktiviert)."""
    if "password_correct" not in st.session_state:
        st.title("🔒 Login & Anmeldung")
        
        kollegen_aus_secrets = st.secrets.get("MITARBEITER_LISTE", ["Keine Mitarbeiter hinterlegt"])

        admin_name = kollegen_aus_secrets[0]

        mitarbeiter_liste = ["-- Bitte Namen auswählen --", admin_name] + list(kollegen_aus_secrets)
        
        # Ein Streamlit-Formular bündelt die Eingaben und reagiert auf die Enter-Taste
        with st.form("login_form", clear_on_submit=False):
            user_wahl = st.selectbox("Name auswählen", mitarbeiter_liste)
            st.text_input("Bitte gib dein Passwort ein:", type="password", key="password_entry")
            
            # Ein Formular benötigt zwingend einen st.form_submit_button
            submit_button = st.form_submit_button("Einloggen", use_container_width=True)
        
        # Die Logik wird ausgeführt, wenn der Button geklickt ODER Enter gedrückt wird
        if submit_button:
            if user_wahl == "-- Bitte Namen wählen --":
                st.error("Bitte wähle zuerst deinen Namen aus der Liste aus!")
            else:
                is_admin_user = (user_wahl == kollegen_aus_secrets[0])
                
                if is_admin_user:
                    if st.session_state["password_entry"] == st.secrets["ADMIN_PASSWORD"]:
                        st.session_state["password_correct"] = True
                        st.session_state["current_user"] = user_wahl
                        st.session_state["is_admin"] = True
                        st.rerun()
                    else:
                        st.error("Falsches Admin-Passwort!")
                else:
                    if st.session_state["password_entry"] == st.secrets["APP_PASSWORD"]:
                        st.session_state["password_correct"] = True
                        st.session_state["current_user"] = user_wahl
                        st.session_state["is_admin"] = False
                        st.rerun()
                    else:
                        st.error("Falsches Mitarbeiter-Passwort!")
        return False
    return st.session_state["password_correct"]

    return st.session_state["password_correct"]

