import json
from pathlib import Path
from config.llm_config import get_openai_client

client = get_openai_client()
PROMPT_PATH = Path("prompts/semantic_schema_prompt.txt")


def generate_semantic_schema(profile: dict):
    system_prompt = PROMPT_PATH.read_text()

    user_input = f"""
    Dataset profile:
    {json.dumps(profile, indent=2)}
    """

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_input}
        ],
        temperature=0
    )

    raw_output = response.choices[0].message.content.strip()

    # 🔒 Defensive guard
    if not raw_output.startswith("{"):
        raise ValueError(f"LLM did not return JSON:\n{raw_output}")

    try:
        parsed = json.loads(raw_output)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON from LLM:\n{raw_output}") from e

    # =====================================================
    # ✅ CRITICAL POST-PROCESSING (THIS FIXES YOUR ERROR)
    # =====================================================

    numeric_metrics = set(profile.get("numeric_metrics", []))

    # Keep only numeric metrics suggested by LLM
    llm_metrics = parsed.get("metrics", [])
    filtered_metrics = [m for m in llm_metrics if m in numeric_metrics]

    # Fallback: if LLM chose none correctly, use all numeric metrics
    if not filtered_metrics:
        filtered_metrics = list(numeric_metrics)

    parsed["metrics"] = filtered_metrics

    return parsed
