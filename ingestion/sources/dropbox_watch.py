import urllib.request, json, os

DROPBOX_API = "https://api.dropboxapi.com/2"
DROPBOX_CONTENT = "https://content.dropboxapi.com/2"

def list_new_files(folder: str = "/health-exports") -> list[dict]:
    token = os.environ.get("DROPBOX_TOKEN")
    if not token: return []
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    data = json.dumps({"path": folder, "limit": 50}).encode()
    req = urllib.request.Request(f"{DROPBOX_API}/files/list_folder", data=data, headers=headers)
    with urllib.request.urlopen(req) as r:
        return [f for f in json.loads(r.read()).get("entries", []) if f[".tag"] == "file"]

def download_file(path: str) -> bytes:
    token = os.environ["DROPBOX_TOKEN"]
    req = urllib.request.Request(f"{DROPBOX_CONTENT}/files/download", headers={
        "Authorization": f"Bearer {token}",
        "Dropbox-API-Arg": json.dumps({"path": path})
    })
    with urllib.request.urlopen(req) as r:
        return r.read()
