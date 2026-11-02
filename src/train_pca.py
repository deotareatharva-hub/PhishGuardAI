
import pandas as pd
import os

from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
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

# Standardize features using training data only
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# Apply PCA while retaining 95% of the variance
pca = PCA(n_components=0.95, random_state=42)

X_train_pca = pca.fit_transform(X_train_scaled)
X_test_pca = pca.transform(X_test_scaled)

print("Original number of features:", X_train.shape[1])
print("Reduced number of components:", X_train_pca.shape[1])
print(
    "Explained variance retained:",
    round(pca.explained_variance_ratio_.sum(), 4)
)

# Train MLP using PCA-reduced features
model = MLPClassifier(
    hidden_layer_sizes=(64, 32),
    activation="relu",
    solver="adam",
    max_iter=100,
    early_stopping=True,
    random_state=42
)

print("\nTraining PCA + MLP model...")
model.fit(X_train_pca, y_train)

# Predictions
y_pred = model.predict(X_test_pca)

# Evaluation
accuracy = accuracy_score(y_test, y_pred)
precision = precision_score(y_test, y_pred, zero_division=0)
recall = recall_score(y_test, y_pred, zero_division=0)
f1 = f1_score(y_test, y_pred, zero_division=0)

print("\n--- PCA + MLP RESULTS (GROUP-AWARE SPLIT) ---")
print(f"Accuracy:  {accuracy:.4f}")
print(f"Precision: {precision:.4f}")
print(f"Recall:    {recall:.4f}")
print(f"F1-score:  {f1:.4f}")

print("\nConfusion Matrix:")
print(confusion_matrix(y_test, y_pred))

# Save results
os.makedirs("results", exist_ok=True)

with open("results/pca_results.txt", "w") as f:
    f.write("PCA + MLP Results (Group-Aware Split)\n")
    f.write(f"Original features: {X_train.shape[1]}\n")
    f.write(f"PCA components: {X_train_pca.shape[1]}\n")
    f.write(
        f"Explained variance: "
        f"{pca.explained_variance_ratio_.sum():.4f}\n"
    )
    f.write(f"Accuracy: {accuracy:.4f}\n")
    f.write(f"Precision: {precision:.4f}\n")
    f.write(f"Recall: {recall:.4f}\n")
    f.write(f"F1-score: {f1:.4f}\n")

print("\nResults saved to results/pca_results.txt")
