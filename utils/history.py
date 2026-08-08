import os
import pandas as pd
from datetime import datetime

HISTORY_PATH = os.path.join(
    os.path.dirname(__file__), "..", "data", "predictions_history.csv"
)

COLUMNS = [
    "horodatage",
    "person_age",
    "person_income",
    "person_home_ownership",
    "person_emp_length",
    "loan_intent",
    "loan_int_rate",
    "cb_person_default_on_file",
    "loan_amnt",
    "cb_person_cred_hist_length",
    "prediction",
    "statut",
    "proba_defaut",
]


def init_history():
    os.makedirs(os.path.dirname(HISTORY_PATH), exist_ok=True)
    if not os.path.exists(HISTORY_PATH):
        pd.DataFrame(columns=COLUMNS).to_csv(HISTORY_PATH, index=False)


def add_prediction(input_dict: dict, prediction: int, proba_defaut: float):
    """Ajoute une prédiction à l'historique et le sauvegarde sur disque."""
    init_history()
    record = {
        "horodatage": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        **input_dict,
        "prediction": prediction,
        "statut": "En règle" if prediction == 0 else "En défaut",
        "proba_defaut": round(proba_defaut, 4),
    }
    df = pd.read_csv(HISTORY_PATH)
    df = pd.concat([df, pd.DataFrame([record])], ignore_index=True)
    df.to_csv(HISTORY_PATH, index=False)


def load_history() -> pd.DataFrame:
    init_history()
    return pd.read_csv(HISTORY_PATH)


def clear_history():
    init_history()
    pd.DataFrame(columns=COLUMNS).to_csv(HISTORY_PATH, index=False)