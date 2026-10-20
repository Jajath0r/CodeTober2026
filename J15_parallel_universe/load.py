from os import path, makedirs
import json

def load_output_json(output_rep : str, result_dict : dict[str, dict[str,str|int]]) -> None:
    if not path.exists(output_rep):
        makedirs(output_rep)
    output_json = path.join(output_rep,"report.json")
    with open(output_json,"w") as output:
        json.dump(result_dict,output)