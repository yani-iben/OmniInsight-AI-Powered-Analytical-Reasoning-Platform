import duckdb
import pandas as pd
import numpy as np

con = duckdb.connect("data/analytics.duckdb")

con.execute("DROP TABLE IF EXISTS ed_encounters;")

# Create the full multi-dimensional schema
con.execute("""
    CREATE TABLE ed_encounters (
        encounter_id INTEGER,
        hour INTEGER,
        disposition VARCHAR,
        avg_los_minutes DOUBLE,
        total_patients INTEGER,
        avg_volume DOUBLE,
        peak_volume DOUBLE
    );
""")

# Seed mock rows so your charts actually have contents to group by
mock_data = {
    "encounter_id": range(1, 25),
    "hour": list(range(24)),
    "disposition": ["Floor", "ICU", "Discharged"] * 8,
    "avg_los_minutes": np.random.randint(45, 360, size=24).astype(float),
    "total_patients": np.random.randint(10, 150, size=24).astype(int),
    "avg_volume": np.random.randint(5, 50, size=24).astype(float),
    "peak_volume": np.random.randint(10, 80, size=24).astype(float)
}

df = pd.DataFrame(mock_data)
con.execute("INSERT INTO ed_encounters SELECT * FROM df;")
con.close()
print("Database cleanly generated with all tracking dimensions!")