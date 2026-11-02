from pathlib import Path
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent

df = pd.read_csv(
    PROJECT_ROOT / "data" / "url_features_extracted1.csv"
)

df = df.dropna(subset=["URL"]).head(30)

print("\nURL TOKEN COUNT INVESTIGATION")
print("=" * 90)

for _, row in df.iterrows():
    url = str(row["URL"])
    count = int(row["token_count"])

    print(f"\nURL: {url}")
    print(f"Dataset token_count: {count}")
    print(f"URL length: {len(url)}")

    print("Scheme:", url.split("://")[0] if "://" in url else "None")

    after_scheme = url.split("://", 1)[-1]
    print("Domain:", after_scheme.split("/", 1)[0])

    path = after_scheme.split("/", 1)[1] if "/" in after_scheme else ""
    print("Path:", path)

print("\n" + "=" * 90)
print("Investigation complete.")