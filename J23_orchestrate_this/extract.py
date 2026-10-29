import json
import duckdb
from typing import Any


def get_config_graph(graph_name : str) -> dict[str,Any]:
    with open(graph_name,'r') as graph:
        graph_data = json.load(graph)
    return {task["id"] : {"depends_on": task['depends_on'],"max_attempts" : task["max_attempts"]} for task in graph_data['tasks']}
