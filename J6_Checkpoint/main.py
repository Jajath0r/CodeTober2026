import argparse
import json
import csv
from contextlib import ExitStack
from datetime import datetime
from typing import TypedDict
from os import path, makedirs,replace,remove

CHECKPOINT_INTERVAL = 10000

class EventInfo(TypedDict):
    updated_at : datetime
    status : str
    payload : str

def parse_input():
    parser = argparse.ArgumentParser(
        description="Checkpoint"
    )
    
    parser.add_argument(
        "input_csv",
        type=str,
        help="csv input file"
    )
    
    parser.add_argument(
        "output_rep",
        type=str,
        help="output repository"
    )
    
    return parser.parse_args()


def build_json_data(nb_read_lines : int, nb_invalid_lines : int, nb_distinct_event_ids : int, nb_replaced_versions : int) -> dict[str,int]:
    return {
        "nb_read_lines" : nb_read_lines,
        "nb_invalid_lines" : nb_invalid_lines,
        "nb_distinct_event_ids" : nb_distinct_event_ids,
        "nb_replaced_versions" : nb_replaced_versions
    }

def write_json_output(json_data : dict[str,int], output_file : str) -> None:
    with open(output_file, "w", newline="") as json_output:
        json.dump(json_data,json_output)

def update_latest_updated_at(id : str, status : str, payload : str, event_dict : dict[str,EventInfo], timestamp : datetime, nb_replaced_versions : int) -> int:
    if id in event_dict:
        if event_dict[id]["updated_at"] >= timestamp:
            return nb_replaced_versions
        else:
            nb_replaced_versions += 1
    event_dict[id] = {"updated_at":timestamp, "status":status, "payload":payload} 
    return nb_replaced_versions

def process_line(ligne : dict[str,str], event_dict : dict[str,EventInfo], nb_replaced_versions : int, nb_invalid_lines : int) ->  tuple[int,int]:
    try:
        current_id = ligne["event_id"]
        current_timestamp = datetime.strptime(ligne['updated_at'], "%Y-%m-%d %H:%M:%S")
        if current_id == "":
            nb_invalid_lines += 1
        else:
            nb_replaced_versions = update_latest_updated_at(current_id,ligne['status'],ligne['payload'],event_dict,current_timestamp, nb_replaced_versions)
    except ValueError:
        nb_invalid_lines += 1
    return nb_replaced_versions, nb_invalid_lines

def write_csv_output(output_file : str, stack: ExitStack,event_dict : dict[str,EventInfo]) -> None:
    output_csv = stack.enter_context(
        open(output_file,"w",newline="")
    )
    w = csv.DictWriter(output_csv,fieldnames=["event_id","updated_at","status","payload"])
    w.writeheader()
    for event in event_dict:
        current_event = event_dict[event]
        row = {"event_id":event, "updated_at":current_event["updated_at"], "status" : current_event["status"], "payload" : current_event["payload"]}
        w.writerow(row)

def main():
    
    args = parse_input()
    
    input_file = args.input_csv
    if not path.exists(args.output_rep):
        makedirs(args.output_rep)   
    output_file = path.join(args.output_rep,"output.csv")
    report_file = path.join(args.output_rep,"report.json")
    input_file_without_ext = path.splitext(input_file.replace("/","_").replace("\\","_").replace(":",""))[0]
    checkpoint_file = "checkpoint_"+input_file_without_ext+".json"
    tmp_checkpoint_file = "checkpoint_tmp_"+input_file_without_ext+".json"
    nb_distinct_event_ids = 0
    event_dict :dict[str, EventInfo] = {}
        
    with ExitStack() as stack:
        if path.exists(checkpoint_file):
            with open(checkpoint_file) as f:
                checkpoint_data = json.load(f)
            cp_event_dict = checkpoint_data["event_dict"]
            for event in cp_event_dict:
                current_event=cp_event_dict[event]
                event_dict[event]={}
                event_dict[event]["updated_at"] = datetime.strptime(current_event["updated_at"],"%Y-%m-%d %H:%M:%S")
                event_dict[event]["status"] = current_event["status"]
                event_dict[event]["payload"] = current_event["payload"]
            nb_read_lines = checkpoint_data["nb_read_lines"]
            nb_replaced_versions = checkpoint_data["nb_replaced_versions"]
            nb_invalid_lines = checkpoint_data["nb_invalid_lines"]
        else:
            nb_read_lines = 0
            nb_invalid_lines = 0
            nb_replaced_versions = 0
            
            
        file = stack.enter_context(
            open(input_file,"r",newline="")
        )
        r = csv.DictReader(file)
        it = 0
        checkpoint_read_lines = nb_read_lines
        for row in r:
            if it < checkpoint_read_lines:
                it += 1
                continue
            nb_read_lines +=1
            nb_replaced_versions,nb_invalid_lines = process_line(row,event_dict,nb_replaced_versions,nb_invalid_lines)
            if nb_read_lines % CHECKPOINT_INTERVAL == 0:
                cp_event_dict = {}
                for event in event_dict:
                    current_event = event_dict[event]
                    cp_event_dict[event] = {}
                    cp_event_dict[event]["updated_at"]=str(current_event["updated_at"])
                    cp_event_dict[event]["status"]=str(current_event["status"])
                    cp_event_dict[event]["payload"]=str(current_event["payload"])
                new_checkpoint_data = {"event_dict":cp_event_dict,"nb_read_lines":nb_read_lines,"nb_replaced_versions":nb_replaced_versions, "nb_invalid_lines":nb_invalid_lines}
                write_json_output(new_checkpoint_data,tmp_checkpoint_file)
                replace(tmp_checkpoint_file,checkpoint_file)
        write_csv_output(output_file,stack,event_dict)
    nb_distinct_event_ids = len(event_dict)
    data = build_json_data(nb_read_lines, nb_invalid_lines, nb_distinct_event_ids, nb_replaced_versions)
    write_json_output(data, report_file)
    remove(checkpoint_file)


if __name__ == "__main__":
    main()