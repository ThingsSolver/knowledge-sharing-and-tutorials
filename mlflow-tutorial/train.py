# The data set used in this example is from http://archive.ics.uci.edu/ml/datasets/Wine+Quality
# P. Cortez, A. Cerdeira, F. Almeida, T. Matos and J. Reis.
# Modeling wine preferences by data mining from physicochemical properties. In Decision Support Systems, Elsevier, 47(4):547-553, 2009.

import os
import warnings
import sys

import pandas as pd
import numpy as np
from sklearn.metrics import silhouette_score
from sklearn.cluster import KMeans

import mlflow
import mlflow.sklearn


def eval_metrics(kmeans, X):
    return silhouette_score(X, labels=kmeans.predict(X)), kmeans.inertia_



if __name__ == "__main__":
    warnings.filterwarnings("ignore")
    np.random.seed(40)

    # Read the old_faithful.csv file (make sure you're running this from the root of MLflow!)
    data_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "old_faithful.csv")
    data = pd.read_csv(data_path)

    k_low = int(sys.argv[1])
    k_high = int(sys.argv[2])

    train_x = data.values
    for k in range(k_low, k_high):
        with mlflow.start_run():
            kmeans = KMeans(n_clusters=k, random_state=42)
            kmeans.fit(train_x)

            labels = kmeans.predict(train_x)

            (s_score, ssd) = eval_metrics(kmeans, train_x)

            print("Kmeans model (k=%f):" % (k))
            print("  silhouette_score: %s" % s_score)
            print("  ssd: %s" % ssd)

            mlflow.log_param("k", k)
            mlflow.log_metric("silhouette_score", s_score)
            mlflow.log_metric("ssd", ssd)

            mlflow.sklearn.log_model(kmeans, "model")
