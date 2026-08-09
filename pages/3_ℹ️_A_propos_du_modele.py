import json
import os
import streamlit as st
import pandas as pd

st.set_page_config(page_title="À propos du modèle", page_icon="ℹ️", layout="wide")

METRICS_PATH = os.path.join(os.path.dirname(__file__), "..", "metrics_modele.json")

st.title("ℹ️ À propos du modèle")

if not os.path.exists(METRICS_PATH):
    st.warning(
        "Le fichier 'metrics_modele.json' est introuvable à la racine du "
        "projet. Génère-le depuis R (voir save_model.R) puis copie-le ici."
    )
    st.stop()

with open(METRICS_PATH, "r", encoding="utf-8") as f:
    infos = json.load(f)

# --- Indicateurs de performance ------------------------------------------
st.subheader("📈 Performance sur le jeu de test")

col1, col2, col3, col4 = st.columns(4)
col1.metric("AUC (ROC)", f"{infos['auc']:.4f}")
col2.metric("Accuracy", f"{infos['accuracy']:.4f}")
col3.metric("Précision", f"{infos['precision']:.4f}")
col4.metric("Rappel", f"{infos['recall']:.4f}")

st.caption(
    f"Évalué sur {infos['nb_observations_test']:,} observations de test "
    f"(après entraînement sur {infos['nb_observations_train']:,} observations), "
    f"séparation 80/20."
    .replace(",", " ")
)

st.divider()

# --- Méthodologie -----------------------------------------------------------
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

# --- Meilleurs hyperparamètres retenus --------------------------------------
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

# --- Variables utilisées -----------------------------------------------------
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