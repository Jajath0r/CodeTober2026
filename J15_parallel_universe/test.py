from simulator import SupplierSimulator
from extract import extract_all_providers

def test_concurrent_extraction():
    # ARRANGE : préparer le scénario
    source = SupplierSimulator("data/providers_all_ok.json")
    limit = 2

    # ACT : exécuter l'extraction
    results = extract_all_providers(source, limit)

    # ASSERT : vérifier les résultats
    assert len(results) == 5

    for provider in results:
        assert results[provider]["catalog"] is not None
        assert results[provider]["errors"] is None

    # Vérifier la concurrence
    assert source.max_active_calls > 1
    assert source.max_active_calls <= limit
    
def test_partial_failure():
    source = SupplierSimulator("data/providers.json")
    limit = 2
    
    results = extract_all_providers(source,limit)
    
    assert len(results) == 5
    
    errors = sum(1 for provider in results if results[provider]["errors"]is not None)
    successes = sum(1 for provider in results if results[provider]["catalog"]is not None)
    assert errors == 1
    assert successes == 4
    
    assert results["gamma"]["catalog"] is None
    assert results["gamma"]["errors"] is not None
    
def test_deterministic_order():
    source_1 = SupplierSimulator("data/providers.json")
    source_2 = SupplierSimulator("data/providers_shuffled.json")

    results_1 = extract_all_providers(source_1, 2)
    results_2 = extract_all_providers(source_2, 2)

    assert list(results_1) == sorted(results_1)
    assert list(results_1) == list(results_2)