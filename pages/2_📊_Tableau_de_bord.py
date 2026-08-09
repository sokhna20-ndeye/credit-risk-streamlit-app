import time
from datetime import datetime
import streamlit as st
import pandas as pd
import plotly.express as px
from utils.history import load_history, clear_history
from utils.report import generer_rapport_pdf
from utils.ui import apply_custom_style, render_header, render_footer

st.set_page_config(page_title="Tableau de bord", page_icon="📊", layout="wide")
apply_custom_style()
render_header("Tableau de bord des prédictions", "Suivi en temps réel des analyses effectuées", icon="📊")

# --- Actualisation automatique ------------------------------------------------
col_refresh, col_status = st.columns([1, 3])
with col_refresh:
    auto_refresh = st.toggle("🔴 Actualisation automatique")
with col_status:
    if auto_refresh:
        st.caption(f"Actualisé automatiquement toutes les 5 secondes — dernière actualisation : {datetime.now().strftime('%H:%M:%S')}")

history = load_history()

if history.empty:
    st.info(
        "Aucune prédiction n'a encore été effectuée. Rends-toi sur la page "
        "🔮 Prédiction pour analyser un premier dossier."
    )
    render_footer()
    if auto_refresh:
        time.sleep(5)
        st.rerun()
    st.stop()

total = len(history)
nb_ok = int((history["prediction"] == 0).sum())
nb_defaut = int((history["prediction"] == 1).sum())
pct_defaut = nb_defaut / total * 100
montant_total = history["loan_amnt"].sum()
proba_moyenne = history["proba_defaut"].mean() * 100
age_moyen = history["person_age"].mean()

# --- Cartes de métriques -----------------------------------------------------
stats = [
    ("👥", str(total), "Total analysé"),
    ("🔴", f"{pct_defaut:.0f}%", "Taux de défaut"),
    ("💰", f"{montant_total:,.0f} $".replace(",", " "), "Montant total analysé"),
    ("⚖️", f"{proba_moyenne:.0f}%", "Risque moyen estimé"),
    ("🎂", f"{age_moyen:.0f} ans", "Âge moyen des dossiers"),
]
cols = st.columns(5)
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

# --- Répartition + statut par type de logement --------------------------------
col_pie, col_box = st.columns(2)

with col_pie:
    st.subheader("Répartition des statuts")
    repartition = history["statut"].value_counts().reset_index()
    repartition.columns = ["statut", "nombre"]
    fig_pie = px.pie(
        repartition, names="statut", values="nombre", color="statut",
        color_discrete_map={"En règle": "#34a853", "En défaut": "#d93025"},
        hole=0.5,
    )
    fig_pie.update_traces(textinfo="percent+label")
    fig_pie.update_layout(showlegend=False, margin=dict(t=10, b=10, l=10, r=10))
    st.plotly_chart(fig_pie, use_container_width=True)

with col_box:
    st.subheader("Statut par type de logement")
    par_logement = (
        history.groupby(["person_home_ownership", "statut"])
        .size()
        .reset_index(name="nombre")
    )
    fig_logement = px.bar(
        par_logement, x="person_home_ownership", y="nombre", color="statut",
        color_discrete_map={"En règle": "#34a853", "En défaut": "#d93025"},
        barmode="group",
        labels={"person_home_ownership": "Statut de logement", "nombre": "Nombre de dossiers"},
    )
    fig_logement.update_layout(margin=dict(t=10, b=10, l=10, r=10), legend_title_text="")
    st.plotly_chart(fig_logement, use_container_width=True)

st.divider()

# --- Historique filtrable + export -------------------------------------------
st.subheader("Historique des prédictions")

col_f1, col_f2, col_f3 = st.columns(3)
with col_f1:
    filtre_statut = st.multiselect("Statut", options=history["statut"].unique().tolist())
with col_f2:
    filtre_intent = st.multiselect("Motif du prêt", options=sorted(history["loan_intent"].unique().tolist()))
