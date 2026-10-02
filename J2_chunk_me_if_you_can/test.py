import pytest
from statistics import increment_status_counter,add_service_statistics,add_to_slowest


@pytest.mark.parametrize(
    "req_status, nb_2xx, nb_4xx, nb_5xx, expected_tuple",
    [
        ('203',0,0,0,(1,0,0)),
        ('405',0,1,0, (0,2,0)),
        ('555',1,1,0,(1,1,1))
    ]
)
def test_increment_status_counter(req_status,nb_2xx, nb_4xx, nb_5xx, expected_tuple):
    ligne = {"status_code": req_status}
    
    resultat = increment_status_counter(ligne, nb_2xx,nb_4xx,nb_5xx)
    
    assert resultat == expected_tuple
    
@pytest.mark.parametrize(
    "row, services_dict, expected_output",
    [
        ({'service':"payments",'status_code':"404",'response_time_ms':"400"},{},{'payments':{'nb_request':1, 'resp_time': 400, 'nb_5xx' : 0}}),
        ({'service':"payments",'status_code':"500",'response_time_ms':"400"},{'payments' : {'nb_request':1, 'resp_time': 400, 'nb_5xx' : 0}},{'payments' : {'nb_request':2, 'resp_time': 800, 'nb_5xx' : 1}}),
        ({'service':"shipments",'status_code':"200",'response_time_ms':"500"},{'payments' : {'nb_request':1, 'resp_time': 400, 'nb_5xx' : 0}},{'payments' : {'nb_request':1, 'resp_time': 400, 'nb_5xx' : 0},'shipments' : {'nb_request':1, 'resp_time': 500, 'nb_5xx' : 0}})
    ]
)
def test_add_service_statistics(row, services_dict, expected_output):
    resultat = add_service_statistics(row, services_dict)
    
    assert resultat == expected_output
 
    
@pytest.mark.parametrize(
    "row, top_10_slowest, expected_output",
    [
        ({'request_id': "REQ-0000007", 'service':'payments', 'endpoint':'/payments/139','response_time_ms':'480'},[],[{'request_id': "REQ-0000007", 'service':'payments', 'endpoint':'/payments/139','response_time_ms':480}]),
        (
            {'request_id':"REQ-0000011",'service':"catalog",'endpoint':"/products/search",'response_time_ms':"360"},
            [
                {'request_id':"REQ-0000004",'service':"catalog",'endpoint':"/categories",'response_time_ms':1809},
                {'request_id':"REQ-0000001",'service':"catalog",'endpoint':"/categories",'response_time_ms':1045},
                {'request_id':"REQ-0000009",'service':"payments",'endpoint':"/payments/3029",'response_time_ms':679},
                {'request_id':"REQ-0000002",'service':"orders",'endpoint':"/orders/7816",'response_time_ms':293},
                {'request_id':"REQ-0000007",'service':"payments",'endpoint':"/payments/139",'response_time_ms':286},
                {'request_id':"REQ-0000008",'service':"orders",'endpoint':"/orders/8882/cancel",'response_time_ms':242},
                {'request_id':"REQ-0000006",'service':"customers",'endpoint':"/customers/6503",'response_time_ms':174},
                {'request_id':"REQ-0000010",'service':"catalog",'endpoint':"/products",'response_time_ms':144},
                {'request_id':"REQ-0000005",'service':"shipping",'endpoint':"/shipments/6960",'response_time_ms':115},
                {'request_id':"REQ-0000003",'service':"customers",'endpoint':"/customers/3410",'response_time_ms':67}
                ],
            [
                {'request_id':"REQ-0000004",'service':"catalog",'endpoint':"/categories",'response_time_ms':1809},
                {'request_id':"REQ-0000001",'service':"catalog",'endpoint':"/categories",'response_time_ms':1045},
                {'request_id':"REQ-0000009",'service':"payments",'endpoint':"/payments/3029",'response_time_ms':679},
                {'request_id':"REQ-0000011",'service':"catalog",'endpoint':"/products/search",'response_time_ms':360},
                {'request_id':"REQ-0000002",'service':"orders",'endpoint':"/orders/7816",'response_time_ms':293},
                {'request_id':"REQ-0000007",'service':"payments",'endpoint':"/payments/139",'response_time_ms':286},
                {'request_id':"REQ-0000008",'service':"orders",'endpoint':"/orders/8882/cancel",'response_time_ms':242},
                {'request_id':"REQ-0000006",'service':"customers",'endpoint':"/customers/6503",'response_time_ms':174},
                {'request_id':"REQ-0000010",'service':"catalog",'endpoint':"/products",'response_time_ms':144},
                {'request_id':"REQ-0000005",'service':"shipping",'endpoint':"/shipments/6960",'response_time_ms':115}
                ]
            ),
        (
                    {'request_id':"REQ-0000011",'service':"catalog",'endpoint':"/products/search",'response_time_ms':"5"},
                    [
                        {'request_id':"REQ-0000004",'service':"catalog",'endpoint':"/categories",'response_time_ms':1809},
                        {'request_id':"REQ-0000001",'service':"catalog",'endpoint':"/categories",'response_time_ms':1045},
                        {'request_id':"REQ-0000009",'service':"payments",'endpoint':"/payments/3029",'response_time_ms':679},
                        {'request_id':"REQ-0000002",'service':"orders",'endpoint':"/orders/7816",'response_time_ms':293},
                        {'request_id':"REQ-0000007",'service':"payments",'endpoint':"/payments/139",'response_time_ms':286},
                        {'request_id':"REQ-0000008",'service':"orders",'endpoint':"/orders/8882/cancel",'response_time_ms':242},
                        {'request_id':"REQ-0000006",'service':"customers",'endpoint':"/customers/6503",'response_time_ms':174},
                        {'request_id':"REQ-0000010",'service':"catalog",'endpoint':"/products",'response_time_ms':144},
                        {'request_id':"REQ-0000005",'service':"shipping",'endpoint':"/shipments/6960",'response_time_ms':115},
                        {'request_id':"REQ-0000003",'service':"customers",'endpoint':"/customers/3410",'response_time_ms':67}
                        ],
                    [
                        {'request_id':"REQ-0000004",'service':"catalog",'endpoint':"/categories",'response_time_ms':1809},
                        {'request_id':"REQ-0000001",'service':"catalog",'endpoint':"/categories",'response_time_ms':1045},
                        {'request_id':"REQ-0000009",'service':"payments",'endpoint':"/payments/3029",'response_time_ms':679},
                        {'request_id':"REQ-0000002",'service':"orders",'endpoint':"/orders/7816",'response_time_ms':293},
                        {'request_id':"REQ-0000007",'service':"payments",'endpoint':"/payments/139",'response_time_ms':286},
                        {'request_id':"REQ-0000008",'service':"orders",'endpoint':"/orders/8882/cancel",'response_time_ms':242},
                        {'request_id':"REQ-0000006",'service':"customers",'endpoint':"/customers/6503",'response_time_ms':174},
                        {'request_id':"REQ-0000010",'service':"catalog",'endpoint':"/products",'response_time_ms':144},
                        {'request_id':"REQ-0000005",'service':"shipping",'endpoint':"/shipments/6960",'response_time_ms':115},
                        {'request_id':"REQ-0000003",'service':"customers",'endpoint':"/customers/3410",'response_time_ms':67}
                        ]
                    )
    ]
)
def test_add_to_slowest(row,top_10_slowest, expected_output):
    resultat = add_to_slowest(row, top_10_slowest)
    
    assert resultat == expected_output
    
