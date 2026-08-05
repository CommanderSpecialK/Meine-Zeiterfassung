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
                st.session_state["feierabend_just_logged"] = True
                st.rerun()
            else:
                st.info("Tag ist bereits beendet oder kein Eintrag vorhanden.")
    
    st.divider()
    
    # Daten einlesen und filtern für Auswertungen
    if os.path.isfile(LOG_FILE):
        df_display = pd.read_csv(LOG_FILE)
        heute = datetime.now().strftime("%Y-%m-%d")
        heutige_daten = df_display[df_display['Start'].str.contains(heute, na=False)].copy()
        
        # --- ZUSAMMENFASSUNG NACH FEIERABEND ---
        ist_feierabend = len(heutige_daten) > 0 and heutige_daten.iloc[-1]["Projekt"] == "🏁 FEIERABEND"
        
        if ist_feierabend:
            st.header("📊 Tageszusammenfassung (Feierabend)")
            
            # Filtere Feierabend-Zeilen für die Berechnung heraus
            df_projekte = heutige_daten[heutige_daten["Projekt"] != "🏁 FEIERABEND"].copy()
            
            if not df_projekte.empty:
                # Berechne Stunden statt Minuten für bessere Lesbarkeit
                df_projekte["Dauer_Std"] = round(df_projekte["Dauer_Min"] / 60, 2)
                
                # Gruppierung nach Projekt und Baugruppe (Unterprojekt)
                summary = df_projekte.groupby(["Projekt", "Unterprojekt"])["Dauer_Std"].sum().reset_index()
                summary.columns = ["Projekt", "Baugruppe", "Geleistete Stunden (h)"]
                
                # Gesamtsumme berechnen
                gesamte_stunden = round(df_projekte["Dauer_Min"].sum() / 60, 2)
                
                # Kennzahlen anzeigen
                st.metric(label="Gesamte Arbeitszeit heute", value=f"{gesamte_stunden} Std")
                st.subheader("Aufteilung nach Baugruppen:")
                st.dataframe(summary, use_container_width=True, hide_index=True)
            else:
                st.info("Keine Projektzeiten für heute aufgezeichnet.")
            st.divider()

        # --- LIVE STATISTIK (WÄHREND DES TAGES) ---
        else:
            st.subheader("⏱️ Live-Statistik heute")
            df_projekte_live = heutige_daten[heutige_daten["Projekt"] != "🏁 FEIERABEND"].copy()
            if not df_projekte_live.empty:
                gesamte_min_live = df_projekte_live["Dauer_Min"].sum()
                # Berechne Zeit seit dem letzten Wechsel für das aktuelle Projekt
                letzter_start = datetime.strptime(df_projekte_live.iloc[-1]["Start"], "%Y-%m-%d %H:%M:%S")
                aktuell_vergangen_min = (datetime.now() - letzter_start).total_seconds() / 60
                
                gesamte_stunden_live = round((gesamte_min_live + aktuell_vergangen_min) / 60, 2)
                st.metric(label="Bisherige Arbeitszeit heute (inkl. aktuelles Projekt)", value=f"{gesamte_stunden_live} Std")
            else:
                st.info("Noch kein Projekt für heute gestartet.")
            st.divider()
        
        # --- TABELLEN ANZEIGE & DOWNLOAD ---
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
