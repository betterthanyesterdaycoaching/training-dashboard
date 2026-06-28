import urllib.request, json, os

DRIVE_API = "https://www.googleapis.com/drive/v3"

def list_new_files(folder_id: str = None) -> list[dict]:
    token = os.environ.get("GOOGLE_DRIVE_TOKEN")
    if not token: return []
    folder_id = folder_id or os.environ.get("GOOGLE_DRIVE_FOLDER_ID", "root")
    query = urllib.request.quote(f"'{folder_id}' in parents and trashed=false")
    url = f"{DRIVE_API}/files?q={query}&fields=files(id,name,mimeType,modifiedTime)"
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {token}"})
    with urllib.request.urlopen(req) as r:
        return json.loads(r.read()).get("files", [])

def download_file(file_id: str) -> bytes:
    token = os.environ["GOOGLE_DRIVE_TOKEN"]
    url = f"{DRIVE_API}/files/{file_id}?alt=media"
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {token}"})
    with urllib.request.urlopen(req) as r:
        return r.read()
