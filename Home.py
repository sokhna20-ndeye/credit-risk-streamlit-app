import json
import os
import streamlit as st
from utils.ui import apply_custom_style, render_header, render_footer

st.set_page_config(
    page_title="Prédiction de Défaut de Paiement",
    page_icon="💳",
    layout="wide",
)

apply_custom_style()

render_header(
    "Prédiction de Défaut de Paiement",
    "Scoring crédit basé sur un modèle Random Forest (Spark ML)",
)

st.markdown(
    "Cette application permet d'analyser un dossier de crédit et de "
    "prédire si une personne est **en règle** ou **en défaut de paiement**, "
    "à partir d'un modèle déjà entraîné et validé."
)

st.write("")

METRICS_PATH = os.path.join(os.path.dirname(__file__), "metrics_modele.json")

if os.path.exists(METRICS_PATH):
    with open(METRICS_PATH, "r", encoding="utf-8") as f:
        infos = json.load(f)

    total_dossiers = infos["nb_observations_train"] + infos["nb_observations_test"]
    stats = [
        ("🎯", f"{infos['auc']:.3f}", "AUC (ROC)"),
        ("✅", f"{infos['accuracy']:.1%}", "Accuracy"),
        ("🔁", f"{infos['nb_folds_validation_croisee']} folds", "Validation croisée"),
        ("📁", f"{total_dossiers:,}".replace(",", " "), "Dossiers analysés"),
    ]

    cols = st.columns(4)
    for col, (icon, value, label) in zip(cols, stats):
        with col:
            st.markdown(
                f"""
                <div class="stat-card">
                    <div>{icon} <span class="stat-value">{value}</span></div>
                    <div class="stat-label">{label}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

st.write("")
st.write("")

nav_items = [
    ("🔮", "Prédiction", "Analyser un nouveau dossier de crédit", "pages/1_🔮_Prediction.py"),
    ("📊", "Tableau de bord", "Suivre les prédictions effectuées", "pages/2_📊_Tableau_de_bord.py"),
    ("ℹ️", "À propos du modèle", "Méthodologie et performance", "pages/3_ℹ️_A_propos_du_modele.py"),
]

cols = st.columns(3)
for col, (icon, title, desc, page) in zip(cols, nav_items):
    with col:
        st.markdown(
            f"""
            <div class="nav-card">
                <div class="nav-icon">{icon}</div>
                <h4>{title}</h4>
                <p>{desc}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.write("")
        st.page_link(page, label="Ouvrir →", use_container_width=True)

render_footer()