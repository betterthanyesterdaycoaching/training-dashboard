import xml.etree.ElementTree as ET
import json
from ingestion.normalise import normalise_biometrics, normalise_workout

def parse_apple_health_xml(filepath: str) -> dict:
    tree = ET.parse(filepath)
    root = tree.getroot()
    biometrics, workouts = {}, []
    type_map = {
        "HKQuantityTypeIdentifierBodyMass": "weight_kg",
        "HKQuantityTypeIdentifierBodyFatPercentage": "body_fat_pct",
        "HKQuantityTypeIdentifierHeartRateVariabilitySDNN": "hrv_ms",
        "HKQuantityTypeIdentifierRestingHeartRate": "resting_hr",
        "HKCategoryTypeIdentifierSleepAnalysis": "sleep_duration_hours",
    }
    for record in root.findall("Record"):
        rtype = record.get("type", "")
        if rtype not in type_map: continue
        d = record.get("startDate", "")[:10]
        biometrics.setdefault(d, {"date": d})
        try:
            val = float(record.get("value"))
            if rtype == "HKQuantityTypeIdentifierBodyFatPercentage": val = round(val * 100, 1)
            biometrics[d][type_map[rtype]] = val
        except: pass
    for wo in root.findall("Workout"):
        d = wo.get("startDate", "")[:10]
        workouts.append(normalise_workout("apple_health", {
            "date": d,
            "activity_type": wo.get("workoutActivityType", "").replace("HKWorkoutActivityType", ""),
            "actual_duration_min": round(float(wo.get("duration", 0)), 1),
        }))
    return {
        "biometrics": [normalise_biometrics("apple_health", r) for r in biometrics.values()],
        "workouts": workouts,
    }

def parse_health_auto_export_json(content) -> dict:
    data = json.load(content)
    biometrics, workouts = {}, []
    for item in data.get("data", []):
        d = item.get("date", "")[:10]
        biometrics.setdefault(d, {"date": d})
        biometrics[d].update({
            "weight_kg": item.get("weight_kg"),
            "hrv_ms": item.get("hrv"),
            "resting_hr": item.get("resting_heart_rate"),
            "sleep_duration_hours": item.get("sleep_hours"),
        })
    return {
        "biometrics": [normalise_biometrics("apple_health", r) for r in biometrics.values()],
        "workouts": workouts,
    }
