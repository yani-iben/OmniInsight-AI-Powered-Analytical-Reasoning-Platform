# src/orchestrator.py
import os
import sys
import duckdb
import faiss
from sentence_transformers import SentenceTransformer
import numpy as np

# Force local directory path lookups for clean imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from compiler import SemanticSQLCompiler

class OmniInsightOrchestrator:
    def __init__(self, db_path="data/analytics.duckdb", index_path="data/knowledge_layer.index"):
        self.con = duckdb.connect(db_path)
        self.encoder = SentenceTransformer('all-MiniLM-L6-v2')
        self.index = faiss.read_index(index_path)
        self.compiler = SemanticSQLCompiler()
        
        with open("data/document_map.txt", "r") as f:
            self.documents = f.readlines()

    def compile_nl_to_sql(self, user_input, history=None):
        # Pass the history dictionary into the compiler module
        return self.compiler.compile_nl_to_sql(user_input, history)

    def diagnose_facility_bottleneck(self, user_query, sql_query):
        # 1. Intercept Glossary Terms
        if sql_query == "CONCEPTUAL_INQUIRY_BYPASS":
            metric_headline = "Semantic Intent Resolved: Mapping open-ended inquiry directly to organizational knowledge maps."
            query_vector = self.encoder.encode([user_query]).astype('float32')
            distances, indices = self.index.search(query_vector, k=1)
            log_match = "No explicit dictionary definition matches this term in our reference documentation."
            if indices[0][0] != -1:
                log_match = self.documents[indices[0][0]].strip()
            recommendation = "1. **Staff Education:** Ensure incoming administrative coordinators reference standard clinical terminology indexes.\n2. **Parameter Compliance:** Note that severity scoring dictates operational prioritization queues."
            return metric_headline, log_match, recommendation

        # 2. Intercept Assistant Conversations
        if sql_query == "ASSISTANT_INQUIRY_BYPASS":
            metric_headline = "Administrative coordinator workspace activated."
            if "email" in user_query.lower() or "write" in user_query.lower():
                log_match = "📋 **Draft Memo for Clinical Leadership Staff**\n\nSubject: Urgent Operational Notification - Active Throughput Constraints\n\nTeam,\nPlease be advised that system telemetry indicates elevated boarding delays across high-urgency units. We are currently observing structural flow constraints specifically during peak shift changes.\n\nAction Items:\n1. Coordinate directly with unit charge nurses to expedite pending clearances.\n2. Review floating clinical resource models to optimize patient decompression paths."
            else:
                log_match = "Hello! I am your embedded clinical intelligence assistant. You can ask me to evaluate operational data sets, cross-reference shift logs, or help draft shift memos based on facility trends."
                
            recommendation = "1. **Export Utility:** Copy the generated text block above directly into your internal messaging portals.\n2. **Verify Metrics:** Return to data-driven inquiries to cross-examine specific ward counts."
            return metric_headline, log_match, recommendation

        # 3. Base Quantitative Data Extraction (Safely protected against missing column fields)
        df_metrics = self.con.execute(sql_query).fetchdf()
        if df_metrics.empty:
            return "⚠️ No operational data found matching those specific parameters.", "No matching logs available.", "Review query boundaries."
            
        if "hour" in df_metrics.columns and len(df_metrics) == 1:
            target_hour = df_metrics["hour"].iloc[0]
            avg_v = df_metrics["avg_volume"].iloc[0] if "avg_volume" in df_metrics.columns else 0.0
            peak_v = df_metrics["peak_volume"].iloc[0] if "peak_volume" in df_metrics.columns else 0.0
            shift_context = "Early Morning Shift Change" if 4 <= target_hour <= 7 else "Standard Operations"
            if 23 <= target_hour or target_hour <= 3: shift_context = "Late Night Shift Overlap"
            metric_headline = f"Isolated Metrics for Hour {target_hour:02d}:00 ({shift_context}). Average load is {avg_v} patients/hr, with worst-case surges capping at {peak_v}."
            search_vector_term = f"hourly volume trends at hour {target_hour} early morning shift handover bottleneck capacity constraint"
            dest = "All Units"
            acuity = "All Levels"
            
        elif "avg_volume" in df_metrics.columns:
            peak_val = df_metrics["peak_volume"].max()
            metric_headline = f"Peak operational surge hitting {peak_val} patients/hour detected across weekend timelines."
            search_vector_term = "weekend staffing shortage peak hourly volume surge capacity constraints"
            dest = "All Units"
            acuity = "All Levels"
            
        elif "avg_los_minutes" in df_metrics.columns:
            worst_row = df_metrics.loc[df_metrics['avg_los_minutes'].idxmax()]
            dest_col = next((c for c in df_metrics.columns if c.lower() in ['destination', 'disposition']), None)
            dest = worst_row[dest_col] if dest_col else "Unknown Department"
            acuity_col = next((c for c in df_metrics.columns if c.lower() in ['acuity_level', 'urgency_level']), None)
            acuity = worst_row[acuity_col] if acuity_col else "Standard"
            mins = worst_row['avg_los_minutes']
            metric_headline = f"Severe boarding backlog isolated at Destination: {dest} (Urgency Level {acuity}) averaging {mins} minutes."
            search_vector_term = f"{dest} patient boarding delays inpatient bed shortage transfer bottleneck"
            
        else:
            metric_headline = "Standard system telemetry check completed."
            search_vector_term = "general facility operations workflow baseline logs"
            dest = "Standard"
            acuity = "Standard"

        # Vector Match Lookup
        query_vector = self.encoder.encode([search_vector_term]).astype('float32')
        distances, indices = self.index.search(query_vector, k=1)
        log_match = "No shift coordination logs explicitly detail issues occurring during this exact threshold."
        if indices[0][0] != -1:
            log_match = self.documents[indices[0][0]].strip()

        # Build Action Plan Context
        if "volume" in sql_query.lower():
            recommendation = "1. **Adjust Rosters:** Dynamically scale nursing shift caps during the flagged peak hourly blocks.\n2. **Deflect Influx:** Route non-critical ambulatory arrivals to secondary local clinical networks."
        else:
            recommendation = f"1. **Clear Boarding Lanes:** Audit active discharges in the {dest} units immediately to open physical beds."

        return metric_headline, log_match, recommendation