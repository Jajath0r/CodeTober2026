from simulator import SupplierSimulator
from concurrent.futures import ThreadPoolExecutor
from models import ProviderResult

def extract_providers(providers_file : str, limit : int) -> dict[str,ProviderResult]:
    source = SupplierSimulator(providers_file)
    return extract_all_providers(source, limit)

def extract_all_providers(source : SupplierSimulator,limit : int) -> dict[str,ProviderResult]:
    future_dict = {}
    provider_dict = {}
    with ThreadPoolExecutor(max_workers=limit) as executor:
        for provider in source.provider_ids:
            future_dict[provider] = executor.submit(source.fetch,provider)
        for provider in sorted(future_dict):
            # print(f"Extracting provider {provider}...")
            provider_dict[provider] = {}
            try:
                provider_dict[provider]["catalog"] = future_dict[provider].result()
                provider_dict[provider]["errors"] = None
            except Exception as e:
                provider_dict[provider]["catalog"] = None
                provider_dict[provider]["errors"] = str(e)
            # finally:
            #     print(f"Provider {provider} extracted !")
    return provider_dict

