
import random

departments = ["ICU", "Discharged", "Floor", "Pediatrics", "Emergency Ward", "Radiology", "Cardiology"]

# Expanded dictionary matrices to dynamically construct thousands of unique sentences
subjects = [
    "Skeletal nursing rosters", "Critical equipment down-time", "Delayed lab turnarounds", 
    "Acuity level mismatching", "Severe physical bed lock", "Electronic EHR system latency",
    "Ambulance diversion bottlenecks", "Ancillary staff shortages"
]

actions = [
    "is driving massive throughput constraints", "has triggered localized boarding backlogs",
    "is creating severe communication handoff gaps", "is slowing down active physician clearances",
    "is extending patient length of stay by roughly 45 minutes", "is compromising discharge velocity"
]

reasons = [
    "due to weekend skeletal lab staffing models.", "following an unpredicted surge in high-urgency admissions.",
    "exacerbated by manual paper backup logging protocols.", "related to delayed deep-cleaning room turnarounds.",
    "coinciding with peak shift crossover transitions."
]

print("Generating 10,000 highly distinct operational memos...")

with open("data/document_map.txt", "w") as f:
    for i in range(10000):
        dept = random.choice(departments)
        sub = random.choice(subjects)
        act = random.choice(actions)
        reas = random.choice(reasons)
        hour = random.randint(0, 23)
        acuity = random.randint(1, 5)
        log_id = f"LOG_REV_{i:05d}"
        
        # Build a highly variable, realistic clinical operational log
        log_line = f"{log_id} | FACILITY OPERATIONS MATRIX: {sub} within the [{dept}] unit {act} {reas} (Telemetry Window: {hour:02d}:00 | Severity Threshold: Level {acuity}).\n"
        f.write(log_line)

print("Successfully generated data/document_map.txt with 10,000 unique logs.")