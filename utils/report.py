"""
Génération d'un rapport PDF à partir de l'historique des prédictions.
"""

from datetime import datetime
from fpdf import FPDF
import pandas as pd


def _safe(texte: str) -> str:
    """Adapte le texte à l'encodage supporté par les polices de base du PDF."""
    return str(texte).encode("latin-1", "replace").decode("latin-1")


def generer_rapport_pdf(history: pd.DataFrame) -> bytes:
    total = len(history)
    nb_ok = int((history["prediction"] == 0).sum())
    nb_defaut = int((history["prediction"] == 1).sum())
    pct_defaut = nb_defaut / total * 100
    montant_total = history["loan_amnt"].sum()

    pdf = FPDF()
    pdf.add_page()

    # --- En-tête -------------------------------------------------------------
    pdf.set_fill_color(27, 79, 114)
    pdf.rect(0, 0, 210, 28, style="F")
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Helvetica", "B", 18)
    pdf.set_xy(10, 8)
    pdf.cell(0, 10, _safe("Rapport d'analyse - Scoring Credit"), ln=True)
    pdf.set_font("Helvetica", "", 10)
    pdf.set_xy(10, 18)
    pdf.cell(0, 6, _safe(f"Genere le {datetime.now().strftime('%d/%m/%Y a %H:%M')}"))

    pdf.set_text_color(0, 0, 0)
    pdf.ln(24)

    # --- Indicateurs clés ------------------------------------------------------
    pdf.set_font("Helvetica", "B", 13)
    pdf.cell(0, 10, _safe("Indicateurs cles"), ln=True)
    pdf.set_font("Helvetica", "", 11)

    indicateurs = [
        ("Dossiers analyses", str(total)),
        ("En regle", str(nb_ok)),
        ("En defaut", str(nb_defaut)),
        ("Taux de defaut", f"{pct_defaut:.1f} %"),
        ("Montant total analyse", f"{montant_total:,.0f} $".replace(",", " ")),
    ]
    for label, valeur in indicateurs:
        pdf.cell(70, 8, _safe(label), border=1)
        pdf.cell(0, 8, _safe(valeur), border=1, ln=True)

    pdf.ln(6)

    # --- Répartition par motif de prêt -----------------------------------------
    pdf.set_font("Helvetica", "B", 13)
    pdf.cell(0, 10, _safe("Repartition par motif de pret"), ln=True)

    par_motif = (
        history.groupby("loan_intent")["prediction"]
        .agg(nb_dossiers="count", nb_defauts="sum")
        .reset_index()
    )
    par_motif["taux_defaut_pct"] = (par_motif["nb_defauts"] / par_motif["nb_dossiers"] * 100).round(1)

    pdf.set_font("Helvetica", "B", 10)
    pdf.set_fill_color(245, 247, 250)
    pdf.cell(60, 8, _safe("Motif"), border=1, fill=True)
    pdf.cell(40, 8, _safe("Dossiers"), border=1, fill=True)
    pdf.cell(40, 8, _safe("Defauts"), border=1, fill=True)
    pdf.cell(40, 8, _safe("Taux (%)"), border=1, fill=True, ln=True)

    pdf.set_font("Helvetica", "", 10)
    for _, row in par_motif.iterrows():
        pdf.cell(60, 8, _safe(row["loan_intent"]), border=1)
        pdf.cell(40, 8, _safe(str(row["nb_dossiers"])), border=1)
        pdf.cell(40, 8, _safe(str(int(row["nb_defauts"]))), border=1)
        pdf.cell(40, 8, _safe(f"{row['taux_defaut_pct']}"), border=1, ln=True)

    pdf.ln(6)

    # --- Détail des dossiers -----------------------------------------------------
    pdf.set_font("Helvetica", "B", 13)
    pdf.cell(0, 10, _safe("Detail des dossiers analyses"), ln=True)

    colonnes = ["horodatage", "person_age", "person_income", "loan_amnt", "statut"]
    entetes = ["Date", "Age", "Revenu", "Montant pret", "Statut"]
    largeurs = [40, 20, 35, 35, 35]

    pdf.set_font("Helvetica", "B", 9)
    pdf.set_fill_color(245, 247, 250)
    for entete, largeur in zip(entetes, largeurs):
        pdf.cell(largeur, 8, _safe(entete), border=1, fill=True)
    pdf.ln()

    pdf.set_font("Helvetica", "", 9)
    for _, row in history.sort_values("horodatage", ascending=False).iterrows():
        for col, largeur in zip(colonnes, largeurs):
            pdf.cell(largeur, 7, _safe(row[col]), border=1)
        pdf.ln()
        if pdf.get_y() > 270:
            pdf.add_page()

    return bytes(pdf.output())