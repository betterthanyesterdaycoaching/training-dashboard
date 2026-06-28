def normalise_biometrics(source: str, raw: dict) -> dict:
    row = {"source": source}
    field_map = {
        "date": ["date", "Date", "day", "created_at"],
        "weight_kg": ["weight_kg", "Weight (kg)", "weight", "mass_kg", "Weight"],
        "body_fat_pct": ["body_fat_pct", "Fat (%)", "body_fat", "fatRatio", "Body Fat (%)"],
        "bmi": ["bmi", "BMI", "body_mass_index"],
        "sleep_duration_hours": ["sleep_duration_hours", "sleep_hours", "total_sleep_duration", "sleepDurationHours", "Sleep Duration (h)"],
        "sleep_score": ["sleep_score", "sleep_quality", "sleepScore", "Sleep Score"],
        "readiness_score": ["readiness_score", "readiness", "readinessScore", "Readiness Score"],
        "hrv_ms": ["hrv_ms", "hrv", "HRV (ms)", "avgHRV", "averageHrv"],
        "resting_hr": ["resting_hr", "resting_heart_rate", "restingHeartRate", "Resting HR"],
    }
    for std_key, aliases in field_map.items():
        for alias in aliases:
            if alias in raw and raw[alias] not in (None, "", "null"):
                row[std_key] = raw[alias]
                break
    return row

def normalise_workout(source: str, raw: dict) -> dict:
    row = {"source": source}
    field_map = {
        "date": ["date", "Date", "start_date", "startDate"],
        "activity_type": ["activity_type", "Activity Type", "type", "sport", "activityType"],
        "title": ["title", "Name", "name", "workout_name", "Activity Name"],
        "actual_duration_min": ["actual_duration_min", "Duration (min)", "duration_min", "moving_time_min", "elapsed_time_min"],
        "actual_tss": ["actual_tss", "TSS", "tss", "Training Stress Score"],
        "avg_heart_rate": ["avg_heart_rate", "Avg HR", "average_heart_rate", "avgHeartRate"],
        "avg_power_watts": ["avg_power_watts", "Avg Power", "average_power", "avgPower"],
        "normalized_power_watts": ["normalized_power_watts", "NP", "normalized_power", "normPower"],
        "rpe": ["rpe", "RPE", "perceived_exertion"],
    }
    for std_key, aliases in field_map.items():
        for alias in aliases:
            if alias in raw and raw[alias] not in (None, "", "null"):
                row[std_key] = raw[alias]
                break
    return row

def normalise_nutrition(source: str, raw: dict) -> dict:
    row = {"source": source}
    field_map = {
        "date": ["date", "Date", "day"],
        "calories_in": ["calories_in", "Calories", "calories", "energy_kcal", "Energy (kcal)"],
        "protein_g": ["protein_g", "Protein (g)", "protein", "proteinGrams"],
        "carbs_g": ["carbs_g", "Carbs (g)", "carbohydrates", "carbsGrams"],
        "fat_g": ["fat_g", "Fat (g)", "fat", "fatGrams"],
        "water_ml": ["water_ml", "Water (ml)", "water", "hydration_ml"],
    }
    for std_key, aliases in field_map.items():
        for alias in aliases:
            if alias in raw and raw[alias] not in (None, "", "null"):
                row[std_key] = raw[alias]
                break
    return row
