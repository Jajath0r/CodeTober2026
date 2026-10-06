import pytest
from main import process_line, update_latest_updated_at
from datetime import datetime

@pytest.mark.parametrize(
    "ligne, event_dict, nb_replaced_version, nb_invalid_lines, expected_tuple, expected_dict",
    [
        (
            {
                "event_id":"",
                "updated_at":"2026-10-06 14:18:00"
            },
            {},
            0,
            0,
            (0,1),
            {}
        ),
        (
            {
                "event_id":"EVT-0001",
                "updated_at":"not_a_date"
            },
            {},
            0,
            0,
            (0,1),
            {}
        ),
        (
            {
                "event_id":"EVT-0001",
                "updated_at":"2026-10-06 14:18:00",
                "status":"",
                "payload":""
            },
            {},
            0,
            0,
            (0,0),
            {
                "EVT-0001":{
                        "updated_at":datetime.strptime("2026-10-06 14:18:00","%Y-%m-%d %H:%M:%S"),
                        "status":"",
                        "payload":""
                    }
            }
        ),
        (
            {
                "event_id":"EVT-0002",
                "updated_at":"2026-10-06 14:19:00",
                "status":"","payload":""
            },
            {
                "EVT-0001":{
                    "updated_at":datetime.strptime("2026-10-06 14:18:00","%Y-%m-%d %H:%M:%S"),
                    "status":"",
                    "payload":""
                }
            },
            0,
            0,
            (0,0),
            {
                "EVT-0001":{
                    "updated_at":datetime.strptime("2026-10-06 14:18:00","%Y-%m-%d %H:%M:%S"),
                    "status":"",
                    "payload":""
                },
                "EVT-0002":{
                    "updated_at":datetime.strptime("2026-10-06 14:19:00","%Y-%m-%d %H:%M:%S"),
                    "status":"",
                    "payload":""
                }
            }
        ),
        (
            {
                "event_id":"EVT-0001",
                "updated_at":"2026-10-06 14:19:00",
                "status":"REJECTED",
                "payload":""
            },
            {
                "EVT-0001":{
                    "updated_at":datetime.strptime("2026-10-06 14:18:00","%Y-%m-%d %H:%M:%S"),
                    "status":"",
                    "payload":""
                }
            },
            0,
            0,
            (1,0),
            {
                "EVT-0001":{
                    "updated_at":datetime.strptime("2026-10-06 14:19:00","%Y-%m-%d %H:%M:%S"),
                    "status":"REJECTED",
                    "payload":""
                }
            }
        ),
        (
            {
                "event_id":"EVT-0001",
                "updated_at":"2026-10-06 14:17:00",
                "status":"REJECTED",
                "payload":""
            },
            {
                "EVT-0001":{
                    "updated_at":datetime.strptime("2026-10-06 14:18:00","%Y-%m-%d %H:%M:%S"),
                    "status":"",
                    "payload":""
                }
            },
            0,
            0,
            (0,0),
            {
                "EVT-0001":{
                    "updated_at":datetime.strptime("2026-10-06 14:18:00","%Y-%m-%d %H:%M:%S"),
                    "status":"",
                    "payload":""
                }
            }
        ),
        (
            {
                "event_id":"EVT-0001",
                "updated_at":"2026-10-06 14:18:00",
                "status":"REJECTED",
                "payload":""
            },
            {
                "EVT-0001":{
                    "updated_at":datetime.strptime("2026-10-06 14:18:00","%Y-%m-%d %H:%M:%S"),
                    "status":"",
                    "payload":""
                }
            },
            0,
            0,
            (0,0),
            {
                "EVT-0001":{
                    "updated_at":datetime.strptime("2026-10-06 14:18:00","%Y-%m-%d %H:%M:%S"),
                    "status":"",
                    "payload":""
                }
            }
        )
    ]
)
def test_process_line(ligne, event_dict, nb_replaced_version, nb_invalid_lines, expected_tuple, expected_dict):
    resultat = process_line(ligne,event_dict, nb_replaced_version,nb_invalid_lines)
    
    assert resultat == expected_tuple
    assert event_dict == expected_dict
    
    
@pytest.mark.parametrize(
    "id, status, payload, event_dict, timestamp, nb_replaced_versions, expected_output, expected_dict",
    [
        (
            "EVT-0001",
            "status",
            "payload",
            {},
            datetime.strptime("2026-10-06 14:48:00","%Y-%m-%d %H:%M:%S"),
            0,
            0,
            {
                "EVT-0001":{
                    "updated_at":datetime.strptime("2026-10-06 14:48:00","%Y-%m-%d %H:%M:%S"),
                    "status":"status",
                    "payload":"payload"
                }
            }
        ),
        (
            "EVT-0001",
            "new_status",
            "new_payload",
            {
                "EVT-0001":{
                    "updated_at":datetime.strptime("2026-10-06 14:48:00","%Y-%m-%d %H:%M:%S"),
                    "status":"status",
                    "payload":"payload"
                }
            },
            datetime.strptime("2026-10-06 14:49:00","%Y-%m-%d %H:%M:%S"),
            0,
            1, 
            {
                "EVT-0001":{
                    "updated_at":datetime.strptime("2026-10-06 14:49:00","%Y-%m-%d %H:%M:%S"),
                    "status":"new_status",
                    "payload":"new_payload"
                }
            }
        ),
        (
            "EVT-0001",
            "new_status",
            "new_payload",
            {
                "EVT-0001":{
                    "updated_at":datetime.strptime("2026-10-06 14:48:00","%Y-%m-%d %H:%M:%S"),
                    "status":"status",
                    "payload":"payload"
                }
            },
            datetime.strptime("2026-10-06 14:48:00","%Y-%m-%d %H:%M:%S"),
            0,
            0, 
            {
                "EVT-0001":{
                    "updated_at":datetime.strptime("2026-10-06 14:48:00","%Y-%m-%d %H:%M:%S"),
                    "status":"status",
                    "payload":"payload"
                }
            }
        ),
        (
            "EVT-0001",
            "new_status",
            "new_payload",
            {
                "EVT-0001":{
                    "updated_at":datetime.strptime("2026-10-06 14:48:00","%Y-%m-%d %H:%M:%S"),
                    "status":"status",
                    "payload":"payload"
                }
            },
            datetime.strptime("2026-10-06 14:47:00","%Y-%m-%d %H:%M:%S"),
            0,
            0, 
            {
                "EVT-0001":{
                    "updated_at":datetime.strptime("2026-10-06 14:48:00","%Y-%m-%d %H:%M:%S"),
                    "status":"status",
                    "payload":"payload"
                }
            }
        )
    ]
)
def test_update_latest_updated_at(id, status, payload, event_dict, timestamp, nb_replaced_versions,expected_output,expected_dict):
    resultat = update_latest_updated_at(id,status,payload,event_dict,timestamp,nb_replaced_versions)
    
    assert resultat == expected_output
    assert event_dict == expected_dict