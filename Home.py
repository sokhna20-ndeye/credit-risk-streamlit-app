import streamlit as st

st.set_page_config(
    page_title="Prédiction de Défaut de Paiement",
    page_icon="💳",
    layout="wide",
)

st.title("💳 Application de Prédiction de Défaut de Paiement")

st.markdown(
    """
Bienvenue dans l'application de démonstration du modèle de Machine Learning
(Random Forest, entraîné avec Spark ML / sparklyr) permettant de prédire si
une personne est **en règle** ou **en défaut de paiement** sur un prêt.

Utilise le menu à gauche pour naviguer :

- **🔮 Prédiction** — saisir les informations d'une personne et obtenir la
  prédiction du modèle.
- **📊 Tableau de bord** — suivre les statistiques et l'historique de toutes
  les prédictions effectuées durant la session de démonstration.
"""
)

st.info(
    "Le modèle utilisé est celui déjà entraîné et validé (validation "
    "croisée) dans le notebook R — il n'est ni réentraîné, ni modifié par "
    "cette application."
)