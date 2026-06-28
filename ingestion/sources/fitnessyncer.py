import csv, io
from ingestion.normalise import normalise_workout

def parse_fitnessyncer_csv(content: str) -> list[dict]:
    reader = csv.DictReader(io.StringIO(content))
    return [normalise_workout("fitnessyncer", row) for row in reader]
