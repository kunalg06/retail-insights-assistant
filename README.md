# 🧠 Retail Insights Assistant  
**GenAI-Powered Conversational Analytics for Retail Data**

## 📌 Overview

The Retail Insights Assistant is a GenAI-powered system that enables business users to analyze retail datasets using natural language queries.
It supports:

- Conversational Q&A (e.g., “Which category is underperforming?”)
- Automated summarization (e.g., “Summarize overall stock performance”)
- Follow-up questions with conversation memory
- Schema-aware, safe SQL generation
- Scalable architecture suitable for 100GB+ datasets (design level)

The system combines data engineering, LLM reasoning, and a multi-agent architecture to deliver reliable insights over real-world retail data.

## ✨ Key Features

- 📁 Accepts CSV / Excel retail datasets
- 💬 ChatGPT-like conversational interface (Streamlit)
- 🧠 Multi-agent design:
    - Mode Detection
    - Intent Extraction
    - Data Extraction (SQL)
    - Validation & Reasoning
    - Explanation & Summarization
- 🧾 Semantic schema generation (automatic, dataset-aware)
- 🛡️ Safe SQL execution (numeric casting, validation)
- ♻️ Conversation memory for follow-ups
- 📊 Summarization & Q&A use the same pipeline 

## 🏗️ Project Structure
```
retail-insights-assistant/
│
├── app.py                     # Streamlit Chat UI
├── main.py                    # CLI runner (optional)
├── requirements.txt
├── .env                       # OpenAI API key
│
├── core/
│   ├── loader.py              # CSV / Excel loader
│   ├── profiler.py            # Dataset profiling
│   ├── semantic_schema.py     # LLM-based schema generation
│   └── file_detector.py
│
├── agents/
│   ├── mode_detection_agent.py
│   ├── intent_extraction_agent.py
│   ├── intent_merge.py
│   ├── data_extraction_agent.py
│   ├── validation_reasoning_agent.py
│   ├── summarization_agent.py
│   ├── explanation_agent.py
│   └── time_followup_resolver.py
│
├── memory/
│   └── conversation_memory.py
│
├── db/
│   └── duckdb_conn.py
│
├── prompts/
│   ├── semantic_schema_prompt.txt
│   └── intent_extraction_prompt.txt
│
└── data/
    └── sample_sales.csv
```
## ⚙️ Environment Setup

### Clone repository
```
git clone <repo-url>
cd retail-insights-assistant
```

### Create virtual environment
```
python -m venv venv
venv\Scripts\activate
```

### Install dependencies
```
pip install -r requirements.txt
```

## 🔑 OpenAI API Key

Create a `.env` file:

```
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxx
```

## ▶️ Run Application

```
streamlit run app.py
```
## 💬 Example Questions

- Which category has the highest stock?
- Which SKU is underperforming?
- Show stock distribution by size
- Summarize overall performance

## 🧠 How the System Works (High Level)

1. Dataset Profiling
    - Detects numeric vs categorical columns
2. Semantic Schema Generation (LLM)
    - Identifies metrics, dimensions, grain
    - Enforced with rule-based validation
3. Mode Detection
    - Summarization vs Q&A
4. Intent Extraction
    - Converts natural language → structured intent
5. SQL Generation
    - Safe, validated DuckDB queries
6. Business Reasoning
    - Top / bottom / distribution logic
7. LLM Explanation
    - Compressed facts → natural language insights
8. Conversation Memory
    - Enables follow-up questions safely
    
## 📊 Scalability

While the demo runs locally, the architecture supports scaling via:
- Parquet / Delta Lake storage
- Cloud data lakes (S3, GCS, ADLS)
- Spark / Databricks / BigQuery
- Column pruning & SQL pushdown
- Minimal LLM token usage (facts only)

## 🛡️Safety & Reliability
- No raw data sent to LLM
- Numeric casting for dirty CSVs
- Feasibility validation (time, metrics)
- Graceful error handling
- Token compression to avoid rate limits

## 📸 Demo Evidence (Recommended)

For submission screenshots:

- Dataset uploaded successfully
![alt text](imgs\Datasetupload.png)

- Q&A example
![alt text](imgs\Q&A.png)

- Follow-up question
![alt text](imgs\followup.png)

- Summarization output
![alt text](imgs\Summary.png)

## ⚠️ Assumptions & Limitations

- Time-based analysis requires a date column
- YoY / QoQ analysis depends on data availability
- Vector search is optional (not required for this assignment)

## 🚀 Future Improvements

- Add Streamlit filters & charts
- Integrate vector DB for report similarity
- Deploy on cloud (AWS / GCP / Azure)
- Add role-based access & logging

## ✅ Conclusion
A production-ready GenAI retail analytics assistant.