with col_f3:
    filtre_logement = st.multiselect("Statut de logement", options=sorted(history["person_home_ownership"].unique().tolist()))

historique_filtre = history.copy()
if filtre_statut:
    historique_filtre = historique_filtre[historique_filtre["statut"].isin(filtre_statut)]
if filtre_intent:
    historique_filtre = historique_filtre[historique_filtre["loan_intent"].isin(filtre_intent)]
if filtre_logement:
    historique_filtre = historique_filtre[historique_filtre["person_home_ownership"].isin(filtre_logement)]

st.dataframe(
    historique_filtre.sort_values("horodatage", ascending=False),
    use_container_width=True,
    height=350,
)

col_export, col_reset = st.columns([1, 1])
with col_export:
    st.download_button(
        "⬇️ Exporter en CSV",
        data=historique_filtre.to_csv(index=False).encode("utf-8"),
        file_name="historique_predictions.csv",
        mime="text/csv",
        use_container_width=True,
    )
with col_reset:
    if st.button("🗑️ Réinitialiser l'historique", use_container_width=True):
        clear_history()
        st.rerun()

st.divider()

# --- Rapport ---------------------------------------------------------------
st.subheader("📄 Rapport")
st.caption("Génère un rapport avec les indicateurs clés, la répartition par motif et le détail des dossiers.")

repartition_intent = (
    history.groupby("loan_intent")["prediction"]
    .agg(nb_dossiers="count", nb_defauts="sum")
    .reset_index()
)
repartition_intent["taux_defaut_pct"] = (
    repartition_intent["nb_defauts"] / repartition_intent["nb_dossiers"] * 100
).round(1)

rapport_html = f"""
<html>
<head>
<meta charset="utf-8">
<style>
    body {{ font-family: Arial, sans-serif; color: #1C1C1C; padding: 30px; }}
    h1 {{ color: #1B4F72; }}
    h2 {{ color: #2E86C1; border-bottom: 1px solid #ddd; padding-bottom: 6px; }}
    table {{ border-collapse: collapse; width: 100%; margin: 12px 0; }}
    th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
    th {{ background-color: #F5F7FA; }}
    .metric {{ display: inline-block; margin-right: 30px; }}
    .metric .value {{ font-size: 1.4rem; font-weight: bold; color: #1B4F72; }}
</style>
</head>
<body>
    <h1>Rapport d'analyse — Scoring Crédit</h1>
    <p>Généré le {datetime.now().strftime('%d/%m/%Y à %H:%M')}</p>

    <h2>Indicateurs clés</h2>
    <div class="metric"><div class="value">{total}</div>Dossiers analysés</div>
    <div class="metric"><div class="value">{nb_ok}</div>En règle</div>
    <div class="metric"><div class="value">{nb_defaut}</div>En défaut</div>
    <div class="metric"><div class="value">{pct_defaut:.1f}%</div>Taux de défaut</div>
    <div class="metric"><div class="value">{montant_total:,.0f} $</div>Montant total analysé</div>

    <h2>Répartition par motif de prêt</h2>
    {repartition_intent.to_html(index=False)}

    <h2>Détail des analyses</h2>
    {history.sort_values('horodatage', ascending=False).to_html(index=False)}
</body>
</html>
"""

col_html, col_pdf = st.columns(2)
with col_html:
    st.download_button(
        "🌐 Rapport HTML (complet, imprimable en PDF)",
        data=rapport_html.encode("utf-8"),
        file_name=f"rapport_credit_{datetime.now().strftime('%Y%m%d_%H%M')}.html",
        mime="text/html",
        use_container_width=True,
    )
with col_pdf:
    pdf_bytes = generer_rapport_pdf(history)
    st.download_button(
        "📄 Rapport PDF (direct)",
        data=pdf_bytes,
        file_name=f"rapport_credit_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf",
        mime="application/pdf",
        use_container_width=True,
    )

render_footer()

if auto_refresh:
    time.sleep(5)
    st.rerun()