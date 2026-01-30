import pandas as pd

def generate_summary_intents(semantic_schema: dict):
    """
    Generate safe summary intents.
    IMPORTANT: No implicit time filters.
    """
    metrics = semantic_schema.get("metrics", [])
    dimensions = semantic_schema.get("dimensions", [])

    if not metrics:
        return []

    primary_metric = metrics[0]

    intents = [
        {
            "name": "overall_metric",
            "intent": {
                "metric": primary_metric,
                "aggregation": "sum",
                "group_by": [],
                "filters": {},
                "time_granularity": None,
                "comparison": None
            }
        }
    ]

    if dimensions:
        intents.append(
            {
                "name": "by_primary_dimension",
                "intent": {
                    "metric": primary_metric,
                    "aggregation": "sum",
                    "group_by": [dimensions[0]],
                    "filters": {},
                    "time_granularity": None,
                    "comparison": None
                }
            }
        )

    return intents



def assemble_summary_results(results: dict) -> dict:
    """
    Assemble summary facts from executed summary queries.
    Fully dynamic, schema-safe, and dataset-agnostic.
    """
    summary = {}

    for name, df in results.items():
        if df is None or df.empty:
            continue

        # Case 1: Single aggregated value (no group_by)
        if df.shape[1] == 1:
            summary[name] = df.iloc[0]["value"]

        # Case 2: Grouped aggregation (by category, region, etc.)
        else:
            summary[name] = df.to_dict(orient="records")

    return summary
