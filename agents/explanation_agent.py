import json
from pathlib import Path
from config.llm_config import get_openai_client

client = get_openai_client()
PROMPT_PATH = Path("prompts/explanation_prompt.txt")

def generate_explanation(original_question: str, reasoning_output: dict) -> str:
    system_prompt = PROMPT_PATH.read_text()
    safe_facts = compress_facts_for_llm(reasoning_output)
    user_input = f"""
    User question:
    {original_question}

    Analysis result:
    {json.dumps(safe_facts, indent=2)}
    """

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_input}
        ],
        temperature=0.2
    )

    return response.choices[0].message.content.strip()
def compress_facts_for_llm(facts: dict, max_items: int = 3) -> dict:
    """
    Reduce summary facts to a small, LLM-safe structure.
    """
    compressed = {}

    for key, value in facts.items():
        # Single numeric value
        if isinstance(value, (int, float)):
            compressed[key] = value

        # List of records (grouped results)
        elif isinstance(value, list) and value:
            compressed[key] = {
                "top": value[:max_items],
                "count": len(value)
            }

        # Dict (already compact)
        elif isinstance(value, dict):
            compressed[key] = value

    return compressed