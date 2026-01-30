import pandas as pd
def profile_input(data):
    if isinstance(data, str):
        return {
            "type": "text",
            "length": len(data),
            "sample": data[:500]
        }

    if isinstance(data, dict):
        return {
            "type": "json",
            "keys": list(data.keys())
        }

    # Pandas DataFrame
    return {
        "type": "tabular",
        "columns": list(data.columns),
        "row_count": len(data),
        "sample_rows": data.head(3).to_dict(orient="records"),
        "numeric_metrics": get_numeric_columns(data)
    }
def get_numeric_columns(df):
    numeric_cols = []

    for col in df.columns:
        try:
            pd.to_numeric(df[col].dropna().head(50))
            numeric_cols.append(col)
        except Exception:
            pass

    return numeric_cols
