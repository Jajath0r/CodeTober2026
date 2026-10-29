import argparse
import duckdb
from os import path, makedirs
from orchestrator import execute_function_in_order
from extract import get_config_graph
from pathlib import Path

def parse_input():
	parser = argparse.ArgumentParser(
		description="Duck Season"
	)

	parser.add_argument(
		"--config",
		type=str,
		required=True,
		help="config file path"
	)
	
	parser.add_argument(
		"--output-dir",
		type=str,
		required=True,
		help="Directory for generated reports"
	)
 
	return parser.parse_args()

def main():
	args = parse_input()
	output_dir = args.output_dir
	project_root = Path(__file__).resolve().parent
	work_dir = Path(args.output_dir).resolve()
	execute_function_in_order(graph=get_config_graph(args.config),project_root=project_root,work_dir=work_dir,run_id="run_001")


if __name__ == "__main__":
    main()