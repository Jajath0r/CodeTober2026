import pytest
from validations import is_valid_event_id,is_valid_event_type,is_valid_event_version,is_valid_timestamp,is_valid_customer_id,is_valid_metadata,has_correct_amount,has_correct_currency,has_correct_country,is_empty_field,is_correct_event

@pytest.fixture
def incorrect_event_1():
    data = {
        "event_id":"EVT-0001",
        "event_type" : "event",
        "event_version":'1',
        "timestamp": "2026-10-03 14:38:00",
        "customer_id":"CUST-1234",
        "amount":"79.50",
        "currency": "EUR",
        "country":"FR",
        "metadata":'{"channel":"web"}'
    }
    return data
@pytest.fixture
def incorrect_event_2():
    data = {
        "event_id":"",
        "event_type" : "order_created",
        "event_version":'1',
        "timestamp": "2026-10-03 14:38:00",
        "customer_id":"CUST-1234",
        "amount":"79.50",
        "currency": "EUR",
        "country":"FR",
        "metadata":'{"channel":"web"}'
    }
    return data
@pytest.fixture
def incorrect_event_3():
    data = {
        "event_id":"EVT-0001",
        "event_type" : "order_created",
        "event_version":'3',
        "timestamp": "2026-10-03 14:38:00",
        "customer_id":"CUST-1234",
        "amount":"79.50",
        "currency": "EUR",
        "country":"FR",
        "metadata":'{"channel":"web"}'
    }
    return data
@pytest.fixture
def incorrect_event_4():
    data = {
        "event_id":"EVT-0001",
        "event_type" : "order_created",
        "event_version":'1',
        "timestamp": "2026-10-03T14:38:00",
        "customer_id":"CUST-1234",
        "amount":"79.50",
        "currency": "EUR",
        "country":"FR",
        "metadata":'{"channel":"web"}'
    }
    return data
@pytest.fixture
def incorrect_event_5():
    data = {
        "event_id":"EVT-0001",
        "event_type" : "order_created",
        "event_version":'2',
        "timestamp": "2026-10-03 14:38:00",
        "customer_id":"",
        "amount":"79.50",
        "currency": "EUR",
        "country":"FR",
        "metadata":'{"channel":"web"}'
    }
    return data
@pytest.fixture
def incorrect_event_6():
    data = {
        "event_id":"EVT-0001",
        "event_type" : "order_created",
        "event_version":'2',
        "timestamp": "2026-10-03 14:38:00",
        "customer_id":"CUST-1234",
        "amount":"79.50",
        "currency": "EUR",
        "country":"FR",
        "metadata":'not-a-json'
    }
    return data
@pytest.fixture
def incorrect_order_1():
    data = {
        "event_id":"EVT-0001",
        "event_type" : "order_created",
        "event_version":'2',
        "timestamp": "2026-10-03 14:38:00",
        "customer_id":"CUST-1234",
        "amount":"-79.50",
        "currency": "EUR",
        "country":"FR",
        "metadata":'{"channel":"web"}'
    }
    return data
@pytest.fixture
def incorrect_order_2():
    data = {
        "event_id":"EVT-0001",
        "event_type" : "order_created",
        "event_version":'2',
        "timestamp": "2026-10-03 14:38:00",
        "customer_id":"CUST-1234",
        "amount":"79.50",
        "currency": "YEN",
        "country":"FR",
        "metadata":'{"channel":"web"}'
    }
    return data
@pytest.fixture
def incorrect_order_3():
    data = {
        "event_id":"EVT-0001",
        "event_type" : "order_created",
        "event_version":'2',
        "timestamp": "2026-10-03 14:38:00",
        "customer_id":"CUST-1234",
        "amount":"79.50",
        "currency": "EUR",
        "country":"USA",
        "metadata":'{"channel":"web"}'
    }
    return data
@pytest.fixture
def incorrect_payment_1():
    data = {
        "event_id":"EVT-0001",
        "event_type" : "order_created",
        "event_version":'2',
        "timestamp": "2026-10-03 14:38:00",
        "customer_id":"CUST-1234",
        "amount":"-79.50",
        "currency": "EUR",
        "country":"FR",
        "metadata":'{"channel":"web"}'
    }
    return data
@pytest.fixture
def incorrect_payment_2():
    data = {
        "event_id":"EVT-0001",
        "event_type" : "order_created",
        "event_version":'2',
        "timestamp": "2026-10-03 14:38:00",
        "customer_id":"CUST-1234",
        "amount":"79.50",
        "currency": "YEN",
        "country":"FR",
        "metadata":'{"channel":"web"}'
    }
    return data
@pytest.fixture
def incorrect_payment_3():
    data = {
        "event_id":"EVT-0001",
        "event_type" : "order_created",
        "event_version":'2',
        "timestamp": "2026-10-03 14:38:00",
        "customer_id":"CUST-1234",
        "amount":"79.50",
        "currency": "EUR",
        "country":"USA",
        "metadata":'{"channel":"web"}'
    }
    return data
