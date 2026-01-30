import streamlit as st
import pandas as pd
import json

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


# --------------------------------------------------
# Page config
# --------------------------------------------------
st.set_page_config(
    page_title="Retail Insights Assistant",
    layout="centered"
)

st.title("🧠 Retail Insights Assistant")
st.caption("GenAI-powered conversational analytics for retail data")


# --------------------------------------------------
# Session State
# --------------------------------------------------
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "memory" not in st.session_state:
    st.session_state.memory = ConversationMemory()

if "semantic_schema" not in st.session_state:
    st.session_state.semantic_schema = None

if "db_conn" not in st.session_state:
    st.session_state.db_conn = None


# --------------------------------------------------
# Dataset Upload (TOP)
# --------------------------------------------------
st.subheader("📁 Upload Dataset")

uploaded_file = st.file_uploader(
    "Upload a sales CSV or Excel file",
    type=["csv", "xlsx"]
)

if uploaded_file:
    with st.spinner("Loading dataset..."):
        file_type = detect_file_type(uploaded_file.name)
        raw_data = load_data(uploaded_file, file_type)

        profile = profile_input(raw_data)
        semantic_schema = generate_semantic_schema(profile)

        st.session_state.semantic_schema = semantic_schema
        st.session_state.db_conn = create_duckdb_connection(raw_data)

    st.success("Dataset loaded successfully. You can start chatting 👇")


# --------------------------------------------------
# Chat History (MIDDLE – scrollable)
# --------------------------------------------------
st.divider()

chat_container = st.container()

with chat_container:
    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])


# --------------------------------------------------
# Chat Input (BOTTOM)
# --------------------------------------------------
if st.session_state.semantic_schema:

    user_input = st.chat_input(
        "Ask a business question or request a summary…"
    )

    if user_input:
        # Add user message
        st.session_state.chat_history.append(
            {"role": "user", "content": user_input}
        )

        with st.spinner("Analyzing..."):
            mode = detect_mode(user_input)

            # ===========================
            # SUMMARIZATION MODE
            # ===========================
            if mode == "summarization":
                summary_intents = generate_summary_intents(
                    st.session_state.semantic_schema
                )

                results = {}
                for item in summary_intents:
                    sql = build_sql_query(item["intent"], "sales")
                    results[item["name"]] = execute_query(
                        st.session_state.db_conn, sql
                    )

                summary_facts = assemble_summary_results(results)

                answer = generate_explanation(
                    user_input,
                    summary_facts
                )

            # ===========================
            # Q&A MODE
            # ===========================
            else:
                intent_response = extract_query_intent(
                    user_input,
                    st.session_state.semantic_schema
                )

                if intent_response.get("status") != "valid":
                    answer = (
                        intent_response.get("reason", "")
                        + "\n\n"
                        + intent_response.get("suggestion", "")
                    )
                else:
                    current_intent = intent_response["intent"]

                    merged_intent = merge_with_previous_intent(
                        current_intent,
                        st.session_state.memory.get_last_intent()
                    )

                    merged_intent = resolve_time_followup(
                        user_input,
                        merged_intent,
                        st.session_state.semantic_schema
                    )

                    st.session_state.memory.update_intent(merged_intent)

                    sql = build_sql_query(merged_intent, "sales")
                    result_df = execute_query(
                        st.session_state.db_conn, sql
                    )

                    reasoning = apply_business_reasoning(
                        merged_intent,
                        result_df
                    )

                    answer = generate_explanation(
                        user_input,
                        reasoning
                    )

        # Add assistant message
        st.session_state.chat_history.append(
            {"role": "assistant", "content": answer}
        )

        # Rerender to show latest message immediately
        st.rerun()
