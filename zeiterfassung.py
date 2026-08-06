import streamlit as st
import pandas as pd

# Importiert die ausgelagerten Logiken aus deinen neuen Dateien
from datenbank import get_local_now, load_data, save_data
from authentifizierung import check_password_and_user

# --- PAGE CONFIG (MUSS ganz oben stehen) ---
st.set_page_config(page_title="Team Zeiterfassung", page_icon="⏱️", layout="centered")

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
    
    col1, col2 = st.columns(2)
    with col1:
        projekt_wahl = st.selectbox("Projekt wählen", list(projekte.keys()))
    with col2:
        unterprojekt_wahl = st.selectbox("Baugruppe wählen", projekte[projekt_wahl])
    
    df_global = load_data()
    
    # --- BUTTON: PROJEKT STARTEN / WECHSELN ---
    if st.button("🚀 Projekt starten / Wechseln", use_container_width=True):
        jetzt = get_local_now()
        neuer_eintrag = {
            "Mitarbeiter": current_user, "Start": jetzt.strftime("%Y-%m-%d %H:%M:%S"),
            "Projekt": projekt_wahl, "Unterprojekt": unterprojekt_wahl, "Dauer_Min": 0.0
        }
        
        df_user = df_global[df_global["Mitarbeiter"] == current_user]
        if len(df_user) > 0:
            letzter_user_index = df_user.index[-1]
            if df_global.at[letzter_user_index, "Projekt"] != "🏁 FEIERABEND":
                try:
                    letzter_start = pd.to_datetime(df_global.at[letzter_user_index, "Start"]).to_pydatetime()
                    dauer = (jetzt - letzter_start).total_seconds() / 60
                    df_global.at[letzter_user_index, "Dauer_Min"] = round(max(0.0, dauer), 2)
                except Exception:
                    pass
        
        df_neu = pd.concat([df_global, pd.DataFrame([neuer_eintrag])], ignore_index=True)
        save_data(df_neu)
        st.success(f"Aktiviert: {projekt_wahl} - {unterprojekt_wahl}")
        st.rerun()
    
    # --- BUTTON: TAG BEENDEN ---
    if st.button("🏁 Tag beenden", use_container_width=True, type="primary"):
        df_user = df_global[df_global["Mitarbeiter"] == current_user]
        if len(df_user) > 0 and df_user.iloc[-1]["Projekt"] != "🏁 FEIERABEND":
            jetzt = get_local_now()
            letzter_user_index = df_user.index[-1]
            try:
                letzter_start = pd.to_datetime(df_global.at[letzter_user_index, "Start"]).to_pydatetime()
                dauer = (jetzt - letzter_start).total_seconds() / 60
                df_global.at[letzter_user_index, "Dauer_Min"] = round(max(0.0, dauer), 2)
            except Exception:
                pass
            
            feierabend = {
                "Mitarbeiter": current_user, "Start": jetzt.strftime("%Y-%m-%d %H:%M:%S"),
                "Projekt": "🏁 FEIERABEND", "Unterprojekt": "-", "Dauer_Min": 0.0
            }
            df_final = pd.concat([df_global, pd.DataFrame([feierabend])], ignore_index=True)
            save_data(df_final)
            st.rerun()
        else:
            st.info("Dein Tag ist bereits beendet oder kein Eintrag vorhanden.")

    # --- STORNO FUNKTION ---
    df_user_storno = df_global[df_global["Mitarbeiter"] == current_user]
    if len(df_user_storno) > 0:
        with st.expander("⚠️ Meinen letzten Eintrag stornieren"):
            letzter = df_user_storno.iloc[-1]
            st.write(f"**Dein letzter Eintrag:** {letzter['Start']} | {letzter['Projekt']}")
            if st.button("🗑️ Diesen Eintrag unwiderruflich löschen", use_container_width=True):
                df_gekuerzt = df_global.drop(df_user_storno.index[-1])
                save_data(df_gekuerzt)
                st.success("Eintrag erfolgreich gelöscht!")
                st.rerun()
    
    #st.divider()
    
    # --- INDIVIDUELLE AUSWERTUNGEN & GRAPHEN ---
    if not df_global.empty:
        df_global['Start_dt'] = pd.to_datetime(df_global['Start'], errors='coerce')
        df_personal = df_global[df_global['Mitarbeiter'] == current_user].copy()

        heute_str = get_local_now().strftime("%Y-%m-%d")
        heutige_daten = df_personal[df_personal['Start_dt'].dt.strftime('%Y-%m-%d') == heute_str].copy()
        
        if len(heutige_daten) > 0 and heutige_daten.iloc[-1]["Projekt"] == "🏁 FEIERABEND":
            st.success("🎉 Dein heutiger Arbeitstag ist offiziell beendet!")
        else:
            st.info("⏱️ Dein Arbeitstag läuft aktuell noch.")

        st.subheader("Dein Log von heute")
        if not heutige_daten.empty:
            heutige_daten['Start_Anzeige'] = heutige_daten['Start_dt'].dt.strftime('%Y-%m-%d %H:%M:%S')
            st.table(heutige_daten[::-1].head(10)[["Start_Anzeige", "Projekt", "Unterprojekt", "Dauer_Min"]].rename(columns={"Start_Anzeige": "Start"}))
        else:
            st.info("Heute noch keine Einträge vorhanden.")
        
        st.divider()
        st.subheader("📅 Meine Monats-Statistik")
        df_personal['Monat_Jahr'] = df_personal['Start_dt'].dt.strftime('%Y-%m')
        aktuelle_monat_str = get_local_now().strftime('%Y-%m')
        
        verfuegbare_monate = sorted(list(df_personal['Monat_Jahr'].dropna().unique()))
        if aktuelle_monat_str not in verfuegbare_monate:
            verfuegbare_monate.append(aktuelle_monat_str)
            verfuegbare_monate = sorted(verfuegbare_monate)
        
        monats_namen = {
            "01": "Januar", "02": "Februar", "03": "März", "04": "April", "05": "Mai", "06": "Juni",
            "07": "Juli", "08": "August", "09": "September", "10": "Oktober", "11": "November", "12": "Dezember"
        }
        
        auswahl_labels = [f"{monats_namen[m_j.split('-')[1]]} {m_j.split('-')[0]}" for m_j in verfuegbare_monate]
        default_idx = verfuegbare_monate.index(aktuelle_monat_str) if aktuelle_monat_str in verfuegbare_monate else len(verfuegbare_monate)-1
        
        monat_auswahl_label = st.selectbox("Monat wählen", auswahl_labels, index=default_idx)
        gewaehlter_monat_str = verfuegbare_monate[auswahl_labels.index(monat_auswahl_label)]
        
        gefilterte_daten = df_personal[df_personal['Monat_Jahr'] == gewaehlter_monat_str].copy()

        if not gefilterte_daten.empty:
            df_projekte = gefilterte_daten[gefilterte_daten["Projekt"] != "🏁 FEIERABEND"].copy()
            if not df_projekte.empty:
                df_projekte["Dauer_Min"] = pd.to_numeric(df_projekte["Dauer_Min"], errors='coerce').fillna(0.0)
                df_projekte["Dauer_Std"] = round(df_projekte["Dauer_Min"] / 60, 2)
                summary = df_projekte.groupby(["Projekt", "Unterprojekt"])["Dauer_Std"].sum().reset_index()
                summary.columns = ["Projekt", "Baugruppe", "Stunden (h)"]
                
                st.metric(label=f"Deine Arbeitszeit im {monat_auswahl_label}", value=f"{round(summary['Stunden (h)'].sum(), 2)} Std")
                summary["Projekt & Baugruppe"] = summary["Projekt"] + " - " + summary["Baugruppe"]
                st.bar_chart(data=summary, x="Projekt & Baugruppe", y="Stunden (h)", use_container_width=True)
                st.dataframe(summary[["Projekt", "Baugruppe", "Stunden (h)"]], use_container_width=True, hide_index=True)


