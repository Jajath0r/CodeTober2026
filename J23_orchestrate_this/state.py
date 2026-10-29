import json
from pathlib import Path

def load_run_state(state_path: Path, run_id: str, graph: dict) -> dict:
    if state_path.exists():
        with state_path.open("r", encoding="utf-8") as file:
            return json.load(file)

    return {
        "run_id": run_id,
        "status": "PENDING",
        "tasks": {
            task_id: {
                "status": "PENDING",
                "attempts": 0,
                "metrics": {},
                "history": []
            }
            for task_id in graph
        }
    }