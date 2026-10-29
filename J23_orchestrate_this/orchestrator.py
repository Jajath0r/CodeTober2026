from typing import Callable
import duckdb
import json
from jobs import execute, TransientJobError, PermanentJobError
from state import load_run_state
from pathlib import Path
from datetime import datetime
from os import replace,path, makedirs
#from extract import extract_orders,extract_products
#from validation import validate_orders, validate_products

def call_wanted_function(
    function: str,
    graph: dict[str, list[str]],
    function_order: list[str]
) -> None:
    if function not in function_order:
        for dependency in graph[function]["depends_on"]:
            call_wanted_function(dependency, graph, function_order)
        function_order.append(function)


def get_all_dependancy(graph: dict[str, list[str]]) -> list[str]:
    function_order = []
    for function in graph:
        call_wanted_function(function, graph, function_order)
    return function_order

def execute_function_in_order(
    graph: dict,
    project_root: Path,
    work_dir: Path,
    run_id: str
) -> dict:
    tasks = {
        "import_orders",
        "import_products",
        "check_orders",
        "check_products",
        "aggregate",
        "publish"
    }
    validate_graph(graph, tasks)
    state_path = work_dir / "runs" / f"{run_id}.json"
    state_path.parent.mkdir(parents=True, exist_ok=True)
    
    function_order = get_all_dependancy(graph)
    run_state = load_run_state(state_path, run_id, graph)
    task_status = run_state["tasks"]
    for f in function_order:
        if task_status[f]["status"] == "SUCCESS":
            continue
        if not all(task_status[d]["status"] == "SUCCESS"for d in graph[f]["depends_on"]):
            task_status[f]["status"] = "SKIPPED"
            save_run_state(run_state, state_path)
            continue
        max_attempts = graph[f]["max_attempts"]
        attempts_used = task_status[f]["attempts"]
        if attempts_used>=max_attempts:
            print(f"Impossible d'effectuer la tâche {f}, nombre maximal de tentative atteint")
            task_status[f]["status"] = "FAILED"
            save_run_state(run_state, state_path)
            continue
        for attempt in range(attempts_used + 1, max_attempts + 1):
            task_status[f]["status"] = "RUNNING"
            task_status[f]["attempts"] = attempt
            save_run_state(run_state, state_path)
            attempt_status = "RUNNING"
            try :
                metrics = execute(
                    task_id=f,
                    project_root=project_root,
                    work_dir=work_dir,
                    run_id=run_id
                )
            except TransientJobError:
                attempt_status = "FAILED"
                if attempt < max_attempts:
                    print(f"Tentative n°{attempt} sur {f} échouée")
                else:
                    print(f"Impossible d'effectuer la tâche {f}, nombre maximal de tentative atteint")
                    task_status[f]["status"] = "FAILED"
            except PermanentJobError:
                attempt_status = "FAILED"
                task_status[f]["status"] = "FAILED"
                print("Erreur permanente")
                break
            else:
                attempt_status = "SUCCESS"
                task_status[f]["status"] = "SUCCESS"
                task_status[f]["metrics"] = metrics
                break
            finally:
                task_status[f]["history"].append({
                "attempt": attempt,
                "status": attempt_status,
                "timestamp": datetime.now().isoformat()
                })
                save_run_state(run_state, state_path)
    if all(run_state["tasks"][task]["status"] == "SUCCESS" for task in run_state["tasks"]) :
        run_state["status"] = "SUCCESS"
    elif "FAILED" in {run_state["tasks"][task]["status"] for task in run_state["tasks"]}:
        run_state["status"] = "FAILED"
    elif "RUNNING" in {run_state["tasks"][task]["status"] for task in run_state["tasks"]}:
        run_state["status"] = "RUNNING"
    save_run_state(run_state,state_path)
    return task_status


def validate_graph(
    graph: dict[str, list[str]],
    tasks: set[str]
) -> None:
    for f in graph:
        if f not in tasks:
            raise ValueError(
                f"Task '{f}' has no associated function"
            )
    visit_status = {f: "UNVISITED" for f in graph}
    for f in graph:
        validate_current_function_graph(graph, visit_status, f)
            

def validate_current_function_graph(graph : dict[str,list[str]], visit_status : dict[str,str], f : str) -> None:
    if f not in visit_status:
        raise ValueError(
            f"Task '{f}' does not exist"
        )
    elif visit_status[f] == "VISITING":
        raise ValueError(
            f"Task '{f}' is already being visited"
        )
    elif visit_status[f] == "VISITED":
        return
    else:
        visit_status[f] = "VISITING"
    for d in graph[f]["depends_on"]:
        if d not in graph:
            raise ValueError(
                f"Task '{f}' depends on unknown task '{d}'"
            )
        else:
            validate_current_function_graph(graph, visit_status,d)
    visit_status[f] = "VISITED"
    
    
def save_run_state(state: dict, state_path: Path) -> None:
    temp_path = state_path.with_suffix(".tmp")

    with temp_path.open("w", encoding="utf-8") as file:
        json.dump(state, file, indent=2)

    replace(temp_path, state_path)