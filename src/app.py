# src/app.py
import os
import sys
import importlib.util
import streamlit as str_layout 
import pandas as pd
import duckdb
import plotly.express as px

# IMPORT ASYNC UTILITIES
import asyncio
from concurrent.futures import ThreadPoolExecutor

# Safe path fix for orchestrator
current_dir = os.path.dirname(os.path.abspath(__file__))
orchestrator_path = os.path.join(current_dir, "orchestrator.py")
spec = importlib.util.spec_from_file_location("orchestrator", orchestrator_path)
orchestrator_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(orchestrator_module)
OmniInsightOrchestrator = orchestrator_module.OmniInsightOrchestrator

str_layout.set_page_config(page_title="OmniInsight Diagnostic Hub", layout="wide")

str_layout.title("OmniInsight Operational Command Center")
str_layout.markdown("### *Dynamic Facility Diagnostics: Driving Text Logs from Real Numbers*")
str_layout.markdown("---")

@str_layout.cache_resource
def init_orchestrator():
    return OmniInsightOrchestrator()

orchestrator = init_orchestrator()
con = duckdb.connect("data/analytics.duckdb")

# INITIALIZE BACKGROUND WORKER THREAD POOL
if "executor" not in str_layout.session_state:
    str_layout.session_state.executor = ThreadPoolExecutor(max_workers=3)

if "query_history" not in str_layout.session_state:
    str_layout.session_state.query_history = {}

# THE ASYNC PIPELINE COORDINATOR GOES HERE
async def run_analytics_pipeline(prompt, history):
    """
    Offloads heavy compilation logic and state transitions to the background executor
    pool, preventing compute lag from freezing the main UI thread.
    """
    loop = asyncio.get_running_loop()
    sql_query, updated_history = await loop.run_in_executor(
        str_layout.session_state.executor, orchestrator.compile_nl_to_sql, prompt, history
    )
    return sql_query, updated_history

# Global Operational Search Engine Bar
str_layout.markdown("#### 💬 Global Operational Search Engine")
user_prompt = str_layout.text_input(
    "Type an operational problem, department, or query to audit facility health:",
    value="Show me wait times for our ICU department",
    placeholder="e.g., who is discharged, what is their wait time..."
)

if user_prompt:
    # EXECUTE THE ASYNC WORKER FROM THE UI LOOP
    # We use asyncio.run to safely block the UI *only* while the worker completes its job
    sql_query, updated_history = asyncio.run(run_analytics_pipeline(user_prompt, str_layout.session_state.query_history))
    
    # Update state history logs
    str_layout.session_state.query_history = updated_history
    
    # Control Flow Guardrail
    if sql_query in ["CONCEPTUAL_INQUIRY_BYPASS", "ASSISTANT_INQUIRY_BYPASS"]:
        df_metrics = pd.DataFrame()
    else:
        df_metrics = con.execute(sql_query).fetchdf()
    
    # Process the backend diagnostic metrics and text logs
    headline, matched_log, action_plan = orchestrator.diagnose_facility_bottleneck(user_prompt, sql_query)
    
    str_layout.markdown("---")
    
    # MAIN PANEL DISPLAY
    col_visual, col_diagnosis = str_layout.columns([3, 2])
    
    with col_visual:
        str_layout.subheader("Live Performance Analytics")
        
        if sql_query == "CONCEPTUAL_INQUIRY_BYPASS":
            str_layout.info("**Knowledge Base Layer Active**\n\nYour query requires an institutional glossary lookup rather than a numerical calculation. The analytics dashboard has dynamically pivoted to scan unstructured administrative files.")
        elif sql_query == "ASSISTANT_INQUIRY_BYPASS":
            str_layout.success(" Assistant Workspace Active: Directing output tracking into operational text summaries.")
        elif "avg_los_minutes" in df_metrics.columns:
            if "acuity_level" in df_metrics.columns:
                dest_col = "destination" if "destination" in df_metrics.columns else "disposition"
                fig = px.bar(df_metrics, x="acuity_level", y="avg_los_minutes", color=dest_col, barmode="group",
                             title="Length of Stay (Minutes) by Patient Urgency & Tracked Unit")
            else:
                dest_col = "disposition" if "disposition" in df_metrics.columns else df_metrics.columns[0]
                fig = px.bar(df_metrics, x=dest_col, y="avg_los_minutes", color=dest_col,
                             title="Average Length of Stay (Minutes) by Department")
            str_layout.plotly_chart(fig, use_container_width=True)
        elif "peak_volume" in df_metrics.columns:
            fig = px.line(df_metrics, x="hour", y="avg_volume", title="Hourly Volume Demands", labels={"avg_volume": "Avg Patients/Hr"})
            fig.update_traces(line_color='#FF4B4B', line_width=2)
            str_layout.plotly_chart(fig, use_container_width=True)
        else:
            str_layout.dataframe(df_metrics, use_container_width=True, hide_index=True)
            
    with col_diagnosis:
        str_layout.subheader("System Diagnostic Summary")
        str_layout.warning(f"**Metric Anomaly Flagged:**\n{headline}")
        str_layout.info(f"**Verifiable Log Evidence (FAISS Match):**\n\n{matched_log}")
        str_layout.success(f"**Prescriptive Action Plan:**\n\n{action_plan}")

con.close()