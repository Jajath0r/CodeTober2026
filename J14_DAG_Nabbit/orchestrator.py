from typing import Callable

def call_wanted_function(
    function: str,
    graph: dict[str, list[str]],
    function_order: list[str]
) -> None:
    if function not in function_order:
        for dependency in graph[function]:
            call_wanted_function(dependency, graph, function_order)
        function_order.append(function)


def get_all_dependancy(graph: dict[str, list[str]]) -> list[str]:
    function_order = []
    for function in graph:
        call_wanted_function(function, graph, function_order)
    return function_order


def extract_catalog():
    raise RuntimeError("Catalogue indisponible")

def extract_orders():
    print("Extraction des commandes")
    
def transform_sales():
    print("Transformation des ventes")
    
def load_sales():
    print("Chargement des ventes")


def execute_function_in_order(graph : dict[str,list[str]]) -> dict[str,str]:
    function_order = get_all_dependancy(graph)
    tasks = {
        "extract_catalog": extract_catalog,
        "extract_orders": extract_orders,
        "transform_sales": transform_sales,
        "load_sales": load_sales,
    }
    validate_graph(graph, tasks)
    function_order = get_all_dependancy(graph)
    task_status = {}
    for f in function_order:
        if not all(task_status.get(d) == "SUCCESS" for d in graph[f]):
            task_status[f] = "SKIPPED"
            continue
        try :
            tasks[f]()
        except Exception:
            task_status[f] = "FAILED"
        else:
            task_status[f] = "SUCCESS"
    return task_status
            
def validate_graph(
    graph: dict[str, list[str]],
    tasks: dict[str, Callable[[], None]]
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
    for d in graph[f]:
        if d not in graph:
            raise ValueError(
                f"Task '{f}' depends on unknown task '{d}'"
            )
        else:
            validate_current_function_graph(graph, visit_status,d)
    visit_status[f] = "VISITED"
    