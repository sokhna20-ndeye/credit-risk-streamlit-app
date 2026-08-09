import streamlit as st
from utils.model_loader import (
    predict_single,
    ModeleIntrouvableError,
    CategorieInconnueError,
)
from utils.history import add_prediction
from utils.insights import generer_observations
from utils.ui import apply_custom_style, render_header, render_footer

st.set_page_config(page_title="Prédiction", page_icon="🔮", layout="wide")
apply_custom_style()
render_header("Prédiction du statut de paiement", "Saisis les informations d'une personne pour évaluer son dossier", icon="🔮")

OPTIONS_HOME_OWNERSHIP = ["RENT", "MORTGAGE", "OWN", "OTHER"]
OPTIONS_LOAN_INTENT = [
    "PERSONAL", "EDUCATION", "MEDICAL", "VENTURE",
    "HOMEIMPROVEMENT", "DEBTCONSOLIDATION",
]
OPTIONS_DEFAULT_ON_FILE = ["N", "Y"]

COULEURS_REMARQUE = {
    "warning": ("#fff8e1", "#8a6d00", "#f0c14b", "⚠️"),
    "info": ("#e8f0fe", "#1a3d7c", "#a7c4f2", "ℹ️"),
    "ok": ("#e6f4ea", "#1e7e34", "#8fd19e", "✅"),
}

with st.form("formulaire_prediction"):
    col1, col2, col3 = st.columns(3)

    with col1:
        st.subheader("Profil")
        person_age = st.number_input("Âge", min_value=18, max_value=100, value=30, step=1)
        person_income = st.number_input("Revenu annuel (USD)", min_value=0, value=50000, step=1000)
        person_home_ownership = st.selectbox("Statut d'occupation du logement", OPTIONS_HOME_OWNERSHIP)
        person_emp_length = st.number_input("Ancienneté d'emploi (années)", min_value=0.0, max_value=60.0, value=5.0, step=0.5)

    with col2:
        st.subheader("Prêt")
        loan_intent = st.selectbox("Motif du prêt", OPTIONS_LOAN_INTENT)
        loan_amnt = st.number_input("Montant du prêt demandé (USD)", min_value=0, value=10000, step=500)
        loan_int_rate = st.number_input("Taux d'intérêt (%)", min_value=0.0, max_value=40.0, value=11.0, step=0.1)

    with col3:
        st.subheader("Historique de crédit")
        cb_person_default_on_file = st.selectbox(
            "Défaut de paiement déjà enregistré dans le passé ?",
            OPTIONS_DEFAULT_ON_FILE, help="Y = oui, N = non",
        )
        cb_person_cred_hist_length = st.number_input("Ancienneté du dossier de crédit (années)", min_value=0, max_value=60, value=5, step=1)

    submit = st.form_submit_button("🔎 Lancer l'analyse", use_container_width=True)

if submit:
    input_dict = {
        "person_age": int(person_age),
        "person_income": float(person_income),
        "person_home_ownership": person_home_ownership,
        "person_emp_length": float(person_emp_length),
        "loan_intent": loan_intent,
        "loan_int_rate": float(loan_int_rate),
        "cb_person_default_on_file": cb_person_default_on_file,
        "loan_amnt": float(loan_amnt),
        "cb_person_cred_hist_length": int(cb_person_cred_hist_length),
    }

    try:
        with st.spinner("Le modèle analyse le dossier..."):
            prediction, proba_ok, proba_defaut = predict_single(input_dict)
    except ModeleIntrouvableError:
        st.error(
            "❌ Le modèle est introuvable. Vérifie que le dossier "
            "'modele_credit_risk_spark' est bien présent à la racine du projet."
        )
        st.stop()
    except CategorieInconnueError as e:
        st.error(f"❌ {e}")
        st.stop()
    except Exception as e:
        st.error("❌ Une erreur inattendue est survenue pendant la prédiction.")
        with st.expander("Détails techniques (pour le débogage)"):
            st.code(str(e))
        st.stop()

    add_prediction(input_dict, prediction, proba_defaut)

    st.divider()

    if prediction == 0:
        st.success("## 🎉👏 Cette personne est en règle !")
        st.toast("👏 Client en règle — dossier validé", icon="👏")
        st.markdown(
            f"""
            <div style="background-color:#e6f4ea;padding:20px;border-radius:10px;border:2px solid #34a853;">
                <h3 style="color:#1e7e34;margin:0;">✅ Profil sans risque particulier détecté</h3>
                <p style="margin:5px 0 0 0;color:#1e7e34;">Probabilité d'être en règle : <b>{proba_ok*100:.1f}%</b></p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.error("## 🚨⚠️ ALERTE : Cette personne est en défaut de paiement !")
        st.markdown(
            f"""
            <div style="background-color:#fce8e6;padding:20px;border-radius:10px;border:2px solid #d93025;">
                <h3 style="color:#a50e0e;margin:0;">🚨 Risque de défaut détecté</h3>
                <p style="margin:5px 0 0 0;color:#a50e0e;">Niveau de risque de défaut : <b>{proba_defaut*100:.1f}%</b></p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.write("")
    st.subheader("📝 Points d'attention sur le profil")
    st.caption(
        "Observations sur les données saisies (indépendantes du modèle), "
        "pour aider à la lecture du dossier."
    )

    for niveau, texte in generer_observations(input_dict):
        bg, text_color, border, icon = COULEURS_REMARQUE[niveau]
        st.markdown(
            f"""
            <div style="background-color:{bg};color:{text_color};
                        border-left:4px solid {border};
                        padding:10px 14px;border-radius:6px;margin-bottom:8px;">
                {icon} {texte}
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.caption("Cette prédiction vient d'être ajoutée à l'historique visible dans le 📊 Tableau de bord.")

render_footer()