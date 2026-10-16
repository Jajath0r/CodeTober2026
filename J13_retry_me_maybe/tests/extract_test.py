from extract import fetch_catalog
from simulator import SimulatedCatalogSource

def test_retry_delays():
    delays = []

    def fake_sleep(seconds):
        delays.append(seconds)

    source = SimulatedCatalogSource(
        "data/catalog.json",
        scenario="two_outages"
    )

    fetch_catalog(source, sleep_func=fake_sleep)

    assert source.calls == 3
    assert delays == [0.5, 1.0]