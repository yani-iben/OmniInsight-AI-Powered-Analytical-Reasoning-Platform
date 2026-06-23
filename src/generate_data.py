# src/generate_data.py
import duckdb
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def build_master_healthcare_data(num_days=730):
    print("Initializing OmniInsight Master Data Generation Suite...")
    
    # -------------------------------------------------------------
    # PART 1: GENERATE STRUCTURED COHORT DATA (Encounters & Vitals)
    # -------------------------------------------------------------
    con = duckdb.connect("data/analytics.duckdb")
    np.random.seed(42)
    num_encounters = 1000
    start_date = datetime(2026, 5, 1)
    
    encounter_ids = [10000 + i for i in range(num_encounters)]
    acuities = np.random.choice([1, 2, 3, 4, 5], p=[0.05, 0.25, 0.45, 0.20, 0.05], size=num_encounters)
    dispositions = []
    
    for ac in acuities:
        if ac in [1, 2]:
            dispositions.append(np.random.choice(["ICU", "Floor"], p=[0.3, 0.7]))
        elif ac == 3:
            dispositions.append(np.random.choice(["Floor", "Discharged"], p=[0.4, 0.6]))
        else:
            dispositions.append("Discharged")
            
    arrival_times_cohort = [start_date + timedelta(minutes=int(np.random.randint(0, 43200))) for _ in range(num_encounters)]
    
    bed_request_delays = [int(np.random.exponential(scale=(ac * 30))) for ac in acuities]
    bed_assignment_delays = [
        int(np.random.normal(loc=45, scale=15)) if disp == "ICU" 
        else int(np.random.normal(loc=180, scale=60)) if disp == "Floor" 
        else 0 for disp in dispositions
    ]
    
    df_encounters = pd.DataFrame({
        "encounter_id": encounter_ids,
        "acuity_level": acuities,
        "arrival_time": arrival_times_cohort,
        "disposition": dispositions
    })
    
    df_encounters['arrival_time'] = pd.to_datetime(df_encounters['arrival_time'])
    df_encounters['bed_request_time'] = df_encounters.apply(
        lambda r: r['arrival_time'] + timedelta(minutes=int(bed_request_delays[r.name])) if r['disposition'] != "Discharged" else None, axis=1
    )
    df_encounters['bed_assignment_time'] = df_encounters.apply(
        lambda r: r['bed_request_time'] + timedelta(minutes=int(bed_assignment_delays[r.name])) if r['disposition'] != "Discharged" else None, axis=1
    )
    df_encounters['total_los_minutes'] = df_encounters.apply(
        lambda r: bed_request_delays[r.name] + bed_assignment_delays[r.name] + int(np.random.randint(30, 120)) if r['disposition'] != "Discharged" else int(np.random.randint(60, 240)), axis=1
    )
    
    df_vitals = pd.DataFrame({
        "encounter_id": encounter_ids,
        "heart_rate": np.random.normal(loc=82, scale=15, size=num_encounters).astype(int),
        "temperature": np.random.normal(loc=98.6, scale=1.2, size=num_encounters).round(1),
        "pain_score": np.random.randint(0, 11, size=num_encounters)
    })
    
    con.execute("CREATE OR REPLACE TABLE ed_encounters AS SELECT * FROM df_encounters")
    con.execute("CREATE OR REPLACE TABLE triage_vitals AS SELECT * FROM df_vitals")
    print("Structured encounter tables built successfully inside DuckDB.")

    # -------------------------------------------------------------
    # PART 2: GENERATE VECTORIZED TIME-SERIES TRENDS (SCALED UP)
    # -------------------------------------------------------------
    time_axis = pd.date_range(start="2024-05-01", periods=num_days * 24, freq="H")
    df_time = pd.DataFrame({"arrival_time": time_axis})
    
    df_time["hour"] = df_time["arrival_time"].dt.hour
    df_time["day_of_week"] = df_time["arrival_time"].dt.dayofweek
    
    daily_seasonality = np.sin(2 * np.pi * df_time['hour'] / 24.0)
    weekend_effect = np.where(df_time['day_of_week'].isin([4, 5]), 1.5, 0.0)
    macro_trend = np.linspace(0, 2, len(df_time))
    random_noise = np.random.normal(0, 1, len(df_time))
    
    calculated_volume = 10 + (daily_seasonality * 5) + (weekend_effect * 4) + macro_trend + random_noise
    df_time['expected_patient_volume'] = np.round(calculated_volume).astype(int)
    
    con.execute("CREATE OR REPLACE TABLE hourly_operational_trends AS SELECT * from df_time")
    print(f"Generated {num_days} days of time-series data vectors.")
    con.close()

    # -------------------------------------------------------------
    # PART 3: GENERATE UNSTRUCTURED TEXT COGNITIVE MEMOS
    # -------------------------------------------------------------
    memos = [
        "SHIFT REPORT - MAY 5 - UNIT COORDINATOR MEMO:\nWe experienced significant boarding delays for admitted patients destined for Floor 3 and Floor 4 between 18:00 and 23:00. Floor beds were unavailable because housekeeping staff was down 50%, delaying room sanitation turns. This caused acuity level 2 and 3 patients to remain in ED bays, creating an access block for arriving ambulances.",
        
        "CLINICAL OPERATIONS EXCELLENCE REVIEW - Q2 BRIEF:\nAcuity level 2 cardiac panels are experiencing an average 45-minute workflow extension on weekend night shifts. Review of internal logs confirms that the main inpatient lab operates on a skeletal crew on Saturdays and Sundays. Lab processing bottlenecks directly delay physician bed requests.",
        
        "FACILITY METRICS EXPLAINER - TRANSPORT ISSUES:\nWhen analyzing length of stay variances for patients being admitted to medicine floors, the time gap between bed assignment and actual room arrival is widening. Internal investigation reveals that patient transport teams have an equipment deficit; specifically, telemetric rolling chairs are missing on the East Wing, forcing nurses to manually track down transport equipment."
    ]
    
    with open("data/operational_memos.txt", "w") as f:
        for memo in memos:
            f.write(memo + "\n\n=== DOCUMENT BREAK ===\n\n")
            
    print("Unstructured file 'data/operational_memos.txt' generated successfully.")
    print("Data Layer preparation complete!")

if __name__ == "__main__":
    build_master_healthcare_data(num_days=730)