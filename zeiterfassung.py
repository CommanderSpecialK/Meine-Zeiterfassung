import streamlit as st
import pandas as pd
from datetime import datetime
import os

# --- PAGE CONFIG ---
st.set_page_config(page_title="Zeiterfassung", page_icon="⏱️", layout="centered")

# --- PASSWORT SCHUTZ FUNKTION ---
def check_password():
    if "password_correct" not in st.session_state:
        st.title("🔒 Login erforderlich")
        st.text_input(
            "Bitte gib das Passwort ein:", 
            type="password", 
            on_change=lambda: st.session_state.update({"password_correct": st.session_state["password"] == st.secrets["APP_PASSWORD"]}), 
            key="password"
        )
        return False
    return st.session_state["password_correct"]

if check_password():

    LOG_FILE = "zeit_log.csv"
    st.title("Meine Zeiterfassung ⏱️")
    
    # Baugruppen-Liste (wiederverwendbar)
    baugruppen = [
        "Maschine Gesamt", "Bett & Anbauteile", "Hydraulik", "Hauptantrieb links", 
        "Spannmittel links & rechts", "Spindelkasten links", "C-Achse links", 
        "Spika rechts inkl. Hauptantrieb rechts inkl. Längsantrieb", "C-Achse rechts", 
        "Kreuzschlitten OL & OR", "Kreuzschlitten UR", "Reitstock inkl. Energiezuführung", 
        "Lünettenschlitten inkl. Energiezuführung", "Scheibenrevolver inkl. Aufbau", 
        "Lünette inkl. Aufbau", "Werkzeugmagazin inkl. Aufbau", "Dreh-Bohr-Fräseinheit inkl. Aufbau", 
        "Werkstück- und Werkzeugkontrolle", "Führungsbahnabdeckung oben & unten", 
        "Maschinenverkleidung inkl. Späneförderer", "Kühlmitteleinrichtung", 
        "Dokumentation, Vertriebsunterlagen, Abnahmeprotokolle", "Vorrichtungen", 
        "Portallader", "Steuerung & Antriebe allgemein", "Sonstiges"
    ]

    # Deine Projekte
    projekte = {
        "Allgemein": baugruppen,
        "M20": baugruppen,
        "M20 Automation": baugruppen,
        "M35 M40 M50": baugruppen,
        "M6x": baugruppen,
        "M70": baugruppen,
        "M80": baugruppen,
        "M1xx": baugruppen,
        "M200": baugruppen,
        "Windchill": baugruppen,
        "Sinumerik One": baugruppen,
        "Palettensystem": baugruppen,
        "Schulung": baugruppen,
        "Pause": ["Mittag", "Kaffee", "Kurzpause"]
    }
    
    # UI Layout für Auswahl
    col1, col2 = st.columns(2)
    with col1:
        projekt_wahl = st.selectbox("Projekt wählen", list(projekte.keys()))
    with col2:
        unterprojekt_wahl = st.selectbox("Baugruppe wählen", projekte[projekt_wahl])
    
    # Button: Start / Wechseln
    if st.button("🚀 Projekt starten / Wechseln", use_container_width=True):
        jetzt = datetime.now()
        zeit_string = jetzt.strftime("%Y-%m-%d %H:%M:%S")
        
        neuer_eintrag = {
            "Start": zeit_string,
            "Projekt": projekt_wahl,
            "Unterprojekt": unterprojekt_wahl,
            "Dauer_Min": 0.0
        }
        
        if not os.path.isfile(LOG_FILE):
            df = pd.DataFrame([neuer_eintrag])
            df.to_csv(LOG_FILE, index=False)
        else:
            df_alt = pd.read_csv(LOG_FILE)
            if len(df_alt) > 0:
                letzter_start = datetime.strptime(df_alt.iloc[-1]["Start"], "%Y-%m-%d %H:%M:%S")
                if df_alt.iloc[-1]["Projekt"] != "🏁 FEIERABEND":
                    dauer = (jetzt - letzter_start).total_seconds() / 60
                    df_alt.at[df_alt.index[-1], "Dauer_Min"] = round(dauer, 2)
            
            df_neu = pd.concat([df_alt, pd.DataFrame([neuer_eintrag])], ignore_index=True)
            df_neu.to_csv(LOG_FILE, index=False)
        st.success(f"Aktiviert: {projekt_wahl} - {unterprojekt_wahl}")
        st.rerun()
    
    # Button: Tag beenden
    if st.button("🏁 Tag beenden", use_container_width=True, type="primary"):
        if os.path.isfile(LOG_FILE):
            df_alt = pd.read_csv(LOG_FILE)
            if len(df_alt) > 0 and df_alt.iloc[-1]["Projekt"] != "🏁 FEIERABEND":
                jetzt = datetime.now()
                letzter_start = datetime.strptime(df_alt.iloc[-1]["Start"], "%Y-%m-%d %H:%M:%S")
                
                dauer = (jetzt - letzter_start).total_seconds() / 60
                df_alt.at[df_alt.index[-1], "Dauer_Min"] = round(dauer, 2)
                
                feierabend = {
                    "Start": jetzt.strftime("%Y-%m-%d %H:%M:%S"),
                    "Projekt": "🏁 FEIERABEND",
                    "Unterprojekt": "-",
                    "Dauer_Min": 0.0
                }
                df_final = pd.concat([df_alt, pd.DataFrame([feierabend])], ignore_index=True)
                df_final.to_csv(LOG_FILE, index=False)
                st.warning("Feierabend geloggt! Bis morgen.")
                st.rerun()
            else:
                st.info("Tag ist bereits beendet oder kein Eintrag vorhanden.")
    
    st.divider()
    
    # Anzeige & Export
    if os.path.isfile(LOG_FILE):
        df_display = pd.read_csv(LOG_FILE)
        heute = datetime.now().strftime("%Y-%m-%d")
        heutige_daten = df_display[df_display['Start'].str.contains(heute, na=False)]
        
        st.subheader("Dein Log von heute")
        if not heutige_daten.empty:
            st.table(heutige_daten[::-1].head(10))
        else:
            st.info("Heute noch keine Einträge vorhanden.")
        
        # Download Button für die CSV
        csv = df_display.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="💾 Gesamtes Logfile (CSV) herunterladen",
            data=csv,
            file_name=f"zeiterfassung_{heute}.csv",
            mime="text/csv"
        )
