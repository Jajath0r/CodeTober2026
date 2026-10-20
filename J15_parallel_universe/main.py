import argparse
from extract import extract_providers
from transform import transform_provider_dict
from load import load_output_json

def parse_input():
    parser = argparse.ArgumentParser(
        description="parallel universe"
    )
    
    parser.add_argument(
        "providers_file",
        type=str,
        help="providers file name"
    )
    
    parser.add_argument(
        "limit",
        type=int,
        help="max appels concurrents"
    )
    
    parser.add_argument(
        "output_rep",
        type=str,
        help="output repository name"
    )
    
    return parser.parse_args()

def main():
    args = parse_input()
    provider_dict = extract_providers(args.providers_file, args.limit)
    result_dict = transform_provider_dict(provider_dict)
    load_output_json(args.output_rep,result_dict)


if __name__ == "__main__":
    main()