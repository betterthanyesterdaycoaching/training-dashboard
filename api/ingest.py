from http.server import BaseHTTPRequestHandler
import json, os, csv, io, urllib.request
from datetime import date
from ingestion.sources.oura import fetch_oura
from ingestion.sources.withings import fetch_withings
from ingestion.sources.dropbox_watch import list_new_files as dropbox_files, download_file as dropbox_dl
from ingestion.sources.google_drive_watch import list_new_files as drive_files, download_file as drive_dl
from ingestion.sources.apple_health import parse_health_auto_export_json
from ingestion.sources.fitnessyncer import parse_fitnessyncer_csv

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_ANON_KEY")

def upsert(table: str, rows: list[dict]):
    if not rows or not SUPABASE_URL: return 0
    url = f"{SUPABASE_URL}/rest/v1/{table}"
    payload = json.dumps(rows).encode()
    req = urllib.request.Request(url, data=payload, headers={
        "apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json", "Prefer": "resolution=merge-duplicates"
    }, method="POST")
    with urllib.request.urlopen(req) as r: return len(rows)

def write_csv(rows: list[dict], label: str):
    if not rows: return
    today = date.today().isoformat()
    os.makedirs("/tmp/data", exist_ok=True)
    path = f"/tmp/data/{today}-{label}.csv"
    with open(path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        results = {"biometrics": 0, "workouts": 0, "errors": []}
        try:
            bio = fetch_oura()
            results["biometrics"] += upsert("daily_biometrics", bio)
            write_csv(bio, "oura-biometrics")
        except Exception as e: results["errors"].append(f"oura: {e}")

        try:
            bio = fetch_withings()
            results["biometrics"] += upsert("daily_biometrics", bio)
            write_csv(bio, "withings-biometrics")
        except Exception as e: results["errors"].append(f"withings: {e}")

        for provider, files_fn, dl_fn in [("dropbox", dropbox_files, dropbox_dl), ("drive", drive_files, drive_dl)]:
            try:
                for f in files_fn():
                    content = dl_fn(f.get("path_lower") or f.get("id"))
                    name = f.get("name", "").lower()
                    if name.endswith(".json"):
                        parsed = parse_health_auto_export_json(io.StringIO(content.decode()))
                        results["biometrics"] += upsert("daily_biometrics", parsed["biometrics"])
                        results["workouts"] += upsert("workouts", parsed["workouts"])
                    elif name.endswith(".csv"):
                        workouts = parse_fitnessyncer_csv(content.decode())
                        results["workouts"] += upsert("workouts", workouts)
            except Exception as e: results["errors"].append(f"{provider}: {e}")

        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(results).encode())
