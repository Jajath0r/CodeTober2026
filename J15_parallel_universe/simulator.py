"""Simulateur de fournisseurs pour CodeTober J15.

Fourni comme infrastructure de test : tu n'as pas à modifier ce fichier.
Les appels sont bloquants (I/O simulée), sans réseau.
"""
from __future__ import annotations

import json
import threading
import time
from pathlib import Path
from typing import Any


class ProviderError(RuntimeError):
    pass


class SupplierSimulator:
    def __init__(self, file_path: str | Path):
        data = json.loads(Path(file_path).read_text(encoding="utf-8"))
        providers = data["providers"]
        self._providers: dict[str, dict[str, Any]] = {}
        for provider in providers:
            name = provider["provider_id"]
            if name in self._providers:
                raise ValueError(f"Duplicate provider_id: {name}")
            self._providers[name] = provider
        self._lock = threading.Lock()
        self.active_calls = 0
        self.max_active_calls = 0
        self.finished_order: list[str] = []
        self.call_count: dict[str, int] = {name: 0 for name in self._providers}

    @property
    def provider_ids(self) -> list[str]:
        return list(self._providers)

    def fetch(self, provider_id: str) -> list[dict[str, Any]]:
        """Retourne les produits d'un fournisseur ou lève ProviderError.

        Métriques partagées et synchronisées : active_calls, max_active_calls,
        finished_order et call_count. Utiliser une seule instance pour tout un run.
        """
        provider = self._providers[provider_id]
        with self._lock:
            self.active_calls += 1
            self.max_active_calls = max(self.max_active_calls, self.active_calls)
            self.call_count[provider_id] += 1
        try:
            time.sleep(provider["delay_seconds"])
            if provider["fail"]:
                raise ProviderError(f"Supplier {provider_id} is unavailable")
            return [item.copy() for item in provider["products"]]
        finally:
            with self._lock:
                self.finished_order.append(provider_id)
                self.active_calls -= 1
