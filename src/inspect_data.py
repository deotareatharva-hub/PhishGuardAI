import pandas as pd

# Load the dataset
df = pd.read_csv("data/url_features_extracted1.csv")

# Display basic information
print("\n--- FIRST 5 ROWS ---")
print(df.head())

print("\n--- DATASET SHAPE ---")
print(df.shape)

print("\n--- COLUMN NAMES ---")
print(df.columns.tolist())

print("\n--- MISSING VALUES ---")
print(df.isnull().sum())

print("\n--- TARGET LABEL COUNTS ---")
print(df["ClassLabel"].value_counts(dropna=False))