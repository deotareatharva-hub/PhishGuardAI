
import os
import time
import pandas as pd
import joblib

from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import TruncatedSVD
from sklearn.neural_network import MLPClassifier
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
    classification_report,
)

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from backend.app.features import FEATURE_COLUMNS


# --------------------------------------------------
# 1. LOAD DATA
# --------------------------------------------------

train_path = "data/train.csv"
test_path = "data/test.csv"

if not os.path.exists(train_path) or not os.path.exists(test_path):
    raise FileNotFoundError(
        "Training or testing data not found. "
        "Expected data/train.csv and data/test.csv."
    )

train_df = pd.read_csv(train_path)
test_df = pd.read_csv(test_path)

if "ClassLabel" not in train_df.columns:
    raise ValueError("ClassLabel is missing from data/train.csv.")

if "ClassLabel" not in test_df.columns:
    raise ValueError("ClassLabel is missing from data/test.csv.")


# --------------------------------------------------
# 2. SELECT THE 14 FEATURES
# --------------------------------------------------

missing_train = [
    column for column in FEATURE_COLUMNS
    if column not in train_df.columns
]

missing_test = [
    column for column in FEATURE_COLUMNS
    if column not in test_df.columns
]

if missing_train or missing_test:
    raise ValueError(
        f"Missing training features: {missing_train}\n"
        f"Missing testing features: {missing_test}"
    )

X_train = train_df[FEATURE_COLUMNS].copy()
y_train = train_df["ClassLabel"].copy()

X_test = test_df[FEATURE_COLUMNS].copy()
y_test = test_df["ClassLabel"].copy()

print("=" * 55)
print("PHISHGUARD-AI: 14-FEATURE SVD + MLP")
print("=" * 55)

print("Training samples:", len(X_train))
print("Testing samples:", len(X_test))
print("Selected features:", len(FEATURE_COLUMNS))
print("Feature order:", FEATURE_COLUMNS)


# --------------------------------------------------
# 3. SCALE FEATURES
# --------------------------------------------------

scaler = StandardScaler()

X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)


# --------------------------------------------------
# 4. APPLY SVD
# --------------------------------------------------

start_time = time.time()

# Use at most 10 components, never exceeding the
# number of available features.
n_components = min(10, X_train.shape[1])

svd = TruncatedSVD(
    n_components=n_components,
    random_state=42,
)

X_train_svd = svd.fit_transform(X_train_scaled)
X_test_svd = svd.transform(X_test_scaled)

svd_time = time.time() - start_time

explained_variance = svd.explained_variance_ratio_.sum()

print("\n--- SVD INFORMATION ---")
print("Original features:", X_train.shape[1])
print("SVD components:", X_train_svd.shape[1])
print("Explained variance ratio:", round(explained_variance, 4))
print("SVD transformation time:", round(svd_time, 3), "seconds")


# --------------------------------------------------
# 5. TRAIN MLP CLASSIFIER
# --------------------------------------------------

model = MLPClassifier(
    hidden_layer_sizes=(64, 32),
    activation="relu",
    solver="adam",
    max_iter=100,
    early_stopping=True,
    random_state=42,
)

print("\nTraining SVD + MLP model...")

model.fit(X_train_svd, y_train)


# --------------------------------------------------
# 6. EVALUATE MODEL
# --------------------------------------------------

y_pred = model.predict(X_test_svd)

accuracy = accuracy_score(y_test, y_pred)
precision = precision_score(
    y_test, y_pred, zero_division=0
)
recall = recall_score(
    y_test, y_pred, zero_division=0
)
f1 = f1_score(
    y_test, y_pred, zero_division=0
)

cm = confusion_matrix(y_test, y_pred)

print("\n--- 14-FEATURE MODEL RESULTS ---")
print(f"Accuracy:  {accuracy:.4f}")
print(f"Precision: {precision:.4f}")
print(f"Recall:    {recall:.4f}")
print(f"F1-score:  {f1:.4f}")

print("\nConfusion Matrix:")
print(cm)

print("\nClassification Report:")
print(classification_report(y_test, y_pred, zero_division=0))


# --------------------------------------------------
# 7. SAVE EVALUATION RESULTS
# --------------------------------------------------

os.makedirs("results", exist_ok=True)

with open("results/svd_14_results.txt", "w", encoding="utf-8") as file:
    file.write("PhishGuard-AI: 14-Feature SVD + MLP Results\n")
    file.write("=" * 50 + "\n")
    file.write(f"Training samples: {len(X_train)}\n")
    file.write(f"Testing samples: {len(X_test)}\n")
    file.write(f"Original features: {X_train.shape[1]}\n")
    file.write(f"SVD components: {X_train_svd.shape[1]}\n")
    file.write(f"Explained variance ratio: {explained_variance:.4f}\n")
    file.write(f"SVD transformation time: {svd_time:.3f} seconds\n")
    file.write(f"Accuracy: {accuracy:.4f}\n")
    file.write(f"Precision: {precision:.4f}\n")
    file.write(f"Recall: {recall:.4f}\n")
    file.write(f"F1-score: {f1:.4f}\n")
    file.write("\nConfusion Matrix:\n")
    file.write(str(cm))
    file.write("\n\nClassification Report:\n")
    file.write(
        classification_report(y_test, y_pred, zero_division=0)
    )

print("\nResults saved to results/svd_14_results.txt")


# --------------------------------------------------
# 8. SAVE THE NEW MODEL PIPELINE
# --------------------------------------------------

os.makedirs("models", exist_ok=True)

pipeline_data = {
    "scaler": scaler,
    "svd": svd,
    "model": model,
    "feature_columns": list(FEATURE_COLUMNS),
    "threshold": 0.5,
}

model_path = "models/svd_mlp_14_pipeline.joblib"

joblib.dump(pipeline_data, model_path)

print("\nNew model saved to:", model_path)
print("Original 16-feature model has not been overwritten.")
print("\nTraining and evaluation completed.")
