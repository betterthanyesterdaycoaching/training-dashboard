CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ─── ATHLETE GOALS ───────────────────────────────────────────
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

-- ─── DAILY BIOMETRICS ────────────────────────────────────────
CREATE TABLE IF NOT EXISTS daily_biometrics (
  date DATE PRIMARY KEY,
  weight_kg DECIMAL(5,2),
  body_fat_pct DECIMAL(4,2),
  bmi DECIMAL(4,2),
  sleep_score INTEGER,
  readiness_score INTEGER,
  hrv_ms DECIMAL(6,2),
  resting_hr INTEGER,
  sleep_duration_hours DECIMAL(4,2)
);

-- ─── DAILY NUTRITION ─────────────────────────────────────────
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

-- ─── WORKOUTS ────────────────────────────────────────────────
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
  coach_comments TEXT,
  source VARCHAR(50)
);

-- ─── RACES ───────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS races (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  race_date DATE NOT NULL,
  race_name VARCHAR(150) NOT NULL,
  location VARCHAR(150),
  discipline VARCHAR(50) CHECK (discipline IN (
    'Mountain Bike Marathon','Mountain Bike XCO','Gravel','Road','Other'
  )),
  priority CHAR(1) CHECK (priority IN ('A','B','C')),
  distance_km DECIMAL(6,2),
  elevation_m INTEGER,
  goal_time VARCHAR(20),
  actual_time VARCHAR(20),
  result_position INTEGER,
  notes TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ─── AI INSIGHTS ─────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS ai_insights (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  date_generated TIMESTAMPTZ DEFAULT NOW(),
  insight_type VARCHAR(50),
  llm_prompt_used TEXT,
  ai_recommendation TEXT,
  implemented BOOLEAN DEFAULT FALSE
);

-- ─── INGESTION LOG ───────────────────────────────────────────
CREATE TABLE IF NOT EXISTS ingestion_log (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  ingested_at TIMESTAMPTZ DEFAULT NOW(),
  source VARCHAR(50),
  filename VARCHAR(200),
  rows_upserted INTEGER,
  status VARCHAR(20),
  error_message TEXT
);

-- ─── VIEW ────────────────────────────────────────────────────
CREATE OR REPLACE VIEW vw_daily_llm_context AS
SELECT
  b.date,
  (SELECT target_w_kg FROM athlete_goals ORDER BY created_at DESC LIMIT 1) AS target_w_kg,
  b.weight_kg,
  b.body_fat_pct,
  b.bmi,
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
GROUP BY b.date, b.weight_kg, b.body_fat_pct, b.bmi, b.hrv_ms,
  b.sleep_score, b.readiness_score, b.resting_hr, b.sleep_duration_hours,
  n.calories_in, n.carbs_g, n.protein_g, n.water_ml;

-- ─── SAMPLE RACE DATA ────────────────────────────────────────
INSERT INTO races (race_date, race_name, location, discipline, priority, distance_km, elevation_m) VALUES
('2026-08-02', 'Local XCO Round 3',        'Brisbane, QLD',   'Mountain Bike XCO',      'C', 30,   800),
('2026-09-14', 'Sunshine Coast Gravel',    'Noosa, QLD',      'Gravel',                 'B', 85,  1200),
('2026-10-19', 'Reef to Ridge MTB',        'Cairns, QLD',     'Mountain Bike Marathon', 'A', 100, 2800),
('2026-11-09', 'Brisbane Road Classic',    'Brisbane, QLD',   'Road',                   'C', 120,  900),
('2027-01-18', 'Dirty Dozen Gravel',       'Toowoomba, QLD',  'Gravel',                 'B', 130, 2200),
('2027-02-22', 'QLD MTB Marathon Champs',  'Gold Coast, QLD', 'Mountain Bike Marathon', 'A', 85,  2100),
('2027-04-06', 'Easter XCO Cup',           'Sydney, NSW',     'Mountain Bike XCO',      'B', 25,   600),
('2027-06-14', 'Winter Gravel Classic',    'Armidale, NSW',   'Gravel',                 'C', 95,  1800)
ON CONFLICT DO NOTHING;
