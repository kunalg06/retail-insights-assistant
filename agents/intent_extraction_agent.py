import json
from pathlib import Path
from config.llm_config import get_openai_client

client = get_openai_client()
PROMPT_PATH = Path("prompts/intent_extraction_prompt.txt")


def extract_query_intent(user_input: str, semantic_schema: dict) -> dict:
    system_prompt = PROMPT_PATH.read_text()

    user_message = f"""
    Semantic schema:
    {json.dumps(semantic_schema, indent=2)}

    User question:
    {user_input}
    """

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ],
        temperature=0
    )

    raw_output = response.choices[0].message.content.strip()

    if not raw_output.startswith("{"):
        raise ValueError(f"Intent agent returned invalid JSON:\n{raw_output}")

    try:
        intent = json.loads(raw_output)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON from intent agent:\n{raw_output}") from e

    # ✅ Normalize & validate
    intent = validate_and_normalize_intent(intent, semantic_schema)

    # ✅ Attach original question ONLY after intent exists
    intent["original_question"] = user_input

    # ✅ Feasibility check
    return check_intent_feasibility(intent, semantic_schema)


def validate_and_normalize_intent(intent: dict, semantic_schema: dict) -> dict:
    allowed_metrics = semantic_schema.get("metrics", [])
    allowed_dimensions = semantic_schema.get("dimensions", [])
    allowed_time_fields = semantic_schema.get("time_fields", [])

    # metric
    if intent.get("metric") not in allowed_metrics:
        intent["metric"] = allowed_metrics[0] if allowed_metrics else None

    # aggregation
    allowed_aggs = ["sum", "avg", "count", "yoy_growth"]
    if intent.get("aggregation") not in allowed_aggs:
        intent["aggregation"] = "sum"

    # group_by
    if not isinstance(intent.get("group_by"), list):
        intent["group_by"] = []

    intent["group_by"] = [
        g for g in intent["group_by"]
        if g in allowed_dimensions
    ]

    # filters
    raw_filters = intent.get("filters")
    if not isinstance(raw_filters, dict):
        raw_filters = {}

    intent["filters"] = {
        k: v for k, v in raw_filters.items()
        if k in allowed_dimensions or k in allowed_time_fields
    }

    # time_granularity
    allowed_time_granularity = ["year", "quarter", "month", None]
    if intent.get("time_granularity") not in allowed_time_granularity:
        intent["time_granularity"] = None

    # comparison
    if intent.get("comparison") not in ["yoy", None]:
        intent["comparison"] = None

    return intent


def check_intent_feasibility(intent: dict, semantic_schema: dict) -> dict:
    time_required = (
        intent.get("time_granularity") is not None
        or intent.get("comparison") is not None
    )

    if time_required and not semantic_schema.get("time_fields"):
        return {
            "status": "invalid",
            "reason": "The dataset does not contain time-based fields required for this analysis.",
            "suggestion": "You can ask questions about stock distribution by category, size, color, or SKU."
        }

    return {
        "status": "valid",
        "intent": intent
    }
