from datetime import datetime
import pycountry

def id_transaction_valide(ligne : dict[str,str],ids_vus : set[str]) -> tuple[bool,bool]:
    current_id = ligne['transaction']
    id_bool = (current_id!="")
    duplicate = (current_id in ids_vus)
    if id_bool :
        ids_vus.add(current_id)
    if duplicate:print(current_id, ids_vus)
    return (id_bool,duplicate)

def id_customer_valide(ligne : dict[str,str]) -> bool:
    return (ligne['customer']!="")

def timestamp_valide(ligne : dict[str,str]) -> bool:
    try:
        datetime.strptime(ligne['timestamp'], "%Y-%m-%d %H:%M:%S")
        return True
    except ValueError:
        return False

def country_valide(ligne : dict[str,str]) -> bool:
    pays = ligne['country']
    if len(pays)!=2 or pays.upper()!=pays:
        return False
    return pycountry.countries.get(alpha_2=pays) is not None

def amount_valide(ligne : dict[str,str]) -> bool:
    try:
        amount = float(ligne['amount'])
        return (amount >= 0)
    except ValueError:
        return False
    

def currency_valide(ligne : dict[str,str]) -> bool:
    return(ligne['currency'] in {"EUR","USD","GBP"})

def status_valide(ligne : dict[str,str]) -> bool:
    return  (ligne['status'] in {"SUCCESS","FAILED","PENDING"})

def normalize_data(ligne : dict[str,str], champ : str)  -> None:
    ligne[champ] = ligne[champ].strip().upper()

def valide_ligne(
        ligne : dict[str,bool],
        transaction_ids_vus : set[str]) -> dict[str,str]:
    for champ in ['transaction', 'customer','country','amount','currency','status']:
        normalize_data(ligne, champ) 
    transaction_bool,duplicate = id_transaction_valide(ligne,transaction_ids_vus)
    timestamp_bool = timestamp_valide(ligne)
    customer_bool = id_customer_valide(ligne)
    country_bool = country_valide(ligne)
    amount_bool = amount_valide(ligne)
    currency_bool = currency_valide(ligne)
    status_bool = status_valide(ligne)
    return {
        "transaction": transaction_bool,
        "timestamp":timestamp_bool,
        "customer":customer_bool,
        "country":country_bool,
        "amount":amount_bool,
        "currency":currency_bool,
        "status":status_bool,
        "duplicate": not duplicate
        }

