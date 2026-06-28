from http.server import BaseHTTPRequestHandler
import json, os, urllib.request

DROPBOX_API = "https://api.dropboxapi.com/2"
DROPBOX_CONTENT = "https://content.dropboxapi.com/2"
DROPBOX_FOLDER = "/health-exports"  # must match your Health Auto Export folder
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_ANON_KEY")
DROPBOX_TOKEN = os.environ.get("DROPBOX_TOKEN")

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        result = {"biometrics_rows": 0, "errors": []}

        if not (DROPBOX_TOKEN and SUPABASE_URL and SUPABASE_KEY):
            result["errors"].append("Missing DROPBOX_TOKEN or Supabase env vars")
            self._respond(result)
            return

        try:
            # 1. List files in /health-exports
            headers = {
                "Authorization": f"Bearer {DROPBOX_TOKEN}",
                "Content-Type": "application/json",
            }
            data = json.dumps({"path": DROPBOX_FOLDER, "limit": 10}).encode("utf-8")
            req = urllib.request.Request(f"{DROPBOX_API}/files/list_folder",
                                         data=data, headers=headers)
            with urllib.request.urlopen(req) as r:
                entries = json.loads(r.read()).get("entries", [])

            # 2. Find the most recent JSON file
            json_files = [e for e in entries if e.get(".tag") == "file"
                          and e["name"].lower().endswith(".json")]
            if not json_files:
                result["errors"].append("No JSON exports found in Dropbox")
                self._respond(result)
                return

            latest = sorted(json_files, key=lambda e: e["name"], reverse=True)[0]
            path_lower = latest["path_lower"]

            # 3. Download the JSON file
            headers = {
                "Authorization": f"Bearer {DROPBOX_TOKEN}",
                "Dropbox-API-Arg": json.dumps({"path": path_lower}),
            }
            req = urllib.request.Request(f"{DROPBOX_CONTENT}/files/download",
                                         headers=headers)
            with urllib.request.urlopen(req) as r:
                content = r.read().decode("utf-8")
            data = json.loads(content)

            # 4. Map JSON to daily_biometrics rows
            biometrics_rows = []
            for item in data.get("data", []):
                d = item.get("date", "")[:10]
                if not d:
                    continue
                row = {
                    "date": d,
                    "weight_kg": item.get("weight_kg"),
                    "hrv_ms": item.get("hrv"),
                    "resting_hr": item.get("resting_heart_rate"),
                    "sleep_duration_hours": item.get("sleep_hours"),
                }
                biometrics_rows.append(row)

            if not biometrics_rows:
                result["errors"].append("No biometrics rows parsed from JSON")
                self._respond(result)
                return

            # 5. Upsert into Supabase daily_biometrics
            url = f"{SUPABASE_URL}/rest/v1/daily_biometrics"
            payload = json.dumps(biometrics_rows).encode("utf-8")
            headers = {
                "apikey": SUPABASE_KEY,
                "Authorization": f"Bearer {SUPABASE_KEY}",
                "Content-Type": "application/json",
                "Prefer": "resolution=merge-duplicates",
            }
            req = urllib.request.Request(url, data=payload,
                                         headers=headers, method="POST")
            with urllib.request.urlopen(req) as r:
                _ = r.read()

            result["biometrics_rows"] = len(biometrics_rows)

        except Exception as e:
            result["errors"].append(str(e))

        self._respond(result)

    def _respond(self, result):
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(result).encode("utf-8"))
