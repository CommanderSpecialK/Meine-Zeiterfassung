import streamlit as st
import pandas as pd

def render_auswertungen(df_global, current_user, auswahl_labels, verfuegbare_monate, default_idx, monats_namen):
    """Verwaltet die Tabs für persönliche Statistiken und das Admin-Dashboard."""
    
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
        
        df_personal = df_global[df_global['Mitarbeiter'] == current_user].copy()
        gefilterte_daten_user = df_personal[df_personal['Monat_Jahr'] == gewaehlter_monat_user].copy()

        if not gefilterte_daten_user.empty:
            df_projekte = gefilterte_daten_user[gefilterte_daten_user["Projekt"] != "🏁 FEIERABEND"].copy()
            if not df_projekte.empty:
                df_projekte["Dauer_Min"] = pd.to_numeric(df_projekte["Dauer_Min"], errors='coerce').fillna(0.0)
                df_projekte["Dauer_Std"] = round(df_projekte["Dauer_Min"] / 60, 2)
                summary = df_projekte.groupby(["Projekt", "Unterprojekt"])["Dauer_Std"].sum().reset_index()
                summary.columns = ["Projekt", "Baugruppe", "Stunden (h)"]
                
                st.metric(label=f"Deine Netto-Arbeitszeit im {monat_wahl_user} (ohne Pause)", 
                          value=f"{round(summary[summary['Projekt'] != 'Pause']['Stunden (h)'].sum(), 2)} Std")
                
                summary["Projekt & Baugruppe"] = summary["Projekt"] + " - " + summary["Unterprojekt"]
                st.bar_chart(data=summary, x="Projekt & Baugruppe", y="Stunden (h)", use_container_width=True)
                st.dataframe(summary[["Projekt", "Baugruppe", "Stunden (h)"]], use_container_width=True, hide_index=True)
            else:
                st.info(f"Keine Projektzeiten im {monat_wahl_user} aufgezeichnet.")
        else:
            st.info(f"Keine Einträge für den Monat {monat_wahl_user} gefunden.")

    # --- REITER 2: ADMIN DASHBOARD (NUR ADMIN) ---
    if tab_admin is not None:
        with tab_admin:
            st.subheader("🏢 Team-Auswertung mit Pausen-Korrektur")
            monat_wahl_admin = st.selectbox("Auswertungsmonat wählen", auswahl_labels, index=default_idx, key="admin_month_select")
            gewaehlter_monat_admin = verfuegbare_monate[auswahl_labels.index(monat_wahl_admin)]
            
            df_admin_base = df_global[(df_global['Monat_Jahr'] == gewaehlter_monat_admin) & (df_global["Projekt"] != "🏁 FEIERABEND")].copy()
            
            if not df_admin_base.empty:
                df_admin_base["Dauer_Min"] = pd.to_numeric(df_admin_base["Dauer_Min"], errors='coerce').fillna(0.0)
                df_admin_base["Dauer_Std"] = round(df_admin_base["Dauer_Min"] / 60, 2)
                
                # FILTER UI
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
                
                # FILTER ANWENDEN
                df_filtered = df_admin_base.copy()
                if wahl_mitarbeiter != "Alle":
                    df_filtered = df_filtered[df_filtered["Mitarbeiter"] == wahl_mitarbeiter]
                if wahl_projekt != "Alle":
                    df_filtered = df_filtered[df_filtered["Projekt"] == wahl_projekt]
                if wahl_unterprojekt != "Alle":
                    df_filtered = df_filtered[df_filtered["Unterprojekt"] == wahl_unterprojekt]
                    
                st.markdown("---")
                if not df_filtered.empty:
                    df_arbeit = df_filtered[df_filtered["Projekt"] != "Pause"]
                    df_pause = df_filtered[df_filtered["Projekt"] == "Pause"]
                    
                    netto_std = round(df_arbeit["Dauer_Std"].sum(), 2)
                    pausen_std = round(df_pause["Dauer_Std"].sum(), 2)
                    
                    m1, m2 = st.columns(2)
                    with m1:
                        st.metric(label="Reine Netto-Arbeitszeit", value=f"{netto_std} Std")
                    with m2:
                        st.metric(label="Gesamte Pausenzeit", value=f"{pausen_std} Std")
                    
                    st.markdown("### 📋 Gefilterte Einzelbuchungen (inkl. Kommentare)")
                    table_data = df_filtered.copy()
                    table_data = table_data[["Mitarbeiter", "Projekt", "Unterprojekt", "Dauer_Std", "Kommentar"]]
                    table_data.columns = ["Mitarbeiter", "Projekt", "Unterbaugruppe", "Stunden (h)", "Mitarbeiter-Notiz"]
                    st.dataframe(table_data, use_container_width=True, hide_index=True)
                    
                    st.markdown("### 💾 Daten exportieren")
                    csv_data = table_data.to_csv(index=False, sep=";").encode("utf-8-sig")
                    st.download_button(
                        label="📥 Gefilterte Auswertung inkl. Kommentare als CSV herunterladen",
                        data=csv_data,
                        file_name=f"zeiterfassung_{gewaehlter_monat_admin}.csv",
                        mime="text/csv",
                        use_container_width=True
                    )
                else:
                    st.info("Keine Daten für diese spezifische Filterkombination gefunden.")
            else:
                st.info(f"Keine Daten für den Monat {monat_wahl_admin} vorhanden.")
