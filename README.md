# Application de Prédiction de Défaut de Paiement

Application Streamlit permettant de prédire, à partir d'un modèle Random
Forest entraîné avec Spark ML (sparklyr), si une personne est en règle ou
en défaut de paiement sur un prêt.

## Structure du projet

```
credit_risk_app/
├── modele_credit_risk_spark/   # Modèle Spark ML déjà entraîné (CrossValidatorModel)
├── pages/
│   ├── 1_🔮_Prediction.py
│   └── 2_📊_Tableau_de_bord.py
├── utils/
│   ├── model_loader.py         # Chargement du modèle + prédiction
│   └── history.py              # Historique des prédictions
├── data/
│   └── predictions_history.csv
├── .streamlit/
│   └── config.toml
├── Home.py
└── requirements.txt
```

## Installation

Prérequis : Python 3.10, Java 8 ou 11 (nécessaire pour PySpark).

```bash
python -m venv venv
venv\Scripts\activate          # Windows
pip install -r requirements.txt
```

## Lancer l'application

```bash
streamlit run Home.py
```

L'application s'ouvre sur `http://localhost:8501`.

## Fonctionnalités

- **🔮 Prédiction** : formulaire de saisie, prédiction en temps réel via le
  modèle Spark ML, affichage visuel (vert + confettis si en règle, alerte
  rouge si en défaut avec niveau de risque).
- **📊 Tableau de bord** : indicateurs clés, graphique de répartition,
  historique complet des prédictions effectuées.

## Notes techniques

- Le modèle n'est ni réentraîné ni modifié par cette application : il a été
  entraîné et validé séparément (validation croisée) via `sparklyr` en R,
  puis exporté avec `ml_save()`.
- L'application lance une session Spark locale (`local[*]`) au premier
  chargement — la première prédiction peut prendre 10 à 30 secondes.