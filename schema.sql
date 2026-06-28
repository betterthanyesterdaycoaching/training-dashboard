CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS athlete_goals (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    current_phase VARCHAR(50),
    target_race_name VARCHAR(100),
    target_race_date DATE,
    target_weight_kg DECIMAL(5,2),
    target_ftp_watts INTEGER,
    target_w_kg DECIMAL(4,2),
    weekly_tss_target INTEGER
);

CREATE TABLE IF NOT EXISTS daily_biometrics (
    date DATE PRIMARY KEY,
    weight_kg DECIMAL(5,2),
    body_fat_pct DECIMAL(4,2),
    sleep_score INTEGER,
    readiness_score INTEGER,
    hrv_ms DECIMAL(6,2),
    resting_hr INTEGER,
    sleep_duration_hours DECIMAL(4,2)
);

CREATE TABLE IF NOT EXISTS daily_nutrition (
    date DATE PRIMARY KEY,
    calories_in INTEGER,
    protein_g INTEGER,
    carbs_g INTEGER,
    fat_g INTEGER,
    fiber_g INTEGER,
    sodium_mg INTEGER,
    water_ml INTEGER
);

CREATE TABLE IF NOT EXISTS workouts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    date DATE REFERENCES daily_biometrics(date),
    activity_type VARCHAR(50),
    title VARCHAR(100),
    planned_duration_min INTEGER,
    actual_duration_min INTEGER,
    planned_tss INTEGER,
    actual_tss INTEGER,
    avg_heart_rate INTEGER,
    max_heart_rate INTEGER,
    avg_power_watts INTEGER,
    normalized_power_watts INTEGER,
    rpe INTEGER,
    coach_comments TEXT
);

CREATE TABLE IF NOT EXISTS ai_insights (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    date_generated TIMESTAMPTZ DEFAULT NOW(),
    insight_type VARCHAR(50),
    llm_prompt_used TEXT,
    ai_recommendation TEXT,
    implemented BOOLEAN DEFAULT FALSE
);

CREATE OR REPLACE VIEW vw_daily_llm_context AS
SELECT 
    b.date,
    (SELECT target_w_kg FROM athlete_goals ORDER BY created_at DESC LIMIT 1) AS target_w_kg,
    b.weight_kg,
    b.hrv_ms,
    b.sleep_score,
    b.readiness_score,
    b.resting_hr,
    b.sleep_duration_hours,
    n.calories_in,
    n.carbs_g,
    n.protein_g,
    n.water_ml,
    COALESCE(SUM(w.actual_tss), 0) AS total_daily_tss,
    COALESCE(SUM(w.actual_duration_min), 0) AS total_training_min,
    CASE 
        WHEN b.weight_kg > 0 AND MAX(w.normalized_power_watts) > 0 
        THEN ROUND((MAX(w.normalized_power_watts) / b.weight_kg)::numeric, 2)
        ELSE NULL 
    END AS peak_w_kg_today
FROM daily_biometrics b
LEFT JOIN daily_nutrition n ON b.date = n.date
LEFT JOIN workouts w ON b.date = w.date
GROUP BY b.date, b.weight_kg, b.hrv_ms, b.sleep_score, b.readiness_score, b.resting_hr, b.sleep_duration_hours, n.calories_in, n.carbs_g, n.protein_g, n.water_ml;
