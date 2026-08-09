import json
import os
import streamlit as st
import pandas as pd
import plotly.express as px
from utils.ui import apply_custom_style, render_header, render_footer

st.set_page_config(page_title="À propos du modèle", page_icon="ℹ️", layout="wide")
apply_custom_style()
render_header("À propos du modèle", "Méthodologie, hyperparamètres et performance", icon="ℹ️")

METRICS_PATH = os.path.join(os.path.dirname(__file__), "..", "metrics_modele.json")

if not os.path.exists(METRICS_PATH):
    st.warning(
        "Le fichier 'metrics_modele.json' est introuvable à la racine du "
        "projet. Génère-le depuis R (voir save_model.R) puis copie-le ici."
    )
    st.stop()

with open(METRICS_PATH, "r", encoding="utf-8") as f:
    infos = json.load(f)

st.subheader("📈 Performance sur le jeu de test")

col1, col2, col3, col4 = st.columns(4)
col1.metric("AUC (ROC)", f"{infos['auc']:.4f}")
col2.metric("Accuracy", f"{infos['accuracy']:.4f}")
col3.metric("Précision", f"{infos['precision']:.4f}")
col4.metric("Rappel", f"{infos['recall']:.4f}")

st.caption(
    f"Évalué sur {infos['nb_observations_test']:,} observations de test "
    f"(après entraînement sur {infos['nb_observations_train']:,} observations), "
    f"séparation 80/20.".replace(",", " ")
)

st.divider()

st.subheader("🧪 Méthodologie")

st.markdown(
    f"""
**Algorithme :** {infos['algorithme']}

**Validation :** validation croisée à **{infos['nb_folds_validation_croisee']} folds**,
avec recherche sur grille des hyperparamètres suivants :
- Nombre d'arbres (`num_trees`) : 20, 50, 100
- Profondeur maximale (`max_depth`) : 3, 5, 10
- Critère d'impureté (`impurity`) : entropy, gini

**Étapes du pipeline de prétraitement (Spark ML) :**
1. Imputation des valeurs manquantes par la **médiane** (`person_emp_length`, `loan_int_rate`)
2. Indexation puis encodage one-hot des variables catégorielles
   (`person_home_ownership`, `loan_intent`, `cb_person_default_on_file`)
3. Assemblage de toutes les variables explicatives en un vecteur de features
4. Standardisation des features (`StandardScaler`)
5. Classification par **Random Forest**
"""
)

st.divider()

st.subheader("🏆 Meilleurs hyperparamètres retenus (validation croisée)")

hp = infos["meilleurs_hyperparametres"]
hp_df = pd.DataFrame(
    {
        "Hyperparamètre": ["Nombre d'arbres", "Profondeur maximale", "Critère d'impureté", "AUC (validation)"],
        "Valeur": [hp.get("num_trees_1"), hp.get("max_depth_1"), hp.get("impurity_1"), f"{hp.get('areaUnderROC'):.4f}"],
    }
)
st.table(hp_df)

st.divider()

st.subheader("🧬 Variables utilisées par le modèle")

col_features, col_target = st.columns([2, 1])
with col_features:
    st.markdown("**Variables explicatives :**")
    for var in infos["variables_utilisees"]:
        st.markdown(f"- `{var}`")
with col_target:
    st.markdown("**Variable cible :**")
    st.markdown(f"- `{infos['variable_cible']}` (0 = en règle, 1 = en défaut)")

st.caption(
    "Le modèle est entraîné et validé indépendamment de cette application "
    "(voir le notebook R d'entraînement) ; l'application se limite au "
    "déploiement, à l'interface et au suivi des prédictions."
)

st.divider()

st.subheader("🧬 Importance des variables")
st.caption(
    "Contribution de chaque variable aux décisions du modèle (calculée "
    "directement à partir du Random Forest entraîné, via "
    "ml_feature_importances)."
)

IMPORTANCES_PATH = os.path.join(os.path.dirname(__file__), "..", "importances_variables.json")

if os.path.exists(IMPORTANCES_PATH):
    with open(IMPORTANCES_PATH, "r", encoding="utf-8") as f:
        importances = json.load(f)

    df_imp = pd.DataFrame(importances).sort_values("importance", ascending=True)

    fig_imp = px.bar(
        df_imp, x="importance", y="variable", orientation="h",
        labels={"importance": "Importance relative", "variable": ""},
        text="importance",
    )
    fig_imp.update_traces(
        marker_color="#2E86C1",
        texttemplate="%{text:.1%}",
        textposition="outside",
    )
    fig_imp.update_layout(margin=dict(t=10, b=10, l=10, r=10))
    st.plotly_chart(fig_imp, use_container_width=True)
else:
    st.info("Fichier 'importances_variables.json' introuvable à la racine du projet.")

render_footer()