"""
Génère des observations objectives sur le profil saisi (indépendantes du
modèle) pour accompagner chaque prédiction.
"""


def generer_observations(input_dict: dict) -> list[tuple[str, str]]:
    """Retourne une liste de (niveau, texte). niveau : 'warning' | 'info' | 'ok'."""
    remarques = []

    revenu = input_dict.get("person_income", 0)
    montant = input_dict.get("loan_amnt", 0)
    if revenu > 0:
        ratio = montant / revenu
        if ratio > 0.4:
            remarques.append(("warning", f"Le prêt représente {ratio*100:.0f}% du revenu annuel (seuil élevé)."))
        elif ratio > 0.2:
            remarques.append(("info", f"Le prêt représente {ratio*100:.0f}% du revenu annuel."))

    if input_dict.get("loan_int_rate", 0) > 15:
        remarques.append(("warning", "Taux d'intérêt élevé (supérieur à 15%)."))

    if input_dict.get("cb_person_default_on_file") == "Y":
        remarques.append(("warning", "Antécédent de défaut de paiement déjà enregistré."))

    if input_dict.get("person_emp_length", 0) < 1:
        remarques.append(("info", "Ancienneté d'emploi très courte (moins d'1 an)."))

    if input_dict.get("cb_person_cred_hist_length", 0) < 2:
        remarques.append(("info", "Historique de crédit court (moins de 2 ans)."))

    if not remarques:
        remarques.append(("ok", "Aucun facteur de vigilance particulier identifié dans le profil saisi."))

    return remarques