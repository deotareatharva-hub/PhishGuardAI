from pathlib import Path

import joblib
import pandas as pd

from backend.app.features import extract_features


# Resolve the model path relative to the project root.
PROJECT_ROOT = Path(__file__).resolve().parents[2]
MODEL_PATH = PROJECT_ROOT / "models" / "svd_mlp_14_pipeline.joblib"


def load_pipeline():
    """Load the trained model pipeline."""
    if not MODEL_PATH.exists():
        raise FileNotFoundError(
            f"Trained model not found: {MODEL_PATH}"
        )

    return joblib.load(MODEL_PATH)


# Load the model once when this module is imported.
pipeline = load_pipeline()


def predict_url(url: str) -> dict:
    """
    Extract URL features and predict the class using the saved model.

    Returns the predicted class, probability estimates, and features.
    """
    # Extract features from the submitted URL.
    features = extract_features(url)

    # Arrange the features in the exact order used during training.
    feature_columns = pipeline["feature_columns"]

    feature_frame = pd.DataFrame(
        [[features[column] for column in feature_columns]],
        columns=feature_columns,
    )

    # Apply the same scaler and SVD transformation used during training.
    scaled_features = pipeline["scaler"].transform(feature_frame)
    reduced_features = pipeline["svd"].transform(scaled_features)

    # Predict the class.
    model = pipeline["model"]
    predicted_class = int(model.predict(reduced_features)[0])

    # Get the probability estimate for the predicted class.
    probabilities = model.predict_proba(reduced_features)[0]
    classes = list(model.classes_)

    probability_by_class = {
        str(int(label)): float(probability)
        for label, probability in zip(classes, probabilities)
    }

    predicted_probability = probability_by_class[str(predicted_class)]

    return {
        "url": url,
        "predicted_class": predicted_class,
        "predicted_class_probability": round(
            predicted_probability, 4
        ),
        "class_probabilities": probability_by_class,
        "features": features,
        "model": "SVD + MLP (14 features)",
    }
