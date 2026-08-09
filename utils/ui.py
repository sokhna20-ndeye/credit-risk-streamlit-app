"""
Éléments d'interface partagés — style moderne avec dégradés, cartes à ombre
et icônes en pastille, pour une présentation professionnelle et cohérente.
"""

import streamlit as st

PRIMARY = "#123C6B"
ACCENT = "#2E86C1"
ACCENT_LIGHT = "#5DADE2"


def apply_custom_style():
    st.markdown(
        f"""
        <style>
        .hero {{
            position: relative;
            overflow: hidden;
            padding: 42px 40px;
            border-radius: 18px;
            background: linear-gradient(135deg, {PRIMARY} 0%, {ACCENT} 55%, {ACCENT_LIGHT} 100%);
            margin-bottom: 26px;
            box-shadow: 0 8px 24px rgba(18, 60, 107, 0.25);
        }}
        .hero::before {{
            content: "";
            position: absolute;
            top: -60px; right: -60px;
            width: 220px; height: 220px;
            background: rgba(255,255,255,0.08);
            border-radius: 50%;
        }}
        .hero::after {{
            content: "";
            position: absolute;
            bottom: -80px; right: 120px;
            width: 160px; height: 160px;
            background: rgba(255,255,255,0.06);
            border-radius: 50%;
        }}
        .hero h1 {{
            color: white;
            margin: 0;
            font-size: 2rem;
            font-weight: 700;
            position: relative;
            z-index: 1;
        }}
        .hero p {{
            color: #E3EEF9;
            margin: 8px 0 0 0;
            font-size: 1.02rem;
            position: relative;
            z-index: 1;
        }}

        .stat-card {{
            background: white;
            border-radius: 14px;
            padding: 18px 20px;
            box-shadow: 0 2px 10px rgba(18, 60, 107, 0.08);
            border: 1px solid #EEF2F6;
        }}
        .stat-card .stat-value {{
            font-size: 1.6rem;
            font-weight: 700;
            color: {PRIMARY};
        }}
        .stat-card .stat-label {{
            font-size: 0.82rem;
            color: #6B7A90;
            margin-top: 2px;
        }}

        .nav-card {{
            background: white;
            border-radius: 16px;
            padding: 26px 22px;
            box-shadow: 0 2px 14px rgba(18, 60, 107, 0.09);
            border: 1px solid #EEF2F6;
            transition: transform 0.15s ease, box-shadow 0.15s ease;
            height: 100%;
        }}
        .nav-card:hover {{
            transform: translateY(-4px);
            box-shadow: 0 10px 24px rgba(18, 60, 107, 0.16);
        }}
        .nav-icon {{
            width: 52px; height: 52px;
            border-radius: 14px;
            background: linear-gradient(135deg, {PRIMARY}, {ACCENT});
            display: flex; align-items: center; justify-content: center;
            font-size: 1.5rem;
            margin-bottom: 14px;
        }}
        .nav-card h4 {{
            margin: 0 0 6px 0;
            color: {PRIMARY};
            font-size: 1.08rem;
        }}
        .nav-card p {{
            color: #6B7A90;
            font-size: 0.88rem;
            margin: 0;
        }}

        .app-footer {{
            margin-top: 40px;
            padding-top: 12px;
            border-top: 1px solid #EEF2F6;
            text-align: center;
            color: #9AA6B8;
            font-size: 0.8rem;
        }}
        .app-footer a {{
            color: {ACCENT};
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_header(title: str, subtitle: str, icon: str = "💳"):
    st.markdown(
        f"""
        <div class="hero">
            <h1>{icon} {title}</h1>
            <p>{subtitle}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_footer():
    st.markdown(
        """
        <div class="app-footer">
            <b>Sokhna B. Diagne</b> — Licence 3, Statistique et Informatique Décisionnelle, EMIA Dakar<br>
            Données stockées localement, aucune transmission externe · Licence MIT ·
            <a href="https://github.com/sokhna20-ndeye/credit-risk-streamlit-app" target="_blank">Code source</a>
        </div>
        """,
        unsafe_allow_html=True,
    )