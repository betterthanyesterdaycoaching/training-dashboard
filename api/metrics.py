from http.server import BaseHTTPRequestHandler
import json, os, urllib.request

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        supabase_url = os.environ.get('SUPABASE_URL')
        supabase_key = os.environ.get('SUPABASE_ANON_KEY')
        rows = []
        if supabase_url and supabase_key:
            try:
                url = f"{supabase_url}/rest/v1/vw_daily_llm_context?select=*&order=date.desc&limit=30"
                req = urllib.request.Request(url, headers={"apikey": supabase_key, "Authorization": f"Bearer {supabase_key}"})
                with urllib.request.urlopen(req) as response:
                    rows = json.loads(response.read().decode('utf-8'))
            except Exception as e:
                rows = [{"error": str(e)}]
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(rows).encode('utf-8'))
