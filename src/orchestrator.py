# src/orchestrator.py
import os
import sys
import duckdb
import pandas as pd
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv
from pinecone import Pinecone

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from compiler import SemanticSQLCompiler

class OmniInsightOrchestrator:
    def __init__(self, db_path="data/analytics.duckdb"):
        load_dotenv()
        self.con = duckdb.connect(db_path)
        self.encoder = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Pass the open database handle directly into the compiler constructor 
        self.compiler = SemanticSQLCompiler(active_con=self.con)
        
        api_key = os.getenv("PINECONE_API_KEY")
        index_name = os.getenv("PINECONE_INDEX_NAME")
        
        pc = Pinecone(api_key=api_key)
        self.cloud_index = pc.Index(index_name)

    def compile_nl_to_sql(self, user_input, history=None):
        """
        Pass-through bridge required by the asynchronous execution engine in app.py
        """
        return self.compiler.compile_nl_to_sql(user_input, history)

    def diagnose_facility_bottleneck(self, user_query):
        # 1. Run compiler to gather intent vectors
        sql_query, query_type = self.compiler.compile_nl_to_sql(user_query)
        
        # Create empty fallback tracking frames
        df_metrics = pd.DataFrame()
        
        # 2. Guardrail Route 1 Intercept: Glossary Terms (Conceptual Bypass)
        if query_type == "conceptual_bypass":
            metric_headline = "Semantic Intent Resolved: Mapping inquiry directly to cloud knowledge maps."
            query_vector = self.encoder.encode([user_query]).tolist()
            cloud_response = self.cloud_index.query(vector=query_vector, top_k=1, include_metadata=True)
            
            log_match = "No explicit dictionary definition matches this term in reference documentation."
            if cloud_response and cloud_response['matches']:
                log_match = cloud_response['matches'][0]['metadata']['text_log']
                
            recommendation = "1. Staff Education: Ensure incoming coordinators reference standard clinical terminology indexes.\n2. Parameter Compliance: Note that severity scoring dictates operational prioritization queues."
            return metric_headline, log_match, recommendation, df_metrics

        # 3. Guardrail Route 2 Intercept: Assistant Workspace Tasks
        if query_type == "assistant_bypass":
            metric_headline = "Administrative coordinator workspace activated."
            if "email" in user_query.lower() or "write" in user_query.lower():
                log_match = "Draft Memo for Clinical Leadership Staff\n\nSubject: Urgent Operational Notification - Active Throughput Constraints\n\nTeam,\nPlease be advised that system telemetry indicates elevated boarding delays across high-urgency units. We are currently observing structural flow constraints specifically during peak shift changes.\n\nAction Items:\n1. Coordinate directly with unit charge nurses to expedite pending clearances.\n2. Review floating clinical resource models to optimize patient decompression paths."
            else:
                log_match = "Hello! I am your embedded clinical intelligence assistant. You can ask me to evaluate operational data sets, cross-reference shift logs, or help draft shift memos based on facility trends."
                
            recommendation = "1. Export Utility: Copy the generated text block above directly into your internal messaging portals.\n2. Verify Metrics: Return to data-driven inquiries to cross-examine specific ward counts."
            return metric_headline, log_match, recommendation, df_metrics

        # 4. Standard Quantitative Data Processing Route
        df_metrics = self.con.execute(sql_query).fetchdf()
        
        if query_type == "hourly_trend":
            metric_headline = "Time-Series Throughput Dynamics: Analytics sorted by 24-hour cycle operations."
            log_search_term = "peak operational hourly volumes capacity constraints shift crossover"
            recommendation = "1. Adjust Rosters: Dynamically scale staffing caps during flagged peak hourly blocks.\n2. Deflect Influx: Route non-critical arrivals to secondary local networks."
        else:
            metric_headline = "Departmental Operational Breakdown: Baseline capacity utilization indicators."
            log_search_term = "general facility operations workflow logs"
            recommendation = "1. Clear Boarding Lanes: Audit active discharges immediately to open physical unit beds.\n2. Parameter Compliance: Optimize shift handover operational queues."
            
        # 5. Core Cloud Vector Match Lookup (Pinecone Integration)
        search_vector = self.encoder.encode([log_search_term]).tolist()
        cloud_response = self.cloud_index.query(vector=search_vector, top_k=1, include_metadata=True)
        
        log_match = "No shift coordination logs explicitly detail issues occurring during this exact threshold."
        if cloud_response and cloud_response['matches']:
            log_match = cloud_response['matches'][0]['metadata']['text_log']

        return metric_headline, log_match, recommendation, df_metrics