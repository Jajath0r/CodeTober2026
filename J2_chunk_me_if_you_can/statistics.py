from operator import itemgetter

def increment_status_counter(row : dict[str,str], nb_2xx : int, nb_4xx : int, nb_5xx : int) -> tuple[int,int,int]:
    n = row['status_code'][0]
    if n == '2':
        nb_2xx += 1
    elif n == '4':
        nb_4xx +=1
    elif n == '5':
        nb_5xx +=1
    return (nb_2xx,nb_4xx,nb_5xx)

def add_service_statistics(row : dict[str,str], services : dict[str,dict[str,int]]) -> dict[str,dict[str,int]]:
    current_service = row['service']
    nb_5 = 1 if row['status_code'][0] == '5' else 0
    if current_service not in services:
        services[current_service] = {"nb_request" : 1, "resp_time" : int(row["response_time_ms"]), "nb_5xx" : nb_5}
    else:
        services[current_service]['nb_request'] += 1
        services[current_service]['resp_time'] += int(row['response_time_ms'])
        services[current_service]['nb_5xx'] +=nb_5
    return services

def add_to_slowest(row : dict[str, str], top_10_slowest : list[dict[str,str]]) -> list[dict[str,str]]:
    if len(top_10_slowest) == 10:
        if int(row['response_time_ms']) > top_10_slowest[-1]['response_time_ms']:
            top_10_slowest.remove(top_10_slowest[-1])
        else: return top_10_slowest
    top_10_slowest.append({"request_id": row["request_id"], "service": row["service"], "endpoint": row["endpoint"], "response_time_ms": int(row["response_time_ms"])})
    return sorted(top_10_slowest, key = lambda r: r['response_time_ms'], reverse=True)

def get_mean_resp_time(resp_time : int, nb_requests : int) -> float:
    return resp_time/nb_requests