import streamlit as st
import pandas as pd
from utils.db_handler import get_user_analyses, get_champs_by_user, get_cultures_by_champ, get_analyses_by_culture

def check_propagation_alert(analyses):
    """
    Vérifie si une maladie apparaît plusieurs fois avec une confiance croissante pour une même culture.
    analyses structure: (id, user, culture, img, pred, conf, stat, date) -> pred = 4, conf = 5
    """
    if len(analyses) < 2:
        return None
    from collections import Counter
    diseases = [a for a in analyses if "healthy" not in str(a[4]).lower()]
    disease_counts = Counter(a[4] for a in diseases)
    for disease, count in disease_counts.items():
        if count >= 2:
            subset = [a for a in diseases if a[4] == disease]
            # Trier par date
            subset = sorted(subset, key=lambda x: x[7])
            confidences = [float(a[5]) for a in subset]
            if confidences[-1] > confidences[0]:
                return {"disease": disease, "count": count, "trend": "croissante",
                        "first": f"{confidences[0]*100:.1f}%", "last": f"{confidences[-1]*100:.1f}%"}
    return None

def show():
  st.markdown("<h1 style='color: #1e293b; margin-bottom: 1.5rem;'>Mes Analyses & Suivi 📋</h1>", unsafe_allow_html=True)
  st.markdown("<p style='color: #64748b; font-size: 1.1rem; margin-bottom: 2rem;'>Vue détaillée et suivi temporel de vos cultures.</p>", unsafe_allow_html=True)
  
  user_id = st.session_state['user']['id']
  
  tab_culture, tab_global = st.tabs(["📈 Suivi par Culture", "🌍 Vue Globale"])
  
  with tab_culture:
      champs = get_champs_by_user(user_id)
      if champs:
          champ_dict = {f"{c[1]} - {c[2]}": c[0] for c in champs}
          selected_champ = st.selectbox("Sélectionnez un champ :", list(champ_dict.keys()), key="analyse_champ_sel")
          
          cultures = get_cultures_by_champ(champ_dict[selected_champ])
          if cultures:
              culture_dict = {f"{c[1]} ({c[2]})": c[0] for c in cultures}
              selected_culture = st.selectbox("Sélectionnez la culture :", list(culture_dict.keys()), key="analyse_culture_sel")
              culture_id = culture_dict[selected_culture]
              
              cult_analyses = get_analyses_by_culture(culture_id)
              if cult_analyses:
                  # Trier par date pour le graphe
                  cult_analyses = sorted(cult_analyses, key=lambda x: x[7])
                  
                  # Alerte Propagation
                  alert = check_propagation_alert(cult_analyses)
                  if alert:
                      st.error(
                          f"🚨 **Alerte propagation** : La maladie '{alert['disease'].replace('_', ' ')}' a été détectée {alert['count']} fois "
                          f"avec une certitude {alert['trend']} ({alert['first']} ➡️ {alert['last']}). "
                          f"Une intervention rapide est recommandée !"
                      )
                  
                  # Graphe d'évolution
                  diseased = [a for a in cult_analyses if "healthy" not in str(a[4]).lower()]
                  if len(diseased) > 0:
                      st.markdown("<h3 style='color: #334155; margin-top: 1rem;'>Évolution des risques (Maladies)</h3>", unsafe_allow_html=True)
                      # Préparation des données pour le graphe (Axe X: Date, Axe Y: Confiance %)
                      chart_data = {
                          a[7]: float(a[5])*100 for a in diseased
                      }
                      st.line_chart(pd.Series(chart_data, name="Confiance IA (%)"))
                  else:
                      st.success("Toutes les analyses pour cette culture indiquent une plante saine ! 🌱")

                  # Tableau détaillé
                  st.markdown("<h4 style='color: #334155; margin-top: 2rem;'>Historique détaillé</h4>", unsafe_allow_html=True)
                  df_c = pd.DataFrame(cult_analyses, columns=["ID", "Utilisateur ID", "Culture ID", "Image", "Prédiction", "Confiance", "Statut", "Date"])
                  df_c = df_c.drop(columns=["ID", "Utilisateur ID", "Culture ID"])
                  df_c['Confiance'] = df_c['Confiance'].apply(lambda x: f"{float(x)*100:.2f}%" if pd.notnull(x) else "N/A")
                  st.dataframe(df_c, hide_index=True, use_container_width=True)
                  
              else:
                  st.info("ℹ️ Aucune analyse pour cette culture. Effectuez un diagnostic dans l'onglet 'Reconnaissance' et associez-le à cette culture.")
          else:
              st.info("Aucune culture enregistrée dans ce champ.")
      else:
          st.info("Vous n'avez pas encore de champs créés. Rendez-vous dans 'Mes Champs'.")

  with tab_global:
      with st.container(border=True):
          analyses = get_user_analyses(user_id)
          if analyses:
            df = pd.DataFrame(analyses, columns=["ID", "Utilisateur ID", "Culture ID", "Image", "Prédiction", "Confiance", "Statut", "Date d'Analyse"])
            df = df.drop(columns=["ID", "Utilisateur ID", "Culture ID"])
            df['Confiance'] = df['Confiance'].apply(lambda x: f"{float(x)*100:.2f}%" if pd.notnull(x) else "N/A")
            st.dataframe(df, hide_index=True, use_container_width=True)
          else:
            st.info("Aucune analyse trouvée pour cet utilisateur.")