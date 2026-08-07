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
    
    col_user, col_logout = st.columns([4, 1])
    with col_user:
        st.caption(f"Eingeloggt als: **{current_user}**")
    with col_logout:
        if st.button("🚪 Ausloggen", use_container_width=True):
            # Löscht alle Login-Daten aus dem aktuellen Sitzungsspeicher
            st.session_state.clear()
            st.rerun()
    

    
    # Baut das Dictionary für die App vollautomatisch zusammen

    projekte = st.secrets.get("PROJEKT_STRUKTUR", {"Allgemein": ["Sonstiges"]})


    
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
    
    #st.divider()
    
    # --- AUSWERTUNGEN & GRAPHEN (MIT ERWEITERTER ADMIN-ANSICHT) ---
    if not df_global.empty:
        df_global['Start_dt'] = pd.to_datetime(df_global['Start'], errors='coerce')
        df_global['Monat_Jahr'] = df_global['Start_dt'].dt.strftime('%Y-%m')
        aktuelle_monat_str = get_local_now().strftime('%Y-%m')
        
        # Persönliche Daten filtern (wird für Filter und Live-Status benötigt)
        df_personal_base = df_global[df_global['Mitarbeiter'] == current_user].copy()
        
        # Verfügbare Monate: Admin sieht alle Monate, Mitarbeiter nur seine eigenen
        if st.session_state.get("is_admin", False):
            verfuegbare_monate = sorted(list(df_global['Monat_Jahr'].dropna().unique()))
        else:
            verfuegbare_monate = sorted(list(df_personal_base['Monat_Jahr'].dropna().unique()))
            
        if aktuelle_monat_str not in verfuegbare_monate:
            verfuegbare_monate.append(aktuelle_monat_str)
            verfuegbare_monate = sorted(verfuegbare_monate)
            
        monats_namen = {
            "01": "Januar", "02": "Februar", "03": "März", "04": "April", "05": "Mai", "06": "Juni",
            "07": "Juli", "08": "August", "09": "September", "10": "Oktober", "11": "November", "12": "Dezember"
        }
        
        auswahl_labels = []
        for m_j in verfuegbare_monate:
            jahr, monat = m_j.split('-')
            label = f"{monats_namen[monat]} {jahr}"
            auswahl_labels.append(label)
            
        default_idx = verfuegbare_monate.index(aktuelle_monat_str) if aktuelle_monat_str in verfuegbare_monate else len(verfuegbare_monate)-1


                # --- LIVE STATUS HEUTE (SCHÖN UNTEN PLATZIERT) ---
        #st.divider()
        heute_str = get_local_now().strftime("%Y-%m-%d")
        heutige_daten = df_personal_base[df_personal_base['Start_dt'].dt.strftime('%Y-%m-%d') == heute_str].copy()
        
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

        
        # Tab-Steuerung für den Admin
        if st.session_state.get("is_admin", False):
            tab_persoenlich, tab_admin = st.tabs(["👤 Meine Statistik", "📊 Admin-Dashboard (Erweiterte Filter)"])
        else:
            tab_persoenlich = st.container()
            tab_admin = None

        # --- REITER 1: PERSÖNLICHE STATISTIK ---
        with tab_persoenlich:
            st.subheader("📅 Meine Monats-Statistik")
            monat_wahl_user = st.selectbox("Monat wählen", auswahl_labels, index=default_idx, key="user_month_select")
            gewaehlter_monat_user = verfuegbare_monate[auswahl_labels.index(monat_wahl_user)]
            
            gefilterte_daten_user = df_personal_base[df_personal_base['Monat_Jahr'] == gewaehlter_monat_user].copy()

            if not gefilterte_daten_user.empty:
                df_projekte = gefilterte_daten_user[gefilterte_daten_user["Project"] != "🏁 FEIERABEND" if "Project" in gefilterte_daten_user else gefilterte_daten_user["Projekt"] != "🏁 FEIERABEND"].copy()
                if not df_projekte.empty:
                    df_projekte["Dauer_Min"] = pd.to_numeric(df_projekte["Dauer_Min"], errors='coerce').fillna(0.0)
                    df_projekte["Dauer_Std"] = round(df_projekte["Dauer_Min"] / 60, 2)
                    summary = df_projekte.groupby(["Projekt", "Unterprojekt"])["Dauer_Std"].sum().reset_index()
                    summary.columns = ["Projekt", "Baugruppe", "Stunden (h)"]
                    
                    st.metric(label=f"Deine Arbeitszeit im {monat_wahl_user}", value=f"{round(summary['Stunden (h)'].sum(), 2)} Std")
                    summary["Projekt & Baugruppe"] = summary["Projekt"] + " - " + summary["Baugruppe"]
                    st.bar_chart(data=summary, x="Projekt & Baugruppe", y="Stunden (h)", use_container_width=True)
                    st.dataframe(summary[["Projekt", "Baugruppe", "Stunden (h)"]], use_container_width=True, hide_index=True)
                else:
                    st.info(f"Keine Projektzeiten im {monat_wahl_user} aufgezeichnet.")
            else:
                st.info(f"Keine Einträge für den Monat {monat_wahl_user} gefunden.")




        # --- REITER 2: ADMIN DASHBOARD (NUR FÜR ADMIN) ---
        if tab_admin is not None:
            with tab_admin:
                st.subheader("🏢 Team-Auswertung mit Filterfunktion")
                monat_wahl_admin = st.selectbox("Auswertungsmonat wählen", auswahl_labels, index=default_idx, key="admin_month_select")
                gewaehlter_monat_admin = verfuegbare_monate[auswahl_labels.index(monat_wahl_admin)]
                
                # Basis-Daten für den gewählten Monat laden (ohne Feierabend)
                df_admin_base = df_global[(df_global['Monat_Jahr'] == gewaehlter_monat_admin) & (df_global["Projekt"] != "🏁 FEIERABEND")].copy()
                
                if not df_admin_base.empty:
                    df_admin_base["Dauer_Min"] = pd.to_numeric(df_admin_base["Dauer_Min"], errors='coerce').fillna(0.0)
                    df_admin_base["Dauer_Std"] = round(df_admin_base["Dauer_Min"] / 60, 2)
                    
                    # --- DYNAMISCHE FILTER UI ---
                    st.markdown("#### 🔍 Daten filtern")
                    f_col1, f_col2, f_col3 = st.columns(3)
                    
                    with f_col1:
                        mitarbeiter_opt = ["Alle"] + sorted(list(df_admin_base["Mitarbeiter"].unique()))
                        wahl_mitarbeiter = st.selectbox("Mitarbeiter", mitarbeiter_opt)
                    
                    df_temp = df_admin_base.copy()
                    if wahl_mitarbeiter != "Alle":
                        df_temp = df_temp[df_temp["Mitarbeiter"] == wahl_mitarbeiter]
                        
                    with f_col2:
                        projekt_opt = ["Alle"] + sorted(list(df_temp["Projekt"].unique()))
                        wahl_projekt = st.selectbox("Baugruppe (Projekt)", projekt_opt)
                        
                    if wahl_projekt != "Alle":
                        df_temp = df_temp[df_temp["Projekt"] == wahl_projekt]
                        
                    with f_col3:
                        unterprojekt_opt = ["Alle"] + sorted(list(df_temp["Unterprojekt"].unique()))
                        wahl_unterprojekt = st.selectbox("Unterbaugruppe", unterprojekt_opt)
                    
                    # --- FILTER ANWENDEN ---
                    df_filtered = df_admin_base.copy()
                    if wahl_mitarbeiter != "Alle":
                        df_filtered = df_filtered[df_filtered["Mitarbeiter"] == wahl_mitarbeiter]
                    if wahl_projekt != "Alle":
                        df_filtered = df_filtered[df_filtered["Projekt"] == wahl_projekt]
                    if wahl_unterprojekt != "Alle":
                        df_filtered = df_filtered[df_filtered["Unterprojekt"] == wahl_unterprojekt]
                        
                    # --- AUSWERTUNG ANZEIGEN ---
                    st.markdown("---")
                    if not df_filtered.empty:
                        ges_stunden_filtered = round(df_filtered["Dauer_Std"].sum(), 2)
                        st.metric(label="Summe geleistete Stunden (gefiltert)", value=f"{ges_stunden_filtered} Std")
                        
                        st.markdown("### 📊 Visuelle Stundenverteilung")
                        if wahl_mitarbeiter == "Alle":
                            chart_data = df_filtered.groupby("Mitarbeiter")["Dauer_Std"].sum().reset_index()
                            st.bar_chart(data=chart_data, x="Mitarbeiter", y="Dauer_Std", use_container_width=True)
                        else:
                            df_filtered["Zusammenfassung"] = df_filtered["Projekt"] + " - " + df_filtered["Unterprojekt"]
                            chart_data = df_filtered.groupby("Zusammenfassung")["Dauer_Std"].sum().reset_index()
                            st.bar_chart(data=chart_data, x="Zusammenfassung", y="Dauer_Std", use_container_width=True)
                        
                        st.markdown("### 📋 Gefilterte Einzelbuchungen")
                        table_data = df_filtered.groupby(["Mitarbeiter", "Projekt", "Unterprojekt"])["Dauer_Std"].sum().reset_index()
                        table_data.columns = ["Mitarbeiter", "Baugruppe (Projekt)", "Unterbaugruppe", "Stunden (h)"]
                        st.dataframe(table_data, use_container_width=True, hide_index=True)
                        
                        # --- NEU: EXPORT BUTTON FÜR DEN ADMIN ---
                        st.markdown("### 💾 Daten exportieren")
                        # Konvertiert die gefilterte Ansicht in ein Excel-freundliches CSV (mit UTF-8-BOM für Umlaute)
                        csv_data = table_data.to_csv(index=False, sep=";").encode("utf-8-sig")
                        
                        st.download_button(
                            label="📥 Gefilterte Auswertung als CSV (Excel) herunterladen",
                            data=csv_data,
                            file_name=f"zeiterfassung_export_{gewaehlter_monat_admin}.csv",
                            mime="text/csv",
                            use_container_width=True
                        )
                    else:
                        st.info("Keine Daten für diese spezifische Filterkombination gefunden.")
                else:
                    st.info(f"Keine Daten für den Monat {monat_wahl_admin} vorhanden.")







