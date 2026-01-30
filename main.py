import json
import pandas as pd

# --- Core imports ---
from core.file_detector import detect_file_type
from core.loader import load_data
from core.profiler import profile_input
from core.semantic_schema import generate_semantic_schema

from db.duckdb_conn import create_duckdb_connection

from agents.mode_detection_agent import detect_mode
from agents.intent_extraction_agent import extract_query_intent
from agents.intent_merge import merge_with_previous_intent
from agents.data_extraction_agent import build_sql_query, execute_query
from agents.validation_reasoning_agent import apply_business_reasoning
from agents.explanation_agent import generate_explanation
from agents.summarization_agent import (
    generate_summary_intents,
    assemble_summary_results,
)

from memory.conversation_memory import ConversationMemory
from agents.time_followup_resolver import resolve_time_followup


# -------------------------------
# CONFIG
# -------------------------------
DATASET_PATH = r"data\P  L March 2021.csv"
TABLE_NAME = "sales"


# -------------------------------
# LOAD DATA + SCHEMA
# -------------------------------
print("\n🔹 Loading dataset...")
file_type = detect_file_type(DATASET_PATH)
raw_data = load_data(DATASET_PATH, file_type)

if not isinstance(raw_data, pd.DataFrame):
    raise ValueError("This demo supports tabular datasets only (CSV / Excel).")

profile = profile_input(raw_data)
semantic_schema = generate_semantic_schema(profile)

with open("schemas/semantic_schema.json", "w") as f:
    json.dump(semantic_schema, f, indent=2)

print("\n✅ Semantic Schema Detected:")
print(json.dumps(semantic_schema, indent=2))


# -------------------------------
# SETUP DB + MEMORY
# -------------------------------
con = create_duckdb_connection(raw_data)
memory = ConversationMemory()


# -------------------------------
# INTERACTIVE LOOP
# -------------------------------
print("\n🧠 Retail Insights Assistant Ready")
print("Type 'exit' to quit.\n")

while True:
    user_input = input("User: ").strip()

    if user_input.lower() in ["exit", "quit"]:
        print("👋 Exiting.")
        break

    # ---------------------------
    # MODE DETECTION
    # ---------------------------
    mode = detect_mode(user_input)

    # ===========================
    # SUMMARIZATION MODE
    # ===========================
    if mode == "summarization":
        print("\n[Mode: Summarization]\n")

        summary_intents = generate_summary_intents(semantic_schema)
        results = {}

        for item in summary_intents:
            sql = build_sql_query(item["intent"], TABLE_NAME)
            results[item["name"]] = execute_query(con, sql)

        summary_facts = assemble_summary_results(results)

        final_answer = generate_explanation(
            user_input,
            summary_facts
        )

        print("Assistant:", final_answer)
        continue

    # ===========================
    # Q&A MODE
    # ===========================
    print("\n[Mode: Q&A]\n")

    intent_response = extract_query_intent(user_input, semantic_schema)

    # Handle invalid / infeasible intent
    if intent_response.get("status") != "valid":
        print("Assistant:", intent_response.get("reason"))
        print("Suggestion:", intent_response.get("suggestion"))
        continue

    current_intent = intent_response["intent"]

    # ✅ Merge with conversation memory (ONLY HERE)
    merged_intent = merge_with_previous_intent(
        current_intent,
        memory.get_last_intent()
    )
    merged_intent["time_fields"] = semantic_schema.get("time_fields", [])

    # Update memory
    memory.update_intent(merged_intent)
    merged_intent = resolve_time_followup(
    user_input,
    merged_intent,
    semantic_schema
    )
    
    # STEP 3: SQL
    sql = build_sql_query(merged_intent, TABLE_NAME)
    result_df = execute_query(con, sql)

    # STEP 4: Reasoning
    reasoning_output = apply_business_reasoning(merged_intent, result_df)

    if reasoning_output.get("status") != "success":
        print("Assistant:", reasoning_output.get("message"))
        continue

    # STEP 5: Explanation
    final_answer = generate_explanation(
        user_input,
        reasoning_output
    )

    print("Assistant:", final_answer)
