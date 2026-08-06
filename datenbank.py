import streamlit as st
import pandas as pd
from datetime import datetime, timezone
import pytz
from streamlit_gsheets import GSheetsConnection

# Verbindung initialisieren
conn = st.connection("gsheets", type=GSheetsConnection)

def get_local_now():
    """Holt die aktuelle Zeit basierend auf der Zeitzone des Benutzer-Browsers."""
    try:
        user_tz_name = st.context.timezone  
        local_tz = pytz.timezone(user_tz_name)
    except Exception:
        local_tz = pytz.timezone("Europe/Berlin")  
    return datetime.now(timezone.utc).astimezone(local_tz).replace(tzinfo=None)

def load_data():
    """Lädt die aktuellen Daten aus dem Google Sheet."""
    try:
        df = conn.read(worksheet="Zeiterfassung", ttl="0s")
        if df.empty or df.columns.size < 5:
            return pd.DataFrame(columns=["Mitarbeiter", "Start", "Projekt", "Unterprojekt", "Dauer_Min"])
        return df
    except Exception:
        return pd.DataFrame(columns=["Mitarbeiter", "Start", "Projekt", "Unterprojekt", "Dauer_Min"])

def save_data(df):
    """Überschreibt das Google Sheet sicher mit den neuen Daten."""
    conn.update(worksheet="Zeiterfassung", data=df)
