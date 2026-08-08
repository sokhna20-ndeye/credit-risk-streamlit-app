import streamlit as st
import plotly.express as px
from utils.history import load_history, clear_history

st.set_page_config(page_title="Tableau de bord", page_icon="📊", layout="wide")

st.title("📊 Tableau de bord des prédictions")

history = load_history()

if history.empty:
    st.info(
        "Aucune prédiction n'a encore été effectuée. Rends-toi sur la page "
        "🔮 Prédiction pour analyser un premier dossier."
    )
else:
    total = len(history)
    nb_ok = int((history["prediction"] == 0).sum())
    nb_defaut = int((history["prediction"] == 1).sum())
    pct_ok = nb_ok / total * 100
    pct_defaut = nb_defaut / total * 100

    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("👥 Total analysé", total)
    col2.metric("🟢 En règle", nb_ok)
    col3.metric("🔴 En défaut", nb_defaut)
    col4.metric("🟢 % En règle", f"{pct_ok:.1f}%")
    col5.metric("🔴 % En défaut", f"{pct_defaut:.1f}%")

    st.divider()

    col_chart, col_hist = st.columns([1, 2])

    with col_chart:
        st.subheader("Répartition des statuts")
        repartition = history["statut"].value_counts().reset_index()
        repartition.columns = ["statut", "nombre"]
        fig = px.pie(
            repartition, names="statut", values="nombre", color="statut",
            color_discrete_map={"En règle": "#34a853", "En défaut": "#d93025"},
            hole=0.45,
        )
        fig.update_traces(textinfo="percent+label")
        st.plotly_chart(fig, use_container_width=True)

    with col_hist:
        st.subheader("Historique des prédictions")
        st.dataframe(
            history.sort_values("horodatage", ascending=False),
            use_container_width=True,
            height=380,
        )

    st.divider()
    if st.button("🗑️ Réinitialiser l'historique"):
        clear_history()
        st.rerun()