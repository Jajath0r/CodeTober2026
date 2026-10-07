import argparse
from datetime import datetime
from contextlib import ExitStack
from os import path, makedirs, replace, remove
import csv
import json

CHECKPOINT_INTERVAL = 1000


def input_parse():
    parser = argparse.ArgumentParser(
        description="Watermark"
    )
    
    parser.add_argument(
        "input_path",
        type=str,
        help="input path like 'datasets/mini_run'"
    )
    
    parser.add_argument(
        "batch",
        type=str,
        help="current batch like '01'"
    )
    
    parser.add_argument(
        "output_rep",
        type=str,
        help="output repository name"
    )
    
    return parser.parse_args()

def return_timestamp_if_valid(timestamp : str) -> datetime:
    try:
        current_timestamp = datetime.strptime(timestamp,"%Y-%m-%d %H:%M:%S")
        return current_timestamp
    except ValueError:
        return None

def get_watermarks(output_json : str) -> tuple[datetime,datetime]:
    if path.exists(output_json):
        with open(output_json,"r") as report:
            data = json.load(report)
        watermark_before = return_timestamp_if_valid(data["watermark_after"])
        watermark_after = watermark_before
    else:
        watermark_before = None
        watermark_after = datetime.min
    return watermark_before,watermark_after


def write_checkpoint(checkpoint_file : str, event_dict : dict[str:str],nb_read_lines : int, nb_processed_lines : int, nb_invalid_lines : int, nb_skipped_lines : int, watermark_before : str, watermark_after : str) -> None:
    data = {
        "event_dict" : event_dict,
        "nb_read_lines" : nb_read_lines,
        "nb_processed_lines" : nb_processed_lines,
        "nb_skipped_lines" : nb_skipped_lines,
        "nb_invalid_lines" : nb_invalid_lines,
        "watermark_before" : watermark_before,
        "watermark_after" : watermark_after 
    }
    cp_tmp = "tmp_"+checkpoint_file
    with open(cp_tmp,"w") as cp:
        json.dump(data,cp)
    replace(cp_tmp,checkpoint_file)

def get_checkpoint_values(checkpoint_file : str, event_dict: dict[str,str], output_json : str) -> tuple[int,int,int,int,datetime,datetime]:
    if path.exists(checkpoint_file):
        with open(checkpoint_file) as f:
            checkpoint_data = json.load(f)
        cp_event_dict = checkpoint_data["event_dict"]
        for event in cp_event_dict:
            event_dict[event] = {}
            for key in cp_event_dict[event]:
                current_event=cp_event_dict[event]
                event_dict[event][key] = current_event[key]
        nb_read_lines = checkpoint_data["nb_read_lines"]
        nb_invalid_lines = checkpoint_data["nb_invalid_lines"]
        nb_skipped_lines = checkpoint_data["nb_skipped_lines"]
        nb_processed_lines = checkpoint_data["nb_processed_lines"]
        watermark_before = return_timestamp_if_valid(checkpoint_data["watermark_before"])
        watermark_after = return_timestamp_if_valid(checkpoint_data["watermark_after"])
    else:
        nb_read_lines = 0
        nb_invalid_lines = 0
        nb_processed_lines = 0
        nb_skipped_lines = 0
        watermark_before, watermark_after = get_watermarks(output_json)
    return nb_read_lines, nb_invalid_lines, nb_skipped_lines, nb_processed_lines, watermark_before, watermark_after

def watermark_to_json(watermark : datetime) -> str | None:
    if watermark is None:
        return None
    else:
        return str(watermark)

def main():
    args = input_parse()
    input_file = args.input_path+"_"+args.batch+".csv"
    output_rep = args.output_rep
    if not path.exists(output_rep):
        makedirs(output_rep)
    normalized_input_file = path.splitext(args.input_path.replace("/","_").replace("\\","_").replace(":",""))[0]
    csv_name = normalized_input_file+"_"+args.batch+"_output.csv"
    json_name = normalized_input_file+"_report.json"
    output_csv = path.join(output_rep,csv_name)
    output_json = path.join(output_rep,json_name)
    
    checkpoint_file = "checkpoint_"+normalized_input_file+args.batch+".json"
    
    event_dict = {}
    with ExitStack() as stack:
        nb_read_lines, nb_invalid_lines, nb_skipped_lines, nb_processed_lines, watermark_before, watermark_after = get_checkpoint_values(checkpoint_file, event_dict, output_json)
        nb_read_lines_cp = nb_read_lines
        file = stack.enter_context(
            open(input_file,"r")
        )
        r = csv.DictReader(file)
        i = 0
        for row in r:
            if i < nb_read_lines_cp:
                i += 1
                continue
            timestamp = return_timestamp_if_valid(row["event_timestamp"])
            if timestamp is None:
                nb_invalid_lines += 1
            else:
                if watermark_before is None or timestamp > watermark_before:
                    nb_processed_lines += 1
                    event_id = row['event_id']
                    event_dict[event_id] = {"event_timestamp":str(timestamp), "customer_id":row["customer_id"], "event_type":row["event_type"], "amount": row["amount"], "source":row["source"]}
                    if timestamp > watermark_after:
                        watermark_after = timestamp
                else:
                    nb_skipped_lines +=1
            nb_read_lines += 1
            if nb_read_lines % CHECKPOINT_INTERVAL == 0:
                write_checkpoint(checkpoint_file, event_dict,nb_read_lines,nb_processed_lines,nb_invalid_lines,nb_skipped_lines,watermark_to_json(watermark_before),watermark_to_json(watermark_after))
        write_checkpoint(checkpoint_file, event_dict,nb_read_lines,nb_processed_lines,nb_invalid_lines,nb_skipped_lines,watermark_to_json(watermark_before),watermark_to_json(watermark_after))
        new_output_csv = path.join(output_rep,"new_" + csv_name)
        with open(new_output_csv,"w",newline="") as output:
            w = csv.DictWriter(output,fieldnames=r.fieldnames)
            w.writeheader()
            for event in event_dict:
                current_event = event_dict[event]
                row = {"event_id":event}
                for key in current_event:
                    row[key] = current_event[key]
                w.writerow(row)
        replace(new_output_csv,output_csv)
        if watermark_after == datetime.min:
            watermark_after = None
        report_data = {"nb_read_lines":nb_read_lines,"nb_skipped_lines":nb_skipped_lines,"nb_processed_lines":nb_processed_lines,"nb_invalid_lines":nb_invalid_lines,"watermark_before":watermark_to_json(watermark_before),"watermark_after":watermark_to_json(watermark_after)}
        new_output_json = path.join(output_rep,"new_" + json_name)
        with open(new_output_json,"w") as report:
            json.dump(report_data,report)
        replace(new_output_json,output_json)
        if path.exists(checkpoint_file):remove(checkpoint_file)
        
if __name__ == "__main__":
    main()