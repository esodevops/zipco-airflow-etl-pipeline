import pandas as pd
from pathlib import Path

CLEANED_DATA_DIR = Path(__file__).resolve().parent.parent / "dataset" / "raw_data"

def extraction():
    try:
        data = pd.read_csv(CLEANED_DATA_DIR/"zipco_transaction.csv")
        print("Data loaded successfully!")
        return data
    except Exception as e:
        print(f"An error occurred: {e}")
        raise
