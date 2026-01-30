def merge_with_previous_intent(new_intent: dict, previous_intent: dict) -> dict:
    """
    Fill missing fields in new intent using previous intent.
    """
    if not previous_intent:
        return new_intent

    merged = new_intent.copy()

    for key in [
        "metric",
        "aggregation",
        "group_by",
        "filters",
        "time_granularity",
        "comparison"
    ]:
        if merged.get(key) in [None, {}, []]:
            merged[key] = previous_intent.get(key)

    return merged
