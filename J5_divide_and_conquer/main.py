import argparse
from os import path, makedirs
import csv
import json
from contextlib import ExitStack
from typing import TypedDict, TextIO



class PartitionInfo(TypedDict):
    writer: csv.DictWriter
    fichier: TextIO
    filepath: str
    ids: set[str]

class ReportInfo(TypedDict):
    nb_read_lines: int
    nb_ignored_doubles:int
    nb_written_lines:int
    nb_partitions_created:int
    nb_line_per_partition:dict[str,int]
    
CACHE_THRESHOLD = 100

def parse_input():
    parser = argparse.ArgumentParser(
        description="csv divider"
    )
    
    parser.add_argument(
        "raw_input",
        type=str,
        help="input filename"
    )

    parser.add_argument(
        "output",
        type=str,
        help="output repository"
    )
    return parser.parse_args()

def evict_oldest_partition(cache_liste: list[str], partitions_dict: dict[str, PartitionInfo]) -> None:
    partition_to_close = cache_liste.pop(0)
    partitions_dict[partition_to_close]["fichier"].close()
    
def mark_as_recently_used(cache_liste : list[str], partition : str) -> None:
    cache_liste.remove(partition)
    cache_liste.append(partition)

def create_partition(row : dict[str,str], partition : str, date:str, partitions_dict : dict[str,PartitionInfo], cache_liste : list[str], output_repository : str, fieldnames : list[str]) -> csv.DictWriter:
    if(len(cache_liste) >= CACHE_THRESHOLD):
        evict_oldest_partition(cache_liste,partitions_dict)
    cache_liste.append(partition)
    output_partition_rep = path.join(output_repository,row['region'])
    if not path.exists(output_partition_rep):
        makedirs(output_partition_rep)
    filepath = path.join(output_partition_rep,date+".csv")
    f = open(filepath,"w",newline="")
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    partitions_dict[partition] = {"writer":writer, "fichier" : f, "filepath": filepath,"ids":set()}
    return writer

def reopen_partition(cache_liste : list[str],partitions_dict : dict[str,PartitionInfo], partition : str, fieldnames : list[str]) -> csv.DictWriter:
    evict_oldest_partition(cache_liste,partitions_dict)
    cache_liste.append(partition)
    f = open(partitions_dict[partition]["filepath"],"a",newline="")
    writer = csv.DictWriter(f,fieldnames=fieldnames)
    partitions_dict[partition]["fichier"] = f
    partitions_dict[partition]["writer"] = writer
    return writer
    
def build_json_data(nb_read_lines : int, nb_ignored_doubles : int, nb_written_lines : int, nb_partitions_created : int, nb_line_per_partition : dict[str,int]) -> ReportInfo:
    return {
            "nb_read_lines" : nb_read_lines,
            "nb_ignored_doubles" : nb_ignored_doubles,
            "nb_written_lines" : nb_written_lines,
            "nb_partitions_created" : nb_partitions_created,
            "nb_line_per_partition" : nb_line_per_partition
        }

def write_report_json(output_repository : str,report_data : ReportInfo) -> None:
    if not path.exists(output_repository):
        makedirs(output_repository)
    partition_report = path.join(output_repository,"partition_report.json")
    
    with open(partition_report,"w",newline="") as report:
        json.dump(report_data,report)

def close_all_cache_partitions(cache_liste : list[str],partitions_dict : dict[str,PartitionInfo]) -> None:
    for partition in cache_liste:
            partitions_dict[partition]["fichier"].close()

def main():
    """Initialisation des variables itératives"""
    nb_read_lines = 0
    nb_ignored_doubles = 0
    nb_written_lines = 0
    nb_partitions_created = 0
    partitions_dict = {}
    nb_line_per_partition = {}
    cache_liste = list()
    
    args = parse_input()

    output_repository = args.output

    with ExitStack() as stack:
        input_file = stack.enter_context(
            open(args.raw_input, mode="r",newline="")
        )
        r = csv.DictReader(input_file)
        fieldnames = r.fieldnames
        for row in r:
            nb_read_lines += 1
            date = row["event_timestamp"].split(" ")[0]
            partition = date + " | " + row["region"]
            if partition not in partitions_dict:
                writer = create_partition(row,partition,date,partitions_dict,cache_liste,output_repository,fieldnames)
                nb_line_per_partition[partition] = 0
                nb_partitions_created += 1
            else:
                if partition not in cache_liste:
                    writer = reopen_partition(cache_liste, partitions_dict, partition, fieldnames)
                else:
                    writer = partitions_dict[partition]["writer"]
                    mark_as_recently_used(cache_liste, partition)
            if row["order_id"] not in partitions_dict[partition]["ids"]:
                writer.writerow(row)
                partitions_dict[partition]["ids"].add(row["order_id"])
                nb_line_per_partition[partition] += 1
                nb_written_lines += 1
            else:
                nb_ignored_doubles += 1

    close_all_cache_partitions(cache_liste,partitions_dict)
    
    partition_report_data = build_json_data(nb_read_lines,nb_ignored_doubles,nb_written_lines,nb_partitions_created,nb_line_per_partition)
    write_report_json(output_repository,partition_report_data)

if __name__ == "__main__":
    main()