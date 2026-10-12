import argparse
import csv
import json
from os import path, makedirs, replace
from contextlib import ExitStack
from sqlite3 import Connection,connect,Row

def parse_input():
    parser = argparse.ArgumentParser(
        description="state of affairs"
    )
    
    parser.add_argument(
        "account_file",
        type=str,
        help="accounts csv file"
    )
    
    parser.add_argument(
        "transfer_file",
        type=str,
        help="transfer csv file"
    )
    parser.add_argument(
        "batch",
        type=str,
        help="batch id"
    )
    
    parser.add_argument(
        "output_rep",
        type=str,
        help="output repository"
    )
    return parser.parse_args()

def create_sql_tables(connection : Connection) -> None:
    connection.execute(
        "CREATE TABLE IF NOT EXISTS accounts (account_id TEXT PRIMARY KEY, balance_cents INTEGER)"
    )
    connection.execute(
        "CREATE TABLE IF NOT EXISTS transfers (transfer_id TEXT PRIMARY KEY, source_account TEXT, destination_account TEXT, amount_cents INTEGER, status TEXT NOT NULL, FOREIGN KEY(source_account) REFERENCES accounts(account_id), FOREIGN KEY(destination_account) REFERENCES accounts(account_id))"
    )
    connection.commit()

def accounts_table_is_empty(connection: Connection) -> bool:
    row = connection.execute(
        "SELECT 1 FROM accounts LIMIT 1"
    ).fetchone()

    return row is None

def write_sql_accounts(connection : Connection, account_reader : csv.DictReader[str]) -> None:
    if not accounts_table_is_empty(connection):
        return 
    for row in account_reader:
        account_id = row["account_id"]
        balance = row["initial_balance_cents"]
        connection.execute(
            "INSERT INTO accounts (account_id, balance_cents) VALUES (?, ?)",
            (account_id, balance),
        )
    connection.commit()

def get_total_balance(connection: Connection) -> int:
    return connection.execute(
        "SELECT COALESCE(SUM(balance_cents), 0) FROM accounts"
    ).fetchone()[0]

def write_sql_transfer(connection : Connection, transfer_reader: csv.DictReader[str], nb_read : int,nb_accepted : int, nb_rejected : int) -> tuple[int,int,int]:
    accounts = {
        account["account_id"]: account["balance_cents"]
        for account in connection.execute("SELECT * FROM accounts")
    }
    for row in transfer_reader:
        amount = int(row["amount_cents"])
        source = row["source_account"]
        dest = row["destination_account"]
        id = row["transfer_id"]
        if accounts[source] >= amount:
            accounts[source] -= amount
            accounts[dest] += amount
            status = 'accepted'
            nb_accepted += 1
        else:
            status = 'rejected'
            nb_rejected += 1
        nb_read += 1
        connection.execute("INSERT INTO transfers VALUES(?,?,?,?,?)",(id, source,dest,amount,status))
    for account in accounts:
        connection.execute("UPDATE accounts SET balance_cents = ? WHERE account_id = ?",(accounts[account],account))
    connection.commit()
    return nb_read, nb_accepted, nb_rejected

def write_balances_csv(w : csv.DictWriter, connection : Connection) -> None:
    new_balance = [
        dict(row)
        for row in connection.execute("SELECT * FROM accounts")
    ]

    for account in new_balance:
        w.writerow(account)
    

def main():
    args = parse_input()
    output_rep = args.output_rep
    transfer_file_name = args.transfer_file+"_"+args.batch+".csv"
    if not path.exists(output_rep):
        makedirs(output_rep)
    balances = path.join(output_rep,"balances.csv")
    report = path.join(output_rep,"report.json")
    nb_read = 0
    nb_accepted = 0
    nb_rejected = 0
    total_balance_before_cents = 0
    db_file = path.join(output_rep,"state_of_affairs.db")
    connection = connect(db_file)
    connection.row_factory = Row
    create_sql_tables(connection)
    with ExitStack() as stack:
        account_file = stack.enter_context(
            open(args.account_file,"r",newline="")
        )
        account_reader = csv.DictReader(account_file)
        write_sql_accounts(connection,account_reader)
        total_balance_before_cents = get_total_balance(connection)
        transfer_file = stack.enter_context(
            open(transfer_file_name, "r",newline="")
        )
        transfer_reader = csv.DictReader(transfer_file)
        nb_read, nb_accepted, nb_rejected = write_sql_transfer(connection,transfer_reader,nb_read, nb_accepted, nb_rejected)
        balances_file = stack.enter_context(
            open(balances,"w",newline="")
        )
        w = csv.DictWriter(balances_file,fieldnames=["account_id","balance_cents"])
        w.writeheader()
        write_balances_csv(w, connection)
        total_balance_after_cents = get_total_balance(connection)
        report_data = {
            "batch":args.batch,
            "nb_read": nb_read,
            "nb_accepted": nb_accepted,
            "nb_rejected": nb_rejected,
            "total_balance_before_cents":total_balance_before_cents,
            "total_balance_after_cents":total_balance_after_cents
        }
        report_json = stack.enter_context(
            open(report,"w",newline="")
        )
        json.dump(report_data,report_json)
                
            
if __name__ == "__main__":
    main()