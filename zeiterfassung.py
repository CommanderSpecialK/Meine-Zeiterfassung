import streamlit as st
import pandas as pd
from datetime import datetime
import os

LOG_FILE = "zeit_log.csv"

st.set_page_config(page_title="Zeiterfassung", page_icon="⏱️")
st.title("Meine Zeiterfassung ⏱️")

# Deine Projekte
projekte = {
    "Projekt A": ["Konzept", "Umsetzung", "Review"],
    "Projekt B": ["Meeting", "Support", "Telefonat"],
    "Pause": ["Mittag", "Kaffee", "Kurzpause"]
}

col1, col2 = st.columns(2)

with col1:
    projekt_wahl = st.selectbox("Projekt wählen", list(projekte.keys()))
with col2:
    unterprojekt_wahl = st.selectbox("Unterprojekt wählen", projekte[projekt_wahl])

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

# NEU: Button: Tag beenden
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
    st.table(heutige_daten) # 'table' sieht oft sauberer aus als 'dataframe'
    
    # Download Button für die CSV
    csv = df_display.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="💾 Gesamtes Logfile (CSV) herunterladen",
        data=csv,
        file_name=f"zeiterfassung_{heute}.csv",
        mime="text/csv",
    )