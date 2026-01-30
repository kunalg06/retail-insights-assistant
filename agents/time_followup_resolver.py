def resolve_time_followup(user_input: str, intent: dict, semantic_schema: dict) -> dict:
    """
    Handles follow-up time queries like 'And in Q4?' or 'What about 2023?'
    """
    text = user_input.lower()

    # Only act if dataset supports time
    if not semantic_schema.get("time_fields"):
        return intent

    # Quarter detection
    for q in ["q1", "q2", "q3", "q4"]:
        if q in text:
            intent["filters"] = intent.get("filters", {})
            intent["filters"]["quarter"] = q.upper()
            intent["time_granularity"] = "quarter"
            return intent

    # Year detection
    for year in range(2000, 2035):
        if str(year) in text:
            intent["filters"] = intent.get("filters", {})
            intent["filters"]["year"] = str(year)
            intent["time_granularity"] = "year"
            return intent

    return intent
