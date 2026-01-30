import pandas as pd


def normalize_value(value):
    """Convert numpy / pandas scalars to native Python types."""
    try:
        return value.item()
    except AttributeError:
        return value


def row_to_native_dict(row: pd.Series) -> dict:
    """Convert a pandas row to a JSON-safe dict."""
    return {k: normalize_value(v) for k, v in row.to_dict().items()}


def apply_business_reasoning(intent: dict, result_df: pd.DataFrame) -> dict:
    if result_df is None or result_df.empty:
        return {
            "status": "no_data",
            "message": "No data available for the given query."
        }

    question = intent.get("original_question", "").lower()

    # ---------- UNDERPERFORMED ----------
    if "underperform" in question or "lowest" in question:
        sorted_df = result_df.sort_values(by="value", ascending=True)
        worst_row = sorted_df.iloc[0]

        return {
            "status": "success",
            "insight_type": "underperformed",
            "row": row_to_native_dict(worst_row)
        }

    # ---------- TOP PERFORMER ----------
    if "top" in question or "best" in question or "highest" in question:
        sorted_df = result_df.sort_values(by="value", ascending=False)
        best_row = sorted_df.iloc[0]

        return {
            "status": "success",
            "insight_type": "top_performer",
            "row": row_to_native_dict(best_row)
        }

    # ---------- DEFAULT (SAFE FALLBACK) ----------
    # Return aggregated preview, NOT full DataFrame
    preview_rows = []

    for _, row in result_df.head(5).iterrows():
        preview_rows.append(row_to_native_dict(row))

    return {
        "status": "success",
        "insight_type": "summary",
        "data": preview_rows
    }
