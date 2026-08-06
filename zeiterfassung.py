import streamlit as st
import pandas as pd
from datetime import datetime, timezone
import pytz
import os
import gspread
from google.oauth2.service_account import Credentials

# --- PAGE CONFIG ---
st.set_page_config(page_title="Team Zeiterfassung", page_icon="⏱️", layout="centered")

# --- ZEITZONEN-FUNKTION ---
def get_local_now():
    try:
        user_tz_name = st.context.timezone  
        local_tz = pytz.timezone(user_tz_name)
    except Exception:
        local_tz = pytz.timezone("Europe/Berlin")  
    return datetime.now(timezone.utc).astimezone(local_tz).replace(tzinfo=None)

# --- GOOGLE SHEETS VERBINDUNG (ÜBER SERVICE ACCOUNT) ---
def get_gspread_client():
    """Verbindet sich sicher über die Streamlit Secrets mit Google Sheets."""
    scopes = [
        "https://googleapis.com",
        "https://googleapis.com"
    ]
    # Holt sich die JSON-Zugangsdaten direkt aus den Streamlit Cloud Secrets
    credentials = Credentials.from_service_account_info(
        st.secrets["gconnections"], 
        scopes=scopes
    )
    return gspread.authorize(credentials)

def load_data():
    """Lädt die aktuellen Daten aus dem Google Sheet."""
    try:
        client = get_gspread_client()
        # Öffnet das Sheet anhand der URL aus deinen Secrets
        sheet = client.open_by_url(st.secrets["connections"]["gsheets"]["spreadsheet"])
        worksheet = sheet.worksheet("Zeiterfassung")
        
        # Holt alle Daten und konvertiert sie in ein Pandas Dataframe
        records = worksheet.get_all_records()
        df = pd.DataFrame(records)
        
        if df.empty:
            return pd.DataFrame(columns=["Mitarbeiter", "Start", "Projekt", "Unterprojekt", "Dauer_Min"])
        return df
    except Exception as e:
        # Falls das Sheet komplett neu/leer ist, leeres Tabellengerüst liefern
        return pd.DataFrame(columns=["Mitarbeiter", "Start", "Projekt", "Unterprojekt", "Dauer_Min"])

def save_data(df):
    """Überschreibt das Google Sheet sicher mit den neuen Daten."""
    client = get_gspread_client()
    sheet = client.open_by_url(st.secrets["connections"]["gsheets"]["spreadsheet"])
    worksheet = sheet.worksheet("Zeiterfassung")
    
    # Löscht das alte Sheet und schreibt die neuen Daten inklusive Header rein
    worksheet.clear()
    worksheet.update([df.columns.values.tolist()] + df.fillna("").values.tolist())


# --- ERWEITERTER LOGIN-SCHUTZ MIT MITARBEITER-AUSWAHL ---
def check_password_and_user():
    if "password_correct" not in st.session_state:
        st.title("🔒 Login & Anmeldung")
        
        # 1. Mitarbeiter Name/Kürzel eingeben
        st.text_input("Dein Name oder Kürzel (z.B. M. Mustermann):", key="user_name")
        
        # 2. Passwort abfragen
        st.text_input(
            "Bitte gib das App-Passwort ein:", 
            type="password", 
            key="password_entry"
        )
        
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

