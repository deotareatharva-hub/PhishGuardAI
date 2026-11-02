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
    confusion_matrix
)

# Load group-aware training and testing datasets
train_df = pd.read_csv("data/train.csv")
test_df = pd.read_csv("data/test.csv")

# Separate features and target
X_train = train_df.drop(columns=["ClassLabel"])
y_train = train_df["ClassLabel"]

X_test = test_df.drop(columns=["ClassLabel"])
y_test = test_df["ClassLabel"]

# Scale features using training data only
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# Apply SVD
start_time = time.time()

svd = TruncatedSVD(n_components=10, random_state=42)

X_train_svd = svd.fit_transform(X_train_scaled)
X_test_svd = svd.transform(X_test_scaled)

svd_time = time.time() - start_time

print("Original features:", X_train.shape[1])
print("SVD components:", X_train_svd.shape[1])
print(
    "Explained variance ratio:",
    round(svd.explained_variance_ratio_.sum(), 4)
)
print("SVD transformation time:", round(svd_time, 3), "seconds")

# Train MLP
model = MLPClassifier(
    hidden_layer_sizes=(64, 32),
    activation="relu",
    solver="adam",
    max_iter=100,
    early_stopping=True,
    random_state=42
)

print("\nTraining SVD + MLP model...")
model.fit(X_train_svd, y_train)

# Predictions
y_pred = model.predict(X_test_svd)

# Evaluation
accuracy = accuracy_score(y_test, y_pred)
precision = precision_score(y_test, y_pred, zero_division=0)
recall = recall_score(y_test, y_pred, zero_division=0)
f1 = f1_score(y_test, y_pred, zero_division=0)

print("\n--- SVD + MLP RESULTS (GROUP-AWARE SPLIT) ---")
print(f"Accuracy:  {accuracy:.4f}")
print(f"Precision: {precision:.4f}")
print(f"Recall:    {recall:.4f}")
print(f"F1-score:  {f1:.4f}")

print("\nConfusion Matrix:")
print(confusion_matrix(y_test, y_pred))

# Save results
os.makedirs("results", exist_ok=True)

with open("results/svd_results.txt", "w") as f:
    f.write("SVD + MLP Results (Group-Aware Split)\n")
    f.write(f"Original features: {X_train.shape[1]}\n")
    f.write(f"SVD components: {X_train_svd.shape[1]}\n")
    f.write(
        f"Explained variance ratio: "
        f"{svd.explained_variance_ratio_.sum():.4f}\n"
    )
    f.write(f"Transformation time: {svd_time:.3f} seconds\n")
    f.write(f"Accuracy: {accuracy:.4f}\n")
    f.write(f"Precision: {precision:.4f}\n")
    f.write(f"Recall: {recall:.4f}\n")
    f.write(f"F1-score: {f1:.4f}\n")

print("\nResults saved to results/svd_results.txt")
# Save the complete trained pipeline components
os.makedirs("models", exist_ok=True)

pipeline_data = {
    "scaler": scaler,
    "svd": svd,
    "model": model,
    "feature_columns": list(X_train.columns),
    "threshold": 0.5
}

joblib.dump(pipeline_data, "models/svd_mlp_pipeline.joblib")

print("Trained SVD + MLP components saved to models/svd_mlp_pipeline.joblib")