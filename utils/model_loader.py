"""
Chargement du pipeline Spark ML déjà entraîné (Random Forest issu de la
validation croisée) et fonction de prédiction pour l'application Streamlit.

Ce module ne réentraîne rien et ne modifie pas la logique du modèle. Il se
contente de charger le CrossValidatorModel exporté par save_model.R (dossier
modele_credit_risk_spark/) et d'appeler model.transform() dessus, exactement
comme le ferait ml_predict() côté R.
"""

import os
import streamlit as st
from pyspark.sql import SparkSession
from pyspark.ml.tuning import CrossValidatorModel
from pyspark.ml.functions import vector_to_array

MODEL_PATH = os.path.join(os.path.dirname(__file__), "..", "modele_credit_risk_spark")

CATEGORIES_CONNUES = {
    "person_home_ownership": ["RENT", "MORTGAGE", "OWN", "OTHER"],
    "loan_intent": [
        "PERSONAL", "EDUCATION", "MEDICAL", "VENTURE",
        "HOMEIMPROVEMENT", "DEBTCONSOLIDATION",
    ],
    "cb_person_default_on_file": ["N", "Y"],
}


class ModeleIntrouvableError(Exception):
    """Levée quand le dossier du modèle Spark est introuvable."""
    pass


class CategorieInconnueError(Exception):
    """Levée quand une valeur saisie n'a jamais été vue à l'entraînement."""
    pass


@st.cache_resource(show_spinner=False)
def get_spark_session():
    """Crée (une seule fois, mise en cache) une session Spark locale,
    avec une configuration mémoire réduite au minimum pour tenir dans
    les ~1 Go de RAM du tier gratuit de Streamlit Community Cloud."""
    spark = (
        SparkSession.builder
        .appName("credit_risk_streamlit")
        .master("local[1]")
        .config("spark.driver.memory", "512m")
        .config("spark.executor.memory", "512m")
        .config("spark.sql.shuffle.partitions", "1")
        .config("spark.ui.enabled", "false")
        .config("spark.ui.showConsoleProgress", "false")
        .getOrCreate()
    )
    spark.sparkContext.setLogLevel("ERROR")
    return spark


@st.cache_resource(show_spinner=False)
def load_model():
    """Charge le CrossValidatorModel déjà entraîné (une seule fois, mise en cache)."""
    spark = get_spark_session()
    if not os.path.exists(MODEL_PATH):
        raise ModeleIntrouvableError(
            f"Dossier modèle introuvable : {MODEL_PATH}. "
            "Vérifie que 'modele_credit_risk_spark' est bien à la racine du projet."
        )
    return CrossValidatorModel.load(MODEL_PATH)


def valider_categories(input_dict: dict):
    """
    Vérifie que les valeurs catégorielles saisies sont bien connues du
    pipeline. Lève une erreur explicite sinon, plutôt que de laisser Spark
    échouer avec une exception Java difficile à interpréter.
    """
    for colonne, valeurs_possibles in CATEGORIES_CONNUES.items():
        valeur = input_dict.get(colonne)
        if valeur not in valeurs_possibles:
            raise CategorieInconnueError(
                f"La valeur '{valeur}' pour '{colonne}' n'est pas reconnue "
                f"par le modèle. Valeurs attendues : {valeurs_possibles}."
            )


def predict_single(input_dict: dict):
    """
    Applique le pipeline déjà entraîné à une seule observation.

    Retourne (prediction, proba_0, proba_1) où prediction vaut 0 (en règle)
    ou 1 (en défaut), et proba_0/proba_1 sont les probabilités associées.
    """
    valider_categories(input_dict)

    spark = get_spark_session()
    model = load_model()

    df = spark.createDataFrame([input_dict])
    result = model.transform(df)
    result = result.withColumn("proba_array", vector_to_array("probability"))

    row = result.select("prediction", "proba_array").collect()[0]
    prediction = int(row["prediction"])
    proba_0 = float(row["proba_array"][0])
    proba_1 = float(row["proba_array"][1])

    return prediction, proba_0, proba_1