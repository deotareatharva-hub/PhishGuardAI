
import os
import pandas as pd

from sklearn.preprocessing import StandardScaler
from sklearn.neural_network import MLPClassifier
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix
)

os.makedirs("results", exist_ok=True)

# Load group-aware training and testing datasets
train_df = pd.read_csv("data/train.csv")
test_df = pd.read_csv("data/test.csv")

X_train = train_df.drop(columns=["ClassLabel"])
y_train = train_df["ClassLabel"]

X_test = test_df.drop(columns=["ClassLabel"])
y_test = test_df["ClassLabel"]

# Standardize features using training data only
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# Build MLP classifier
model = MLPClassifier(
    hidden_layer_sizes=(64, 32),
    activation="relu",
    solver="adam",
    max_iter=100,
    early_stopping=True,
    random_state=42
)

print("Training MLP model using group-aware split...")

model.fit(X_train_scaled, y_train)
y_pred = model.predict(X_test_scaled)

# Calculate metrics
accuracy = accuracy_score(y_test, y_pred)
precision = precision_score(y_test, y_pred, zero_division=0)
recall = recall_score(y_test, y_pred, zero_division=0)
f1 = f1_score(y_test, y_pred, zero_division=0)
cm = confusion_matrix(y_test, y_pred)

print("\n--- MLP RESULTS (GROUP-AWARE SPLIT) ---")
print(f"Accuracy:  {accuracy:.4f}")
print(f"Precision: {precision:.4f}")
print(f"Recall:    {recall:.4f}")
print(f"F1-score:  {f1:.4f}")
print("\nConfusion Matrix:")
print(cm)
print("\nIterations used:", model.n_iter_)

# Save metrics for model comparison
with open("results/mlp_results.txt", "w") as f:
    f.write("MLP Results (Group-Aware Split)\n")
    f.write(f"Accuracy: {accuracy:.4f}\n")
    f.write(f"Precision: {precision:.4f}\n")
    f.write(f"Recall: {recall:.4f}\n")
    f.write(f"F1-score: {f1:.4f}\n")
    f.write(f"Confusion Matrix:\n{cm}\n")
    f.write(f"Iterations: {model.n_iter_}\n")

print("\nResults saved to results/mlp_results.txt")