@pytest.fixture
def correct_order():
    data = {
        "event_id":"EVT-0001",
        "event_type" : "order_created",
        "event_version":'2',
        "timestamp": "2026-10-03 14:38:00",
        "customer_id":"CUST-1234",
        "amount":"79.50",
        "currency": "EUR",
        "country":"FR",
        "metadata":'{"channel":"web"}'
    }
    return data
@pytest.fixture
def correct_payment():
    data = {
        "event_id":"EVT-0001",
        "event_type" : "payment_received",
        "event_version":'2',
        "timestamp": "2026-10-03 14:38:00",
        "customer_id":"CUST-1234",
        "amount":"79.50",
        "currency": "EUR",
        "country":"FR",
        "metadata":'{"channel":"web"}'
    }
    return data
@pytest.fixture
def correct_customer():
    data = {
        "event_id":"EVT-0001",
        "event_type" : "customer_updated",
        "event_version":'2',
        "timestamp": "2026-10-03 14:38:00",
        "customer_id":"CUST-1234",
        "amount":"",
        "currency": "",
        "country":"",
        "metadata":'{"channel":"web"}'
    }
    return data
@pytest.fixture
def correct_payment():
    data = {
        "event_id":"EVT-0001",
        "event_type" : "customer_updated",
        "event_version":'2',
        "timestamp": "2026-10-03 14:38:00",
        "customer_id":"CUST-1234",
        "amount":"79.50",
        "currency": "EUR",
        "country":"FR",
        "metadata":'{"channel":"web"}'
    }
    return data



@pytest.mark.parametrize(
    "event_id, expected",
    [
        ("",False),
        ("EVT-001",True)
    ]
)
def test_is_valid_event_id(event_id,expected):
    ligne = {"event_id":event_id}
    
    result = is_valid_event_id(ligne)
    
    assert result is expected
    
@pytest.mark.parametrize(
    "event_type, expected",
    [
        ("invalid", False),
        ("",False),
        ("order_created",True),
        ("payment_received",True),
        ("customer_updated",True)
    ]
)
def test_is_valid_event_type(event_type, expected):
    ligne = {"event_type":event_type}
    
    result = is_valid_event_type(ligne)
    
    assert result is expected


@pytest.mark.parametrize(
    "version, expected",
    [
        ('1', True),
        ('2', True),
        ('0', False),
        ('', False)
    ]
)
def test_is_valid_event_version(version, expected):
    ligne = {"event_version":version}
    
    result = is_valid_event_version(ligne)
    
    assert result is expected
    
@pytest.mark.parametrize(
    'timestamp, expected',
    [
        ("",False),
        ("Not-a-date", False),
        ("2026-10-02T08:38:00",False),
        ("2026/10/02 08:38:00", False),
        ("2026-10-02 08:38:00", True)
    ]
)
def test_is_valid_timestamp(timestamp, expected):
    ligne = {"timestamp": timestamp}
    
    result = is_valid_timestamp(ligne)
    
    assert result is expected
    

@pytest.mark.parametrize(
    'id, expected',
    [
        ('', False),
        ("CUST-9999",True)
    ]
)
def test_is_valid_customer_id(id, expected):
    ligne = {"customer_id": id}
    
    result = is_valid_customer_id(ligne)
    
    assert result is expected
    
    
@pytest.mark.parametrize(
    "metadata, expected",
    [
        ('{"channel":"web"}', True),
        ("{}", True),
        ("not-a-json", False)
    ]
)
def test_is_valid_metadata(metadata, expected):
    ligne = {"metadata":metadata}
    
    result = is_valid_metadata(ligne)
    
    assert result is expected
    

@pytest.mark.parametrize(
    "amount, expected",
    [
        ("twenty", False),
        ("-5.3",False),
        ("0", False),
        ("5.50", True)
    ]
)
def test_has_correct_amount(amount, expected):
    ligne = {"amount":amount}
    
    result = has_correct_amount(ligne)
    
    assert result is expected
    

@pytest.mark.parametrize(
    "currency, expected",
    [
        ("EUR",True),
        ("USD", True),
        ("GBP", True),
        ("YEN", False)
    ]
)
def test_has_correct_currency(currency, expected):
    ligne = {"currency":currency}
    
    result = has_correct_currency(ligne)
    
    assert result is expected
    

@pytest.mark.parametrize(
    "country, expected",
    [
        ("FR",True),
        ("USA", False)
    ]
)
def test_has_correct_country(country, expected):
    ligne = {"country":country}
    
    result = has_correct_country(ligne)
    
    assert result is expected
    

@pytest.mark.parametrize(
    "fieldname, fieldvalue, expected",
    [
        ("currency","",True),
        ("amount","5.50",False),
        ("country","USA",False)
    ]
)
def test_is_empty_field(fieldname, fieldvalue, expected):
    ligne = {fieldname: fieldvalue}
    
    result = is_empty_field(fieldname, ligne)
    
    assert result is expected


@pytest.mark.parametrize(
    "row, expected",
    [
        (incorrect_event_1,False),
        (incorrect_event_2,False),
        (incorrect_event_3,False),
        (incorrect_event_4,False),
        (incorrect_event_6,False),
        (correct_order,True),
        (correct_customer,True),
        (correct_payment,True)
    ]
)
def test_correct_event(row, expected):
    result = is_correct_event(row)
    
    assert result is expected