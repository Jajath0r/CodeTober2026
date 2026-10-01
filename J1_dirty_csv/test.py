import pytest
from validation import id_transaction_valide, id_customer_valide, timestamp_valide,country_valide,amount_valide,currency_valide,status_valide,normalize_data,valide_ligne

@pytest.mark.parametrize(
    "transaction, ids_vus, expected_output, expected_set",
    [
        ("",set(),(False, False),set()),
        ("TXN-1021",{'TXN-1021'},(True, True),{'TXN-1021'}),
        ("TXN-1021", set(),(True, False),{'TXN-1021'}),
        ("TXN-1021", {'TXN-1009'},(True, False),{'TXN-1009','TXN-1021'})
    ]
)
def test_transaction_validation(transaction, ids_vus, expected_output,expected_set):
    ligne = {"transaction":transaction}
    
    resultat = id_transaction_valide(ligne, ids_vus)
    
    assert resultat == expected_output
    assert ids_vus == expected_set


@pytest.mark.parametrize(
    "id, expected",
    [
        ("",False),
        ("CUST-001",True)
    ]
)
def test_customer_validation(id, expected):
    ligne = {"customer": id}
    
    resultat = id_customer_valide(ligne)
    
    assert resultat is expected

    
@pytest.mark.parametrize(
    "timestamp, expected",
    [
        ("2026-09-30T08:14:22", False),
        ("not-a-date", False),
        ("2026-09-30 08:14:22", True),
    ]
)
def test_timestamp_validation(timestamp, expected):
    ligne = {"timestamp": timestamp}

    resultat = timestamp_valide(ligne)

    assert resultat is expected
    
@pytest.mark.parametrize(
    "country, expected",
    [
        ("USA",False),
        ("",False),
        ("XX",False),
        ("FR",True)
    ]
)
def test_country_validation(country, expected):
    ligne = {"country":country}
    
    resultat = country_valide(ligne)
    
    assert resultat is expected
    
    
@pytest.mark.parametrize(
    "amount, expected",
    [
        ("", False),
        ("twenty-two",False),
        ("-5.50", False),
        ("8",True),
        ("5.39",True)
    ]
)
def test_amount_validation(amount, expected):
    ligne = {"amount":amount}
    
    resultat = amount_valide(ligne)
    
    assert resultat is expected
    

@pytest.mark.parametrize(
    "currency, expected",
    [
        ("", False),
        ("CAD",False),
        ("USD", True),
        ("EUR",True),
        ("GBP",True)
    ]
)
def test_currency_validation(currency, expected):
    ligne = {"currency":currency}
    
    resultat = currency_valide(ligne)
    
    assert resultat is expected
    
    
@pytest.mark.parametrize(
    "status, expected",
    [
        ("", False),
        ("None",False),
        ("SUCCESS", True),
        ("FAILED",True),
        ("PENDING",True)
    ]
)
def test_status_validation(status, expected):
    ligne = {"status":status}
    
    resultat = status_valide(ligne)
    
    assert resultat is expected
    

@pytest.mark.parametrize(
    "champ, valeur, expected",
    [
        ("currency"," EUR ", "EUR"),
        ("customer","CUST 001", "CUST 001"),
        ("status","SUCCESS","SUCCESS"),
        ("country", "fr","FR"),
        ("status", " failed ", "FAILED"),
        ("customer", "   ", "")
    ]
)
def test_data_normalization(champ, valeur, expected):
    ligne = {champ: valeur}
    normalize_data(ligne,champ)
    
    resultat = ligne[champ]
    
    assert resultat == expected
    
#{'transaction': 'TXN-1021', 'timestamp': '2026-09-30 10:01:44', 'customer': 'CUST-022', 'country': 'DE', 'amount': '75.00', 'currency': 'EUR', 'status': 'SUCCESS'}

@pytest.mark.parametrize(
    "ligne, ids_vus, expected",
    [
        ({'transaction': 'TXN-1021', 'timestamp': '2026-09-30 10:01:44', 'customer': 'CUST-022', 'country': 'DE', 'amount': '75.00', 'currency': 'EUR', 'status': 'SUCCESS'},set(),{'transaction': True, 'timestamp': True, 'customer': True, 'country': True, 'amount': True, 'currency': True, 'status': True, 'duplicate':True}),
        ({'transaction': 'TXN-1021', 'timestamp': '2026-09-30 10:01:44', 'customer': 'CUST-022', 'country': 'DE', 'amount': '-7.50', 'currency': 'EUR', 'status': 'SUCCESS'},set(),{'transaction': True, 'timestamp': True, 'customer': True, 'country': True, 'amount': False, 'currency': True, 'status': True, 'duplicate':True}),
        ({'transaction': 'TXN-1021', 'timestamp': '2026-09-30 10:01:44', 'customer': 'CUST-022', 'country': 'XX', 'amount': '', 'currency': 'EUR', 'status': ' done '},set(),{'transaction': True, 'timestamp': True, 'customer': True, 'country': False, 'amount': False, 'currency': True, 'status': False, 'duplicate':True}),
        ({'transaction': 'TXN-1021', 'timestamp': '2026-09-30 10:01:44', 'customer': 'CUST-022', 'country': 'DE', 'amount': '75.00', 'currency': 'EUR', 'status': 'SUCCESS'},{'TXN-1021'},{'transaction': True, 'timestamp': True, 'customer': True, 'country': True, 'amount': True, 'currency': True, 'status': True, 'duplicate':False}),
    ]
)
def test_ligne_validation(ligne, ids_vus, expected):
    resultat = valide_ligne(ligne,ids_vus)
    
    assert resultat == expected