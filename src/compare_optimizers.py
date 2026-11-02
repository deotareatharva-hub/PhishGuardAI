
import os
import time
import pandas as pd
import matplotlib.pyplot as plt

from sklearn.preprocessing import StandardScaler
from sklearn.neural_network import MLPClassifier
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score
)

# Create results directory
os.makedirs("results", exist_ok=True)

# Load the same group-aware training and testing datasets
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

results = []
training_losses = {}

# Compare SGD and Adam on the same split
for optimizer in ["sgd", "adam"]:

    print(f"\nTraining MLP with {optimizer.upper()}...")

    model = MLPClassifier(
        hidden_layer_sizes=(64, 32),
        activation="relu",
        solver=optimizer,
        learning_rate_init=0.001,
        max_iter=100,
        early_stopping=True,
        random_state=42
    )

    start_time = time.time()

    model.fit(X_train_scaled, y_train)

    training_time = time.time() - start_time

    y_pred = model.predict(X_test_scaled)

    metrics = {
        "Optimizer": optimizer.upper(),
        "Accuracy": accuracy_score(y_test, y_pred),
        "Precision": precision_score(
            y_test, y_pred, zero_division=0
        ),
        "Recall": recall_score(
            y_test, y_pred, zero_division=0
        ),
        "F1 Score": f1_score(
            y_test, y_pred, zero_division=0
        ),
        "Training Time (seconds)": training_time,
        "Iterations": model.n_iter_
    }

    results.append(metrics)
    training_losses[optimizer.upper()] = model.loss_curve_

    print(f"Accuracy: {metrics['Accuracy']:.4f}")
    print(f"Precision: {metrics['Precision']:.4f}")
    print(f"Recall: {metrics['Recall']:.4f}")
    print(f"F1 Score: {metrics['F1 Score']:.4f}")
    print(f"Training time: {training_time:.2f} seconds")
    print(f"Iterations: {model.n_iter_}")

# Save comparison table
results_df = pd.DataFrame(results)

results_df.to_csv(
    "results/optimizer_comparison.csv",
    index=False
)

print("\n--- OPTIMIZER COMPARISON (GROUP-AWARE SPLIT) ---")
print(results_df.round(4).to_string(index=False))

# Plot training loss curves
plt.figure(figsize=(8, 5))

for optimizer, losses in training_losses.items():
    plt.plot(
        range(1, len(losses) + 1),
        losses,
        label=optimizer
    )

plt.xlabel("Iteration")
plt.ylabel("Training Loss")
plt.title("MLP Optimization: SGD vs Adam")
plt.legend()
plt.tight_layout()

plt.savefig(
    "results/optimizer_loss_comparison.png",
    dpi=300
)

plt.close()

print("\nSaved: results/optimizer_comparison.csv")
print("Saved: results/optimizer_loss_comparison.png")
