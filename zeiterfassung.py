import streamlit as st
import pandas as pd
from datetime import datetime
import os


st.set_page_config(page_title="Zeiterfassung", page_icon="⏱️")
st.title("Meine Zeiterfassung ⏱️")

# --- PASSTWORT SCHUTZ FUNKTION ---
def check_password():
    if "password_correct" not in st.session_state:
        st.title("🔒 Login erforderlich")
        st.text_input("Bitte gib das Passwort ein:", type="password", on_change=lambda: st.session_state.update({"password_correct": st.session_state["password"] == st.secrets["APP_PASSWORD"]}), key="password")
        return False
    return st.session_state["password_correct"]

if check_password():

    LOG_FILE = "zeit_log.csv"
    

    
    # Deine Projekte
    projekte = {
        "Allgemein": ["Maschine Gesamt", "Bett & Anbauteile", "Hydraulik", "Hauptantrieb links", "Spannmittel links & rechts", "Spindelkasten links", "C-Achse links", "Spika rechts inkl. Hauptantrieb rechts inkl. Längsantrieb", "C-Achse rechts", "Kreuzschlitten OL & OR", "Kreuzschlitten UR", "Reitstock inkl. Energiezuführung", "Lünettenschlitten inkl. Energiezuführung", "Scheibenrevolver inkl. Aufbau", "Lünette inkl. Aufbau", "Werkzeugmagazin inkl. Aufbau", "Dreh-Bohr-Fräseinheit inkl. Aufbau", "Werkstück- und Werkzeugkontrolle", "Führungsbahnabdeckung oben & unten", "Maschinenverkleidung inkl. Späneförderer", "Kühlmitteleinrichtung", "Dokumentation, Vertriebsunterlagen, Abnahmeprotokolle", "Vorrichtungen", "Portallader", "Steuerung & Antriebe allgemein", "Sonstiges"],
        "M20": ["Maschine Gesamt", "Bett & Anbauteile", "Hydraulik", "Hauptantrieb links", "Spannmittel links & rechts", "Spindelkasten links", "C-Achse links", "Spika rechts inkl. Hauptantrieb rechts inkl. Längsantrieb", "C-Achse rechts", "Kreuzschlitten OL & OR", "Kreuzschlitten UR", "Reitstock inkl. Energiezuführung", "Lünettenschlitten inkl. Energiezuführung", "Scheibenrevolver inkl. Aufbau", "Lünette inkl. Aufbau", "Werkzeugmagazin inkl. Aufbau", "Dreh-Bohr-Fräseinheit inkl. Aufbau", "Werkstück- und Werkzeugkontrolle", "Führungsbahnabdeckung oben & unten", "Maschinenverkleidung inkl. Späneförderer", "Kühlmitteleinrichtung", "Dokumentation, Vertriebsunterlagen, Abnahmeprotokolle", "Vorrichtungen", "Portallader", "Steuerung & Antriebe allgemein", "Sonstiges"],
        "M20 Automation": ["Maschine Gesamt", "Bett & Anbauteile", "Hydraulik", "Hauptantrieb links", "Spannmittel links & rechts", "Spindelkasten links", "C-Achse links", "Spika rechts inkl. Hauptantrieb rechts inkl. Längsantrieb", "C-Achse rechts", "Kreuzschlitten OL & OR", "Kreuzschlitten UR", "Reitstock inkl. Energiezuführung", "Lünettenschlitten inkl. Energiezuführung", "Scheibenrevolver inkl. Aufbau", "Lünette inkl. Aufbau", "Werkzeugmagazin inkl. Aufbau", "Dreh-Bohr-Fräseinheit inkl. Aufbau", "Werkstück- und Werkzeugkontrolle", "Führungsbahnabdeckung oben & unten", "Maschinenverkleidung inkl. Späneförderer", "Kühlmitteleinrichtung", "Dokumentation, Vertriebsunterlagen, Abnahmeprotokolle", "Vorrichtungen", "Portallader", "Steuerung & Antriebe allgemein", "Sonstiges"],
        "M35 M40 M50": ["Maschine Gesamt", "Bett & Anbauteile", "Hydraulik", "Hauptantrieb links", "Spannmittel links & rechts", "Spindelkasten links", "C-Achse links", "Spika rechts inkl. Hauptantrieb rechts inkl. Längsantrieb", "C-Achse rechts", "Kreuzschlitten OL & OR", "Kreuzschlitten UR", "Reitstock inkl. Energiezuführung", "Lünettenschlitten inkl. Energiezuführung", "Scheibenrevolver inkl. Aufbau", "Lünette inkl. Aufbau", "Werkzeugmagazin inkl. Aufbau", "Dreh-Bohr-Fräseinheit inkl. Aufbau", "Werkstück- und Werkzeugkontrolle", "Führungsbahnabdeckung oben & unten", "Maschinenverkleidung inkl. Späneförderer", "Kühlmitteleinrichtung", "Dokumentation, Vertriebsunterlagen, Abnahmeprotokolle", "Vorrichtungen", "Portallader", "Steuerung & Antriebe allgemein", "Sonstiges"],
        "M6x": ["Maschine Gesamt", "Bett & Anbauteile", "Hydraulik", "Hauptantrieb links", "Spannmittel links & rechts", "Spindelkasten links", "C-Achse links", "Spika rechts inkl. Hauptantrieb rechts inkl. Längsantrieb", "C-Achse rechts", "Kreuzschlitten OL & OR", "Kreuzschlitten UR", "Reitstock inkl. Energiezuführung", "Lünettenschlitten inkl. Energiezuführung", "Scheibenrevolver inkl. Aufbau", "Lünette inkl. Aufbau", "Werkzeugmagazin inkl. Aufbau", "Dreh-Bohr-Fräseinheit inkl. Aufbau", "Werkstück- und Werkzeugkontrolle", "Führungsbahnabdeckung oben & unten", "Maschinenverkleidung inkl. Späneförderer", "Kühlmitteleinrichtung", "Dokumentation, Vertriebsunterlagen, Abnahmeprotokolle", "Vorrichtungen", "Portallader", "Steuerung & Antriebe allgemein", "Sonstiges"],
        "M70": ["Maschine Gesamt", "Bett & Anbauteile", "Hydraulik", "Hauptantrieb links", "Spannmittel links & rechts", "Spindelkasten links", "C-Achse links", "Spika rechts inkl. Hauptantrieb rechts inkl. Längsantrieb", "C-Achse rechts", "Kreuzschlitten OL & OR", "Kreuzschlitten UR", "Reitstock inkl. Energiezuführung", "Lünettenschlitten inkl. Energiezuführung", "Scheibenrevolver inkl. Aufbau", "Lünette inkl. Aufbau", "Werkzeugmagazin inkl. Aufbau", "Dreh-Bohr-Fräseinheit inkl. Aufbau", "Werkstück- und Werkzeugkontrolle", "Führungsbahnabdeckung oben & unten", "Maschinenverkleidung inkl. Späneförderer", "Kühlmitteleinrichtung", "Dokumentation, Vertriebsunterlagen, Abnahmeprotokolle", "Vorrichtungen", "Portallader", "Steuerung & Antriebe allgemein", "Sonstiges"],
        "M80": ["Maschine Gesamt", "Bett & Anbauteile", "Hydraulik", "Hauptantrieb links", "Spannmittel links & rechts", "Spindelkasten links", "C-Achse links", "Spika rechts inkl. Hauptantrieb rechts inkl. Längsantrieb", "C-Achse rechts", "Kreuzschlitten OL & OR", "Kreuzschlitten UR", "Reitstock inkl. Energiezuführung", "Lünettenschlitten inkl. Energiezuführung", "Scheibenrevolver inkl. Aufbau", "Lünette inkl. Aufbau", "Werkzeugmagazin inkl. Aufbau", "Dreh-Bohr-Fräseinheit inkl. Aufbau", "Werkstück- und Werkzeugkontrolle", "Führungsbahnabdeckung oben & unten", "Maschinenverkleidung inkl. Späneförderer", "Kühlmitteleinrichtung", "Dokumentation, Vertriebsunterlagen, Abnahmeprotokolle", "Vorrichtungen", "Portallader", "Steuerung & Antriebe allgemein", "Sonstiges"],
        "M1xx": ["Maschine Gesamt", "Bett & Anbauteile", "Hydraulik", "Hauptantrieb links", "Spannmittel links & rechts", "Spindelkasten links", "C-Achse links", "Spika rechts inkl. Hauptantrieb rechts inkl. Längsantrieb", "C-Achse rechts", "Kreuzschlitten OL & OR", "Kreuzschlitten UR", "Reitstock inkl. Energiezuführung", "Lünettenschlitten inkl. Energiezuführung", "Scheibenrevolver inkl. Aufbau", "Lünette inkl. Aufbau", "Werkzeugmagazin inkl. Aufbau", "Dreh-Bohr-Fräseinheit inkl. Aufbau", "Werkstück- und Werkzeugkontrolle", "Führungsbahnabdeckung oben & unten", "Maschinenverkleidung inkl. Späneförderer", "Kühlmitteleinrichtung", "Dokumentation, Vertriebsunterlagen, Abnahmeprotokolle", "Vorrichtungen", "Portallader", "Steuerung & Antriebe allgemein", "Sonstiges"],
        "M200": ["Maschine Gesamt", "Bett & Anbauteile", "Hydraulik", "Hauptantrieb links", "Spannmittel links & rechts", "Spindelkasten links", "C-Achse links", "Spika rechts inkl. Hauptantrieb rechts inkl. Längsantrieb", "C-Achse rechts", "Kreuzschlitten OL & OR", "Kreuzschlitten UR", "Reitstock inkl. Energiezuführung", "Lünettenschlitten inkl. Energiezuführung", "Scheibenrevolver inkl. Aufbau", "Lünette inkl. Aufbau", "Werkzeugmagazin inkl. Aufbau", "Dreh-Bohr-Fräseinheit inkl. Aufbau", "Werkstück- und Werkzeugkontrolle", "Führungsbahnabdeckung oben & unten", "Maschinenverkleidung inkl. Späneförderer", "Kühlmitteleinrichtung", "Dokumentation, Vertriebsunterlagen, Abnahmeprotokolle", "Vorrichtungen", "Portallader", "Steuerung & Antriebe allgemein", "Sonstiges"],
        "Windchill": ["Maschine Gesamt", "Bett & Anbauteile", "Hydraulik", "Hauptantrieb links", "Spannmittel links & rechts", "Spindelkasten links", "C-Achse links", "Spika rechts inkl. Hauptantrieb rechts inkl. Längsantrieb", "C-Achse rechts", "Kreuzschlitten OL & OR", "Kreuzschlitten UR", "Reitstock inkl. Energiezuführung", "Lünettenschlitten inkl. Energiezuführung", "Scheibenrevolver inkl. Aufbau", "Lünette inkl. Aufbau", "Werkzeugmagazin inkl. Aufbau", "Dreh-Bohr-Fräseinheit inkl. Aufbau", "Werkstück- und Werkzeugkontrolle", "Führungsbahnabdeckung oben & unten", "Maschinenverkleidung inkl. Späneförderer", "Kühlmitteleinrichtung", "Dokumentation, Vertriebsunterlagen, Abnahmeprotokolle", "Vorrichtungen", "Portallader", "Steuerung & Antriebe allgemein", "Sonstiges"],
        "Sinumerik One": ["Maschine Gesamt", "Bett & Anbauteile", "Hydraulik", "Hauptantrieb links", "Spannmittel links & rechts", "Spindelkasten links", "C-Achse links", "Spika rechts inkl. Hauptantrieb rechts inkl. Längsantrieb", "C-Achse rechts", "Kreuzschlitten OL & OR", "Kreuzschlitten UR", "Reitstock inkl. Energiezuführung", "Lünettenschlitten inkl. Energiezuführung", "Scheibenrevolver inkl. Aufbau", "Lünette inkl. Aufbau", "Werkzeugmagazin inkl. Aufbau", "Dreh-Bohr-Fräseinheit inkl. Aufbau", "Werkstück- und Werkzeugkontrolle", "Führungsbahnabdeckung oben & unten", "Maschinenverkleidung inkl. Späneförderer", "Kühlmitteleinrichtung", "Dokumentation, Vertriebsunterlagen, Abnahmeprotokolle", "Vorrichtungen", "Portallader", "Steuerung & Antriebe allgemein", "Sonstiges"],
        "Palettensystem": ["Maschine Gesamt", "Bett & Anbauteile", "Hydraulik", "Hauptantrieb links", "Spannmittel links & rechts", "Spindelkasten links", "C-Achse links", "Spika rechts inkl. Hauptantrieb rechts inkl. Längsantrieb", "C-Achse rechts", "Kreuzschlitten OL & OR", "Kreuzschlitten UR", "Reitstock inkl. Energiezuführung", "Lünettenschlitten inkl. Energiezuführung", "Scheibenrevolver inkl. Aufbau", "Lünette inkl. Aufbau", "Werkzeugmagazin inkl. Aufbau", "Dreh-Bohr-Fräseinheit inkl. Aufbau", "Werkstück- und Werkzeugkontrolle", "Führungsbahnabdeckung oben & unten", "Maschinenverkleidung inkl. Späneförderer", "Kühlmitteleinrichtung", "Dokumentation, Vertriebsunterlagen, Abnahmeprotokolle", "Vorrichtungen", "Portallader", "Steuerung & Antriebe allgemein", "Sonstiges"],
        "Schulung": ["Maschine Gesamt", "Bett & Anbauteile", "Hydraulik", "Hauptantrieb links", "Spannmittel links & rechts", "Spindelkasten links", "C-Achse links", "Spika rechts inkl. Hauptantrieb rechts inkl. Längsantrieb", "C-Achse rechts", "Kreuzschlitten OL & OR", "Kreuzschlitten UR", "Reitstock inkl. Energiezuführung", "Lünettenschlitten inkl. Energiezuführung", "Scheibenrevolver inkl. Aufbau", "Lünette inkl. Aufbau", "Werkzeugmagazin inkl. Aufbau", "Dreh-Bohr-Fräseinheit inkl. Aufbau", "Werkstück- und Werkzeugkontrolle", "Führungsbahnabdeckung oben & unten", "Maschinenverkleidung inkl. Späneförderer", "Kühlmitteleinrichtung", "Dokumentation, Vertriebsunterlagen, Abnahmeprotokolle", "Vorrichtungen", "Portallader", "Steuerung & Antriebe allgemein", "Sonstiges"],
        "Pause": ["Mittag", "Kaffee", "Kurzpause"]
    }
    
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
            "Dauer_Min": 0
        }
        
        if not os.path.isfile(LOG_FILE):
            df = pd.DataFrame([neuer_eintrag])
            df.to_csv(LOG_FILE, index=False)
        else:
            df_alt = pd.read_csv(LOG_FILE)
            if len(df_alt) > 0:
                letzter_start = datetime.strptime(df_alt.iloc[-1]["Start"], "%Y-%m-%d %H:%M:%S")
                # Nur berechnen, wenn der letzte Eintrag nicht schon "FEIERABEND" war
                if df_alt.iloc[-1]["Projekt"] != "🏁 FEIERABEND":
                    dauer = (jetzt - letzter_start).total_seconds() / 60
                    df_alt.at[df_alt.index[-1], "Dauer_Min"] = round(dauer, 2)
            
            df_neu = pd.concat([df_alt, pd.DataFrame([neuer_eintrag])], ignore_index=True)
            df_neu.to_csv(LOG_FILE, index=False)
        st.success(f"Aktiviert: {projekt_wahl}")
    
    # Button: Tag beenden
    if st.button("🏁 Tag beenden", use_container_width=True, type="primary"):
        if os.path.isfile(LOG_FILE):
            df_alt = pd.read_csv(LOG_FILE)
            if len(df_alt) > 0 and df_alt.iloc[-1]["Projekt"] != "🏁 FEIERABEND":
                jetzt = datetime.now()
                letzter_start = datetime.strptime(df_alt.iloc[-1]["Start"], "%Y-%m-%d %H:%M:%S")
                
                # Dauer für das letzte Projekt berechnen
                dauer = (jetzt - letzter_start).total_seconds() / 60
                df_alt.at[df_alt.index[-1], "Dauer_Min"] = round(dauer, 2)
                
                # Feierabend-Zeile hinzufügen
                feierabend = {
                    "Start": jetzt.strftime("%Y-%m-%d %H:%M:%S"),
                    "Projekt": "🏁 FEIERABEND",
                    "Unterprojekt": "-",
                    "Dauer_Min": 0
                }
                df_final = pd.concat([df_alt, pd.DataFrame([feierabend])], ignore_index=True)
                df_final.to_csv(LOG_FILE, index=False)
                st.warning("Feierabend geloggt! Bis morgen.")
            else:
                st.info("Tag ist bereits beendet oder kein Eintrag vorhanden.")
    
    st.divider()
    
    # Anzeige & Export
    if os.path.isfile(LOG_FILE):
        df_display = pd.read_csv(LOG_FILE)
        heute = datetime.now().strftime("%Y-%m-%d")
        heutige_daten = df_display[df_display['Start'].str.contains(heute)]
        
        st.subheader(f"Dein Log von heute")
        st.table(heutige_daten[::-1].head(10)) # 'table' sieht oft sauberer aus als 'dataframe'
        
        # Download Button für die CSV
        csv = df_display.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="💾 Gesamtes Logfile (CSV) herunterladen",
            data=csv,
            file_name=f"zeiterfassung_{heute}.csv",
            mime="text/csv",
    
        )






