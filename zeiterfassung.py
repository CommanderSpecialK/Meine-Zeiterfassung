import streamlit as st
import pandas as pd
from datetime import datetime, timezone
import pytz
import os

# --- PAGE CONFIG ---
st.set_page_config(page_title="Zeiterfassung", page_icon="⏱️", layout="centered")

# --- ZEITZONEN-FUNKTION (MEZ / Lokale Zeit absichern) ---
def get_local_now():
    """Holt die aktuelle Zeit basierend auf der Zeitzone des Benutzer-Browsers."""
    try:
        user_tz_name = st.context.timezone  # Liest z.B. 'Europe/Berlin' oder 'Europe/Vienna' aus
        local_tz = pytz.timezone(user_tz_name)
    except Exception:
        local_tz = pytz.timezone("Europe/Berlin")  # Fallback auf MEZ/MESZ
    
    # Konvertiert die aktuelle UTC-Zeit präzise in die lokale Zeitzone
    return datetime.now(timezone.utc).astimezone(local_tz).replace(tzinfo=None)

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
        jetzt = get_local_now()
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
                jetzt = get_local_now()
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
                st.rerun()
            else:
                st.info("Tag ist bereits beendet oder kein Eintrag vorhanden.")
    
    st.divider()
    
    # Daten einlesen und filtern für Auswertungen
    if os.path.isfile(LOG_FILE):
        df_display = pd.read_csv(LOG_FILE)
        
        # --- DATUMSFILTER ---
        st.subheader("📅 Auswertungszeitraum filtern")
        heute_datum = get_local_now().date()
        
        # Datumsbereich-Auswahl (Standardmäßig nur der heutige Tag vorausgewählt)
        date_range = st.date_input("Zeitraum wählen", [heute_datum, heute_datum])
        
        # Filtern nach ausgewähltem Zeitraum (nur valide Bereiche verarbeiten)
        if len(date_range) == 2:
            start_date, end_date = date_range
            # Konvertiere Spalte in Datetime für den Filter-Vergleich
            df_display['Start_dt'] = pd.to_datetime(df_display['Start'])
            gefilterte_daten = df_display[
                (df_display['Start_dt'].dt.date >= start_date) & 
                (df_display['Start_dt'].dt.date <= end_date)
            ].copy()
        else:
            gefilterte_daten = df_display[df_display['Start'].str.contains(heute_datum.strftime("%Y-%m-%d"), na=False)].copy()

        # --- RECHTLICHE STATISTIK & DIAGRAMM ---
        if not gefilterte_daten.empty:
            df_projekte = gefilterte_daten[gefilterte_daten["Project"] != "🏁 FEIERABEND" if "Project" in gefilterte_daten else gefilterte_daten["Projekt"] != "🏁 FEIERABEND"].copy()
            
            if not df_projekte.empty:
                df_projekte["Dauer_Std"] = round(df_projekte["Dauer_Min"] / 60, 2)
                
                # Aggregieren für Statistik und Diagramm
                summary = df_projekte.groupby(["Projekt", "Unterprojekt"])["Dauer_Std"].sum().reset_index()
                summary.columns = ["Projekt", "Baugruppe", "Stunden (h)"]
                
                # Gesamtstunden berechnen
                gesamte_stunden = round(summary["Stunden (h)"].sum(), 2)
                
                # Layout für Kennzahl und Diagramm
                st.metric(label="Geleistete Arbeitszeit im Zeitraum", value=f"{gesamte_stunden} Std")
                
                # Visualisierung: Balkendiagramm nach Baugruppen gerichtet
                st.subheader("📊 Stundenverteilung nach Baugruppe")
                # Kombiniere Projekt + Baugruppe für eine eindeutige Achsen-Beschriftung im Chart
                summary["Projekt & Baugruppe"] = summary["Projekt"] + " - " + summary["Baugruppe"]
                
                st.bar_chart(
                    data=summary,
                    x="Projekt & Baugruppe",
                    y="Stunden (h)",
                    use_container_width=True
                )
                
                st.subheader("📋 Zusammenfassung in Zahlen:")
                st.dataframe(summary[["Projekt", "Baugruppe", "Stunden (h)"]], use_container_width=True, hide_index=True)
            else:
                st.info("Keine Projektzeiten im gewählten Zeitraum aufgezeichnet.")
        else:
            st.info("Keine Einträge für diesen Zeitraum gefunden.")
            
        st.divider()
        
        # --- LIVE STATUS ODER FEIERABEND ANZEIGE (NUR FÜR HEUTE) ---
        heute_str = heute_datum.strftime("%Y-%m-%d")
        heutige_daten = df_display[df_display['Start'].str.contains(heute_str, na=False)].copy()
        
        if len(heutige_daten) > 0 and heutige_daten.iloc[-1]["Projekt"] == "🏁 FEIERABEND":
            st.success("🎉 Der heutige Arbeitstag ist offiziell beendet! Feierabend ist eingetragen.")
        else:
            st.info("⏱️ Der Arbeitstag läuft aktuell noch. Die Statistik oben zeigt den aktuellen Stand ohne das laufende Rest-Intervall.")

        st.divider()
        
        # --- TABELLEN ANZEIGE (HEUTE) & DOWNLOAD ---
        st.subheader("Dein Log von heute")
        if not heutige_daten.empty:
            st.table(heutige_daten[::-1].head(10))
        else:
            st.info("Heute noch keine Einträge vorhanden.")
        
        # Download Button für das gesamte File
        csv = df_display.drop(columns=['Start_dt'], errors='ignore').to_csv(index=False).encode('utf-8')
        st.download_button(
            label="💾 Gesamtes Logfile (CSV) herunterladen",
            data=csv,
            file_name=f"zeiterfassung_export.csv",
            mime="text/csv"
        )

