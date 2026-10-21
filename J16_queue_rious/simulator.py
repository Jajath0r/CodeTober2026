"""CodeTober J13: deterministic catalog-source simulator.

This is test infrastructure supplied with the exercise; it is not the retry implementation.
"""
from __future__ import annotations

import json
from pathlib import Path


class TransientSourceError(RuntimeError):
    """Temporary source outage; a later call can succeed."""


class PermanentSourceError(RuntimeError):
    """Non-recoverable source error for this run."""


SCENARIOS = {
    "healthy": (0, None),
    "one_outage": (1, None),
    "two_outages": (2, None),
    "unavailable": (None, "transient"),
    "access_denied": (None, "permanent"),
}


class SimulatedCatalogSource:
    """Use one instance throughout an execution; `calls` counts attempts.

    Call `.fetch()` to retrieve the catalog object as a Python dictionary.
    """

    def __init__(self, catalog_path: str | Path, scenario: str = "healthy") -> None:
        if scenario not in SCENARIOS:
            raise ValueError(f"Unknown scenario: {scenario}")
        self.catalog_path = Path(catalog_path)
        self.scenario = scenario
        self.calls = 0

    def fetch(self) -> dict:
        self.calls += 1
        initial_failures, failure_kind = SCENARIOS[self.scenario]
        if failure_kind == "permanent":
            raise PermanentSourceError("Catalog access denied")
        if failure_kind == "transient" or (
            initial_failures is not None and self.calls <= initial_failures
        ):
            raise TransientSourceError("Catalog service temporarily unavailable")
        return json.loads(self.catalog_path.read_text(encoding="utf-8"))
