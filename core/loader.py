import pandas as pd
import json

def load_data(file_path: str, file_type: str):
    if file_type == "csv":
        return pd.read_csv(file_path,low_memory=False)

    elif file_type == "excel":
        return pd.read_excel(file_path)

    elif file_type == "json":
        with open(file_path, "r") as f:
            return json.load(f)
    else:
        raise ValueError("Unsupported file type")