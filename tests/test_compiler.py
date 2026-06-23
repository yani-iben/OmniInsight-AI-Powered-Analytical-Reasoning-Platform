import pytest
from src.orchestrator import OmniInsightOrchestrator

def test_semantic_router_icu_extraction():
    orchestrator = OmniInsightOrchestrator(db_path="data/analytics.duckdb")
    query = "Show me wait times for ICU"
    sql = orchestrator.compile_nl_to_sql(query)
    
    assert "disposition = 'ICU'" in sql
    assert "SELECT" in sql