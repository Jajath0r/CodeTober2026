import argparse
from sqlite3 import connect,Row
from os import path,makedirs
from extract import get_catalog
from load import create_catalog_table, insert_product_in_catalog

def parse_input():
    parser = argparse.ArgumentParser(
        description="Slowly but surely"
    )
    
    parser.add_argument(
        "input_rep",
        type=str,
        help="catalog repository path"
    )
    
    parser.add_argument(
        "input_file",
        type=str,
        help="catalog filename"
    )
    parser.add_argument(
        "output_rep",
        type=str,
        help="output repository"
    )
    
    return parser.parse_args()


def main():
    args = parse_input()
    input_rep = args.input_rep
    catalog = args.input_file
    output_rep = args.output_rep
    if not path.exists(output_rep):
        makedirs(output_rep)
    # 1. Récupérer le fichier catalogue et sa date
    catalog_date = catalog.removeprefix("catalog_").removesuffix(".json")
    catalog_path = path.join(input_rep, catalog)
    catalog_dict = get_catalog(catalog_path)
    # 2. Ouvrir la connexion SQLite
    #    avec row_factory = Row
    db_path = path.join(output_rep,"catalog.db")
    connection = connect(db_path)
    connection.row_factory = Row
    try:
        # 3. Créer la table catalog si nécessaire
        create_catalog_table(connection)
        # 4. Extraire les produits du catalogue JSON
        for product_id, product in catalog_dict.items():
            row = {"product_id": product_id, **product}
            insert_product_in_catalog(connection, row, catalog_date)

    except Exception:
        connection.rollback()
        raise
    else:
        connection.commit()
    finally:
        connection.close()
if __name__ == "__main__":
    main()