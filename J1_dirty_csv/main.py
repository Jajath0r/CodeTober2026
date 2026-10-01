import argparse
import csv
from collections import Counter
import json
from os import path,makedirs

from validation import valide_ligne

"""PRÉ-JOB : Création des sorties et compteurs"""
transactions_cleans = []
transactions_rejected = []
quality_report = []
transaction_ids_vus = set()
champs = ['transaction', 'timestamp', 'customer', 'country', 'amount', 'currency', 'status']
rejets = champs + ['duplicate']
compteur_rejets = Counter({cle : 0 for cle in rejets})
nb_lignes = 0

"""PARSING"""
parser = argparse.ArgumentParser(
    description="Nettoyage CSV"
)

parser.add_argument(
    "entrée",
    type=str,
    help="Fichier à nettoyer"
)

parser.add_argument(
    "sortie",
    type=str,
    help="Dossier contenants les outputs"
)

args = parser.parse_args()


"""Création des noms de fichier de sortie"""
output_rep = args.sortie
if not path.exists(output_rep):
    makedirs(output_rep)
clean = path.join(output_rep, "transactions_clean.csv")
rejected = path.join(output_rep,"transactions_rejected.csv")
report = path.join(output_rep,"quality_report.json")

"""LECTURE CSV"""
with open(args.entrée, mode = 'r', newline='') as fichier_entree:
    r = csv.DictReader(fichier_entree, fieldnames=champs)
    header = next(r)
    for ligne in r:
        nb_lignes += 1
        # Si chaque ligne comporte bien les 7 cellules requises et qu'aucune de ces cellules n'est vide 
        validations = valide_ligne(ligne, transaction_ids_vus)
        if all(validations.values()):
            transactions_cleans.append(ligne)
        else:
            rejection_reasons = []
            for motif, est_valide in validations.items():
                if not est_valide:
                    compteur_rejets[motif] += 1
                    rejection_reasons.append(motif)
            ligne['rejection_reason']=" ".join(rejection_reasons)
            transactions_rejected.append(ligne)

"""ECRITURE CSV"""
with open(clean, mode = "w", newline = '') as fichier_clean:
    w = csv.DictWriter(fichier_clean, fieldnames=champs)
    w.writeheader()
    for ligne in transactions_cleans:
        w.writerow(ligne)
        
with open(rejected, mode = "w", newline = '') as fichier_rejets:
    w = csv.DictWriter(fichier_rejets, fieldnames=champs+['rejection_reason'])
    w.writeheader()
    for ligne in transactions_rejected:
        w.writerow(ligne)


quality_data = {
    "total_rows" : nb_lignes,
    "valid_rows" : len(transactions_cleans),
    "rejected_rows" : len(transactions_rejected),
    "duplicate_rows" : compteur_rejets["duplicate"],
    "rejection_reasons":compteur_rejets
}
with open(report,"w") as quality_report_json:
    json.dump(quality_data,quality_report_json)