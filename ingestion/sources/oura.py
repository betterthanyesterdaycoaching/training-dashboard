import urllib.request, json, os
from ingestion.normalise import normalise_biometrics

def fetch_oura(days: int = 30) -> list[dict]:
    token = os.environ.get("OURA_TOKEN")
    if not token:
        raise ValueError("OURA_TOKEN not set")
    from datetime import date, timedelta
    start = (date.today() - timedelta(days=days)).isoformat()
    headers = {"Authorization": f"Bearer {token}"}
    results = {}

    # Sleep
    url = f"https://api.ouraring.com/v2/usercollection/daily_sleep?start_date={start}"
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req) as r:
        for item in json.loads(r.read())["data"]:
            d = item["day"]
            results.setdefault(d, {})["date"] = d
            results[d]["sleep_score"] = item.get("score")
            results[d]["sleep_duration_hours"] = round(
                item.get("contributors", {}).get("total_sleep", 0) / 3600, 2
            )

    # Readiness
    url = f"https://api.ouraring.com/v2/usercollection/daily_readiness?start_date={start}"
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req) as r:
        for item in json.loads(r.read())["data"]:
            d = item["day"]
            results.setdefault(d, {})["date"] = d
            results[d]["readiness_score"] = item.get("score")

    # HRV + resting HR
    url = f"https://api.ouraring.com/v2/usercollection/daily_cardiovascular_age?start_date={start}"
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req) as r:
        for item in json.loads(r.read()).get("data", []):
            d = item.get("day")
            if d:
                results.setdefault(d, {})["date"] = d
                results[d]["hrv_ms"] = item.get("hrv_balance_ms")

    return [normalise_biometrics("oura", row) for row in results.values()]
