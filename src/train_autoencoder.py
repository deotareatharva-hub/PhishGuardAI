
import os
import time
import numpy as np
import pandas as pd
import tensorflow as tf
import matplotlib.pyplot as plt

from sklearn.preprocessing import StandardScaler
from sklearn.neural_network import MLPClassifier
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix
)

# Reproducibility
np.random.seed(42)
tf.random.set_seed(42)

# Create required directories
os.makedirs("models", exist_ok=True)
os.makedirs("results", exist_ok=True)

# Load the group-aware training and testing datasets
train_df = pd.read_csv("data/train.csv")
test_df = pd.read_csv("data/test.csv")

# Separate features and target
X_train = train_df.drop(columns=["ClassLabel"])
y_train = train_df["ClassLabel"]

X_test = test_df.drop(columns=["ClassLabel"])
y_test = test_df["ClassLabel"]

# Standardize using training data only
scaler = StandardScaler()

X_train_scaled = scaler.fit_transform(X_train).astype("float32")
X_test_scaled = scaler.transform(X_test).astype("float32")

# Autoencoder architecture
input_dim = X_train_scaled.shape[1]
encoding_dim = 8

inputs = tf.keras.Input(shape=(input_dim,))

# Encoder: 16 features -> 12 neurons -> 8 encoded features
encoded = tf.keras.layers.Dense(
    12,
    activation="relu"
)(inputs)

encoded = tf.keras.layers.Dense(
    encoding_dim,
    activation="relu",
    name="encoded_features"
)(encoded)

# Decoder: 8 encoded features -> 12 neurons -> 16 reconstructed features
decoded = tf.keras.layers.Dense(
    12,
    activation="relu"
)(encoded)

outputs = tf.keras.layers.Dense(
    input_dim,
    activation="linear"
)(decoded)

autoencoder = tf.keras.Model(inputs, outputs)

autoencoder.compile(
    optimizer="adam",
    loss="mse"
)

# Train the autoencoder using training features only
start_time = time.time()

history = autoencoder.fit(
    X_train_scaled,
    X_train_scaled,
    epochs=30,
    batch_size=256,
    validation_split=0.1,
    shuffle=True,
    callbacks=[
        tf.keras.callbacks.EarlyStopping(
            monitor="val_loss",
            patience=4,
            restore_best_weights=True
        )
    ],
    verbose=1
)

training_time = time.time() - start_time

# Save the trained autoencoder
autoencoder.save("models/autoencoder.keras")

# Extract compressed representations
encoder = tf.keras.Model(
    inputs=autoencoder.input,
    outputs=autoencoder.get_layer("encoded_features").output
)

X_train_encoded = encoder.predict(
    X_train_scaled,
    verbose=0
)

X_test_encoded = encoder.predict(
    X_test_scaled,
    verbose=0
)

print("\n--- Autoencoder Information ---")
print("Original features:", input_dim)
print("Encoded features:", X_train_encoded.shape[1])
print("Training samples:", len(X_train))
print("Testing samples:", len(X_test))
print("Autoencoder training time:", round(training_time, 2), "seconds")

# Train MLP classifier on compressed features
classifier = MLPClassifier(
    hidden_layer_sizes=(32, 16),
    activation="relu",
    solver="adam",
    max_iter=100,
    early_stopping=True,
    random_state=42
)

print("\nTraining MLP on autoencoder features...")

classifier.fit(X_train_encoded, y_train)
y_pred = classifier.predict(X_test_encoded)

# Calculate classification metrics
accuracy = accuracy_score(y_test, y_pred)
precision = precision_score(y_test, y_pred, zero_division=0)
recall = recall_score(y_test, y_pred, zero_division=0)
f1 = f1_score(y_test, y_pred, zero_division=0)
cm = confusion_matrix(y_test, y_pred)

print("\n--- AUTOENCODER + MLP RESULTS (GROUP-AWARE SPLIT) ---")
print(f"Accuracy:  {accuracy:.4f}")
print(f"Precision: {precision:.4f}")
print(f"Recall:    {recall:.4f}")
print(f"F1-score:  {f1:.4f}")

print("\nConfusion Matrix:")
print(cm)

# Save training and validation loss plot
plt.figure(figsize=(8, 5))
plt.plot(history.history["loss"], label="Training Loss")
plt.plot(history.history["val_loss"], label="Validation Loss")
plt.xlabel("Epoch")
plt.ylabel("Mean Squared Error")
plt.title("Autoencoder Training and Validation Loss")
plt.legend()
plt.tight_layout()
plt.savefig("results/autoencoder_loss.png", dpi=300)
plt.close()

# Save evaluation results
with open("results/autoencoder_results.txt", "w") as f:
    f.write("Autoencoder + MLP Results (Group-Aware Split)\n")
    f.write(f"Original features: {input_dim}\n")
    f.write(f"Encoded features: {X_train_encoded.shape[1]}\n")
    f.write(f"Training samples: {len(X_train)}\n")
    f.write(f"Testing samples: {len(X_test)}\n")
    f.write(f"Autoencoder training time: {training_time:.2f} seconds\n")
    f.write(f"Accuracy: {accuracy:.4f}\n")
    f.write(f"Precision: {precision:.4f}\n")
    f.write(f"Recall: {recall:.4f}\n")
    f.write(f"F1-score: {f1:.4f}\n")
    f.write(f"Confusion Matrix:\n{cm}\n")

print("\nSaved model: models/autoencoder.keras")
print("Saved plot: results/autoencoder_loss.png")
print("Saved metrics: results/autoencoder_results.txt")
