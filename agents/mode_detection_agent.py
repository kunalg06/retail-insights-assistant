from pathlib import Path
from config.llm_config import get_openai_client

client = get_openai_client()
PROMPT_PATH = Path("prompts/mode_detection_prompt.txt")

SUMMARY_KEYWORDS = [
    "summary", "summarize", "overview", "performance",
    "insights", "trend", "high level", "overall"
]

def detect_mode(user_input: str) -> str:
    text = user_input.lower()

    # Rule-based fast path
    if any(keyword in text for keyword in SUMMARY_KEYWORDS):
        return "summarization"

    # LLM fallback
    system_prompt = PROMPT_PATH.read_text()

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_input}
        ],
        temperature=0
    )

    mode = response.choices[0].message.content.strip()

    if mode not in ["summarization", "qa"]:
        raise ValueError(f"Invalid mode returned by LLM: {mode}")

    return mode
