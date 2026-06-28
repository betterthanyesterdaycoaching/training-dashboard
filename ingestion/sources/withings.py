import urllib.request, urllib.parse, json, os
from ingestion.normalise import normalise_biometrics

WITHINGS_TOKEN_URL = "https://wbsapi.withings.net/v2/oauth2"
WITHINGS_MEASURE_URL = "https://wbsapi.withings.net/measure"

def refresh_access_token() -> str:
    client_id = os.environ.get("WITHINGS_CLIENT_ID")
    if not client_id: return None
    client_secret = os.environ["WITHINGS_CLIENT_SECRET"]
    refresh_token = os.environ["WITHINGS_REFRESH_TOKEN"]
    data = urllib.parse.urlencode({
        "action": "requesttoken",
        "grant_type": "refresh_token",
        "client_id": client_id,
        "client_secret": client_secret,
        "refresh_token": refresh_token,
    }).encode()
    req = urllib.request.Request(WITHINGS_TOKEN_URL, data=data, method="POST")
    try:
        with urllib.request.urlopen(req) as r:
            body = json.loads(r.read())
        return body["body"]["access_token"]
    except:
        return None

def fetch_withings(days: int = 30) -> list[dict]:
    from datetime import date, timedelta
    token = refresh_access_token()
    if not token: return []
    import time
    start_ts = int(time.time()) - days * 86400
    data = urllib.parse.urlencode({
        "action": "getmeas",
        "meastypes": "1,6,8",
        "category": 1,
        "startdate": start_ts,
    }).encode()
    req = urllib.request.Request(
        WITHINGS_MEASURE_URL, data=data,
        headers={"Authorization": f"Bearer {token}"}, method="POST"
    )
    with urllib.request.urlopen(req) as r:
        body = json.loads(r.read())

    results = {}
    for group in body.get("body", {}).get("measuregrps", []):
        from datetime import datetime
        d = datetime.utcfromtimestamp(group["date"]).strftime("%Y-%m-%d")
        results.setdefault(d, {"date": d})
        for m in group["measures"]:
            val = m["value"] * (10 ** m["unit"])
            if m["type"] == 1:
                results[d]["weight_kg"] = round(val, 2)
            elif m["type"] == 6:
                results[d]["body_fat_pct"] = round(val, 1)

    height_m = float(os.environ.get("ATHLETE_HEIGHT_M", "1.75"))
    for d, row in results.items():
        if "weight_kg" in row:
            row["bmi"] = round(row["weight_kg"] / (height_m ** 2), 1)

    return [normalise_biometrics("withings", row) for row in results.values()]
