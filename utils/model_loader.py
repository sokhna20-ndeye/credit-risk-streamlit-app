import os
import streamlit as st
from pyspark.sql import SparkSession
from pyspark.ml.tuning import CrossValidatorModel
from pyspark.ml.functions import vector_to_array

# Chemin du dossier modèle exporté par save_model.R
MODEL_PATH = os.path.join(os.path.dirname(__file__), "..", "modele_credit_risk_spark")


@st.cache_resource(show_spinner=False)
def get_spark_session():
    """Crée (une seule fois, mise en cache) une session Spark locale."""
    spark = (
        SparkSession.builder
        .appName("credit_risk_streamlit")
        .master("local[*]")
        .config("spark.driver.memory", "2g")
        .config("spark.sql.shuffle.partitions", "4")
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
        raise FileNotFoundError(
            f"Dossier modèle introuvable : {MODEL_PATH}\n"
            "As-tu bien placé le dossier 'modele_credit_risk_spark' "
            "à la racine du projet, au même niveau que Home.py ?"
        )
    return CrossValidatorModel.load(MODEL_PATH)


def predict_single(input_dict: dict):
    """Applique le modèle déjà entraîné à une seule observation."""
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