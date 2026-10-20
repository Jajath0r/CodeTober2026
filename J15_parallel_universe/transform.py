from models import ProviderResult

def transform_provider_dict(provider_dict : dict[str,ProviderResult]) -> dict[str, dict[str,str|int]]:
    result_dict = {}
    for provider in provider_dict:
        result_dict[provider] = {}
        if provider_dict[provider]["catalog"] is not None:
            result_dict[provider]["status"] = "SUCCESS"
            result_dict[provider]["nb_products"] = len(provider_dict[provider]["catalog"])
            result_dict[provider]["errors"] = ""
        else:
            result_dict[provider]["status"] = "FAILED"
            result_dict[provider]["nb_products"] = "-"
            result_dict[provider]["errors"] = provider_dict[provider]["errors"]
    return result_dict