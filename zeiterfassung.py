import streamlit as st
import pandas as pd
from datetime import datetime, timezone
import pytz
import os

# --- PAGE CONFIG ---
st.set_page_config(page_title="Zeiterfassung", page_icon="⏱️", layout="centered")

# --- ZEITZONEN-FUNKTION ---
def get_local_now():
    """Holt die aktuelle Zeit basierend auf der Zeitzone des Benutzer-Browsers."""
    try:
        user_tz_name = st.context.timezone  
        local_tz = pytz.timezone(user_tz_name)
    except Exception:
        local_tz = pytz.timezone("Europe/Berlin")  
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
    
    # Button-Bereich (Projekt starten / Tag beenden)
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

    # --- FEHLBUCHUNG / STORNO FUNKTION ---
    if os.path.isfile(LOG_FILE):
        df_storno = pd.read_csv(LOG_FILE)
        if len(df_storno) > 0:
            with st.expander("⚠️ Letzten Eintrag stornieren"):
                letzter = df_storno.iloc[-1]
                st.write(f"**Letzter Eintrag:** {letzter['Start']} | {letzter['Projekt']} ({letzter['Unterprojekt']})")
                st.warning("Das Löschen kann nicht rückgängig gemacht werden!")
                if st.button("🗑️ Diesen Eintrag unwiderruflich löschen", use_container_width=True):
                    df_gekuerzt = df_storno.drop(df_storno.index[-1])
                    df_gekuerzt.to_csv(LOG_FILE, index=False)
                    st.success("Eintrag erfolgreich gelöscht!")
                    st.rerun()
    
    st.divider()
    
    # Daten einlesen für Auswertungen
    if os.path.isfile(LOG_FILE):
        df_display = pd.read_csv(LOG_FILE)
        df_display['Start_dt'] = pd.to_datetime(df_display['Start'])
        
        # --- MONATSFILTER GENERIEREN ---
        st.subheader("📅 Monats-Statistik auswählen")
        
        # Erzeuge eine Liste aller verfügbaren Monate aus den Daten + dem aktuellen Monat
        df_display['Monat_Jahr'] = df_display['Start_dt'].dt.strftime('%Y-%m')
        aktuelle_monat_str = get_local_now().strftime('%Y-%m')
        
        verfuegbare_monate = sorted(list(df_display['Monat_Jahr'].dropna().unique()))
        if aktuelle_monat_str not in verfuegbare_monate:
            verfuegbare_monate.append(aktuelle_monat_str)
            verfuegbare_monate = sorted(verfuegbare_monate)
        
        # Darstellung für den Benutzer
        monats_namen = {
            "01": "Januar", "02": "Februar", "03": "März", "04": "April", 
            "05": "Mai", "06": "Juni", "07": "Juli", "08": "August", 
            "09": "September", "10": "Oktober", "11": "November", "12": "Dezember"
        }
        
        auswahl_labels = []
        default_index = len(verfuegbare_monate) - 1 
        
        for idx, m_j in enumerate(verfuegbare_monate):
            j, m = m_j.split("-")
            label = f"{monats_namen[m]} {j}"
            auswahl_labels.append(label)
            if m_j == aktuelle_monat_str:
                default_index = idx

        monat_auswahl_label = st.selectbox("Monat wählen", auswahl_labels, index=default_index)
        
        # Gewählten Monat wieder in das Format "YYYY-MM" zurückrechnen
        gewaehlter_index = auswahl_labels.index(monat_auswahl_label)
        gewaehlter_monat_str = verfuegbare_monate[gewaehlter_index]
        
        # Daten filtern nach dem gewählten Monat
        gefilterte_daten = df_display[df_display['Monat_Jahr'] == gewaehlter_monat_str].copy()

        # --- STATISTIK & GRAPH FÜR DEN GEWÄHLTEN MONAT ---
        if not gefilterte_daten.empty:
            df_projekte = gefilterte_daten[gefilterte_daten["Projekt"] != "🏁 FEIERABEND"].copy()
            
            if not df_projekte.empty:
                df_projekte["Dauer_Std"] = round(df_projekte["Dauer_Min"] / 60, 2)
                
                # Aggregieren für Statistik und Diagramm
                summary = df_projekte.groupby(["Projekt", "Unterprojekt"])["Dauer_Std"].sum().reset_index()
                summary.columns = ["Projekt", "Baugruppe", "Stunden (h)"]
                
                gesamt_stunden = round(summary["Stunden (h)"].sum(), 2)
                st.metric(label=f"Geleistete Arbeitszeit im {monat_auswahl_label}", value=f"{gesamt_stunden} Std")
                
                # Visualisierung: Balkendiagramm
                st.subheader(f"📊 Stundenverteilung im {monat_auswahl_label}")
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
                st.info(f"Keine Projektzeiten im {monat_auswahl_label} aufgezeichnet.")
        else:
            st.info(f"Keine Einträge für den Monat {monat_auswahl_label} gefunden.")
            
        st.divider()
        
        # --- LIVE STATUS HEUTE ---
        heute_str = get_local_now().strftime("%Y-%m-%d")
        heutige_daten = df_display[df_display['Start'].str.contains(heute_str, na=False)].copy()
        
        if len(heutige_daten) > 0 and heutige_daten.iloc[-1]["Projekt"] == "🏁 FEIERABEND":
            st.success("🎉 Der heutige Arbeitstag ist offiziell beendet!")
        else:
            st.info("⏱️ Der Arbeitstag läuft aktuell noch.")

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