if check_password_and_user():
    
    current_user = st.session_state["current_user"]
    st.title("Meine Zeiterfassung ⏱️")
    st.caption(f"Eingeloggt als: **{current_user}**")
    
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
    
    # Daten initial laden
    df_global = load_data()
    
    # Button: Projekt starten / Wechseln
    if st.button("🚀 Projekt starten / Wechseln", use_container_width=True):
        jetzt = get_local_now()
        zeit_string = jetzt.strftime("%Y-%m-%d %H:%M:%S")
        
        neuer_eintrag = {
            "Mitarbeiter": current_user,
            "Start": zeit_string,
            "Projekt": projekt_wahl,
            "Unterprojekt": unterprojekt_wahl,
            "Dauer_Min": 0.0
        }
        
        # Letzten Eintrag SPEZIFISCH FÜR DIESEN MITARBEITER finden und Dauer updaten
        df_user = df_global[df_global["Mitarbeiter"] == current_user]
        if len(df_user) > 0:
            letzter_user_index = df_user.index[-1]
            if df_global.at[letzter_user_index, "Projekt"] != "🏁 FEIERABEND":
                letzter_start = datetime.strptime(df_global.at[letzter_user_index, "Start"], "%Y-%m-%d %H:%M:%S")
                dauer = (jetzt - letzter_start).total_seconds() / 60
                df_global.at[letzter_user_index, "Dauer_Min"] = round(dauer, 2)
        
        # Neuen Eintrag anhängen und hochladen
        df_neu = pd.concat([df_global, pd.DataFrame([neuer_eintrag])], ignore_index=True)
        save_data(df_neu)
        st.success(f"Aktiviert: {projekt_wahl} - {unterprojekt_wahl}")
        st.rerun()
    
    if st.button("🏁 Tag beenden", use_container_width=True, type="primary"):
        df_user = df_global[df_global["Mitarbeiter"] == current_user]
        if len(df_user) > 0 and df_user.iloc[-1]["Projekt"] != "🏁 FEIERABEND":
            jetzt = get_local_now()
            letzter_user_index = df_user.index[-1]
            
            letzter_start = datetime.strptime(df_global.at[letzter_user_index, "Start"], "%Y-%m-%d %H:%M:%S")
            dauer = (jetzt - letzter_start).total_seconds() / 60
            df_global.at[letzter_user_index, "Dauer_Min"] = round(dauer, 2)
            
            feierabend = {
                "Mitarbeiter": current_user,
                "Start": jetzt.strftime("%Y-%m-%d %H:%M:%S"),
                "Projekt": "🏁 FEIERABEND",
                "Unterprojekt": "-",
                "Dauer_Min": 0.0
            }
            df_final = pd.concat([df_global, pd.DataFrame([feierabend])], ignore_index=True)
            save_data(df_final)
            st.rerun()
        else:
            st.info("Dein Tag ist bereits beendet oder kein Eintrag vorhanden.")

    # --- STORNO FUNKTION (NUR FÜR DEN EIGENEN LETZTEN EINTRAG) ---
    df_user_storno = df_global[df_global["Mitarbeiter"] == current_user]
    if len(df_user_storno) > 0:
        with st.expander("⚠️ Meinen letzten Eintrag stornieren"):
            letzter = df_user_storno.iloc[-1]
            letzter_global_idx = df_user_storno.index[-1]
            st.write(f"**Dein letzter Eintrag:** {letzter['Start']} | {letzter['Projekt']} ({letzter['Unterprojekt']})")
            st.warning("Das Löschen entfernt deine letzte Buchung aus der Datenbank!")
            if st.button("🗑️ Diesen Eintrag unwiderruflich löschen", use_container_width=True):
                df_gekuerzt = df_global.drop(letzter_global_idx)
                save_data(df_gekuerzt)
                st.success("Eintrag erfolgreich gelöscht!")
                st.rerun()
    
    st.divider()
    
    # --- DATEN FILTERN FÜR DIE INDIVIDUELLE AUSWERTUNG ---
    if not df_global.empty:
        df_global['Start_dt'] = pd.to_datetime(df_global['Start'])
        
        # Filtere primär nach den Einträgen des angemeldeten Benutzers
        df_personal = df_global[df_global['Mitarbeiter'] == current_user].copy()
        
        # --- MONATSFILTER GENERIEREN ---
        st.subheader("📅 Meine Monats-Statistik")
        
        df_personal['Monat_Jahr'] = df_personal['Start_dt'].dt.strftime('%Y-%m')
        aktuelle_monat_str = get_local_now().strftime('%Y-%m')
        
        verfuegbare_monate = sorted(list(df_personal['Monat_Jahr'].dropna().unique()))
        if aktuelle_monat_str not in verfuegbare_monate:
            verfuegbare_monate.append(aktuelle_monat_str)
            verfuegbare_monate = sorted(verfuegbare_monate)
        
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
        
        gewaehlter_index = auswahl_labels.index(monat_auswahl_label)
        gewaehlter_monat_str = verfuegbare_monate[gewaehlter_index]
        
        gefilterte_daten = df_personal[df_personal['Monat_Jahr'] == gewaehlter_monat_str].copy()

        # --- STATISTIK & GRAPH ---
        if not gefilterte_daten.empty:
            df_projekte = gefilterte_daten[gefilterte_daten["Projekt"] != "🏁 FEIERABEND"].copy()
            
            if not df_projekte.empty:
                df_projekte["Dauer_Std"] = round(df_projekte["Dauer_Min"] / 60, 2)
                summary = df_projekte.groupby(["Projekt", "Unterprojekt"])["Dauer_Std"].sum().reset_index()
                summary.columns = ["Projekt", "Baugruppe", "Stunden (h)"]
                
                gesamt_stunden = round(summary["Stunden (h)"].sum(), 2)
                st.metric(label=f"Deine Arbeitszeit im {monat_auswahl_label}", value=f"{gesamt_stunden} Std")
                
                st.subheader(f"📊 Stundenverteilung im {monat_auswahl_label}")
                summary["Projekt & Baugruppe"] = summary["Projekt"] + " - " + summary["Baugruppe"]
                
                st.bar_chart(data=summary, x="Projekt & Baugruppe", y="Stunden (h)", use_container_width=True)
                st.dataframe(summary[["Projekt", "Baugruppe", "Stunden (h)"]], use_container_width=True, hide_index=True)
            else:
                st.info(f"Keine Projektzeiten im {monat_auswahl_label} aufgezeichnet.")
        else:
            st.info(f"Keine Einträge für den Monat {monat_auswahl_label} gefunden.")
            
        st.divider()
        
        # --- LIVE STATUS HEUTE ---
        heute_str = get_local_now().strftime("%Y-%m-%d")
        heutige_daten = df_personal[df_personal['Start'].str.contains(heute_str, na=False)].copy()
        
        if len(heutige_daten) > 0 and heutige_daten.iloc[-1]["Projekt"] == "🏁 FEIERABEND":
            st.success("🎉 Dein heutiger Arbeitstag ist offiziell beendet!")
        else:
            st.info("⏱️ Dein Arbeitstag läuft aktuell noch.")

        st.divider()
        
        # --- TABELLEN ANZEIGE (EIGENE EINTRÄGE HEUTE) ---
        st.subheader("Dein Log von heute")
        if not heutige_daten.empty:
            st.table(heutige_daten[::-1].head(10)[["Start", "Projekt", "Unterprojekt", "Dauer_Min"]])
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

