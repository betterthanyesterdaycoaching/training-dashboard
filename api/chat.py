from http.server import BaseHTTPRequestHandler
import json, os, urllib.request, time

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers.get('Content-Length', 0))
        body = json.loads(self.rfile.read(content_length).decode('utf-8')) if content_length else {}
        user_query = body.get('query', '')
        supabase_url = os.environ.get('SUPABASE_URL')
        supabase_key = os.environ.get('SUPABASE_ANON_KEY')
        gemini_api_key = os.environ.get('GEMINI_API_KEY')

        context_data = '[]'
        if supabase_url and supabase_key:
            try:
                url = f"{supabase_url}/rest/v1/vw_daily_llm_context?select=*&order=date.desc&limit=14"
                req = urllib.request.Request(url, headers={
                    "apikey": supabase_key,
                    "Authorization": f"Bearer {supabase_key}"
                })
                with urllib.request.urlopen(req) as response:
                    context_data = response.read().decode('utf-8')
            except Exception as e:
                context_data = json.dumps({"supabase_error": str(e)})

        answer = 'Gemini API key missing.'
        if gemini_api_key:
            prompt = (
                "You are an elite endurance coach and sports nutritionist. "
                "Use the athlete data below to answer clearly and practically with concise actions. "
                f"Athlete data: {context_data}. User question: {user_query}"
            )
            gemini_url = (
                f"https://generativelanguage.googleapis.com/v1beta/models/"
                f"gemini-2.0-flash-lite:generateContent?key={gemini_api_key}"
            )
            payload = json.dumps({
                'contents': [{'parts': [{'text': prompt}]}],
                'generationConfig': {'temperature': 0.2}
            }).encode('utf-8')

            for attempt in range(3):
                try:
                    req = urllib.request.Request(
                        gemini_url, data=payload,
                        headers={'Content-Type': 'application/json'}, method='POST'
                    )
                    with urllib.request.urlopen(req) as response:
                        data = json.loads(response.read().decode('utf-8'))
                        answer = data['candidates'][0]['content']['parts'][0]['text']
                        break
                except Exception as e:
                    if '429' in str(e) and attempt < 2:
                        time.sleep(5)
                    else:
                        answer = f'Gemini error: {str(e)}'
                        break

        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps({'answer': answer}).encode('utf-8'))
