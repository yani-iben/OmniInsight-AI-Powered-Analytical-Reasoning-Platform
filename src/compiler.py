# src/compiler.py
import duckdb

class SemanticSQLCompiler:
    def __init__(self, active_con=None):
        if active_con is not None:
            try:
                self.columns = [row[0].lower() for row in active_con.execute("PRAGMA table_info('ed_encounters');").fetchall()]
            except Exception:
                self.columns = []
        else:
            self.columns = []
            
        # Hardcoded fallback safety fields MUST match your full mock schema structure!
        if not self.columns or "hour" not in self.columns:
            self.columns = ["encounter_id", "hour", "disposition", "avg_los_minutes", "total_patients"]
    def compile_nl_to_sql(self, user_input, history=None):
        query_clean = user_input.lower().strip()
        
        # 1. Dynamically discover what the time column is actually named
        # Checks if it's 'hour', 'encounter_hour', 'arrival_time', etc.
        time_col = "hour"
        for col in self.columns:
            if "hour" in col or "time" in col:
                time_col = col
                break
                
        # 2. Dynamically discover the tracking metrics columns
        los_col = next((c for c in self.columns if "los" in c or "stay" in c), "avg_los_minutes")
        vol_col = next((c for c in self.columns if "patient" in c or "volume" in c or "count" in c), "total_patients")
        disp_col = next((c for c in self.columns if "disp" in c or "dept" in c or "unit" in c), "disposition")

        # Guardrail Route 1: Check for open-ended terminology lookups
        if any(word in query_clean for word in ["what is", "define", "glossary", "meaning", "acuity level"]):
            return "CONCEPTUAL_INQUIRY_BYPASS", "conceptual_bypass"
            
        # Guardrail Route 2: Check for administrative workspace tasks
        if any(word in query_clean for word in ["write", "email", "memo", "assistant", "draft"]):
            return "ASSISTANT_INQUIRY_BYPASS", "assistant_bypass"

        # Route 3: Volumetric Time-Series Trend Inquiries (Using Resolved Columns)
        if any(word in query_clean for word in ["when", "time", "hour", "trend", "peak"]):
            digits = [int(s) for s in query_clean.split() if s.isdigit()]
            if digits:
                target_hour = digits[0] % 24
                return f"SELECT {time_col} as hour, avg_volume, peak_volume, {vol_col} as total_patients, {los_col} as avg_los_minutes FROM ed_encounters WHERE {time_col} = {target_hour}", "hourly_trend"
            
            return f"SELECT {time_col} as hour, AVG({los_col}) as avg_los_minutes, SUM({vol_col}) as total_patients FROM ed_encounters GROUP BY {time_col} ORDER BY {time_col}", "hourly_trend"

        # Default Fallback Route: Departmental Breakdowns
        return f"SELECT {disp_col} as disposition, AVG({los_col}) as avg_los_minutes, SUM({vol_col}) as total_patients FROM ed_encounters GROUP BY {disp_col}", "department_breakdown"