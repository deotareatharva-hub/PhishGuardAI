
import pandas as pd
from sklearn.model_selection import GroupShuffleSplit

# Load the original dataset
df = pd.read_csv("data/url_features_extracted1.csv")

print("Original dataset shape:", df.shape)

# Remove rows with missing target labels
df = df.dropna(subset=["ClassLabel"]).copy()

# Remove exact duplicate records
df = df.drop_duplicates().copy()

# Ensure target labels are integers
df["ClassLabel"] = df["ClassLabel"].astype(int)

# Separate URLs, features, and target
urls = df["URL"].astype(str)
X = df.drop(columns=["URL", "ClassLabel"])
y = df["ClassLabel"]

print("\nData cleaning completed!")
print("Cleaned dataset shape:", df.shape)
print("Feature matrix shape:", X.shape)
print("Target shape:", y.shape)

print("\nClass distribution:")
print(y.value_counts())

print("\nMissing feature values:", X.isnull().sum().sum())
print("\nFeature columns:")
print(X.columns.tolist())

# Save cleaned data, including URLs
df.to_csv("data/cleaned_dataset.csv", index=False)

print("\nCleaned dataset saved to data/cleaned_dataset.csv")

# Group identical feature combinations together
# Identical feature vectors must remain in the same split.
groups = pd.util.hash_pandas_object(X, index=False).astype(str)

# Create a group-aware train-test split
splitter = GroupShuffleSplit(
    n_splits=1,
    test_size=0.20,
    random_state=42
)

train_idx, test_idx = next(
    splitter.split(X, y, groups=groups)
)

X_train = X.iloc[train_idx]
X_test = X.iloc[test_idx]
y_train = y.iloc[train_idx]
y_test = y.iloc[test_idx]

# Save the splits for consistent model evaluation
train_df = X_train.copy()
train_df["ClassLabel"] = y_train

test_df = X_test.copy()
test_df["ClassLabel"] = y_test

train_df.to_csv("data/train.csv", index=False)
test_df.to_csv("data/test.csv", index=False)

print("\n--- GROUP-AWARE TRAIN-TEST SPLIT ---")
print("Training samples:", len(X_train))
print("Testing samples:", len(X_test))
print("Training class distribution:")
print(y_train.value_counts())
print("Testing class distribution:")
print(y_test.value_counts())

print("\nTraining groups:", groups.iloc[train_idx].nunique())
print("Testing groups:", groups.iloc[test_idx].nunique())
print(
    "Overlapping feature groups:",
    len(
        set(groups.iloc[train_idx])
        & set(groups.iloc[test_idx])
    )
)

print("\nSaved:")
print("  data/cleaned_dataset.csv")
print("  data/train.csv")
print("  data/test.csv")
