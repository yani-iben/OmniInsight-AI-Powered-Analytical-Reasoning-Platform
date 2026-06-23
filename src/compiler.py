# src/compiler.py
import re

class SemanticSQLCompiler:
    def __init__(self):
        pass

    def compile_nl_to_sql(self, user_input, history=None):
        """
        Adaptive SQL Compiler with Context Inheritance.
        """
        input_lower = user_input.lower()
        history = history or {}
        
        if any(w in input_lower for w in ["write", "email", "summarize", "hello", "hi ", "help", "thank"]):
            return "ASSISTANT_INQUIRY_BYPASS", history
        
        if any(w in input_lower for w in ["what is", "what are", "meaning of", "define", "explain"]):
            return "CONCEPTUAL_INQUIRY_BYPASS", history

        # Extract Active Parameters from Current Input
        current_destination = None
        if "discharg" in input_lower: current_destination = "Discharged"
        elif "icu" in input_lower: current_destination = "ICU"
        elif "floor" in input_lower: current_destination = "Floor"
        
        current_acuity = None
        for num in ["1", "2", "3", "4", "5"]:
            if f"acuity {num}" in input_lower or f"level {num}" in input_lower or f"urgency {num}" in input_lower:
                current_acuity = num

        # CONTEXT PERSISTENCE TRIGGER (Pronoun Resolution)
        # If the user uses a pronoun like "their", "them", or "they", look at history
        if any(p in input_lower for p in ["their", "them", "they", "those", "that shift"]):
            if not current_destination and "last_destination" in history:
                current_destination = history["last_destination"]
            if not current_acuity and "last_acuity" in history:
                current_acuity = history["last_acuity"]

        # Update running history state
        if current_destination: history["last_destination"] = current_destination
        if current_acuity: history["last_acuity"] = current_acuity

        # Build the SQL Query dynamically based on resolved states
        hour_match = re.search(r'(?:hour\s*|at\s*)(\d+)', input_lower)
        
        if any(w in input_lower for w in ["wait", "stay", "acuity", "boarding", "who", "show", "list"]) or current_destination or current_acuity:
            base_select = """
            SELECT 
                disposition as destination,
                acuity_level,
                COUNT(*) as total_patients,
                ROUND(AVG(total_los_minutes), 1) as avg_los_minutes,
                ROUND(quantile_cont(total_los_minutes, 0.90), 1) as p90_los_minutes
            FROM ed_encounters
            """
            filters = []
            if current_destination:
                filters.append(f"disposition = '{current_destination}'")
            if current_acuity:
                filters.append(f"acuity_level = {current_acuity}")

            if filters:
                sql_query = base_select + " WHERE " + " AND ".join(filters)
            else:
                return "SELECT disposition, COUNT(*) as total_patients, ROUND(AVG(total_los_minutes), 1) as avg_los_minutes FROM ed_encounters GROUP BY disposition;", history
            
            sql_query += "\nGROUP BY disposition, acuity_level\nORDER BY avg_los_minutes DESC;"
            return sql_query, history
            
        elif hour_match:
            target_hour = hour_match.group(1)
            return f"SELECT hour, ROUND(AVG(expected_patient_volume), 1) as avg_volume, MAX(expected_patient_volume) as peak_volume FROM hourly_operational_trends WHERE hour = {target_hour} GROUP BY hour;", history
            
        else:
            return "SELECT hour, ROUND(AVG(expected_patient_volume), 1) as avg_volume, MAX(expected_patient_volume) as peak_volume FROM hourly_operational_trends WHERE day_of_week IN (4, 5) GROUP BY hour ORDER BY hour ASC;", history