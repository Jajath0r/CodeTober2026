import pytest
import json
import subprocess
import sys
from pathlib import Path

from extract import validate_config_file


def test_unknown_key():
    config = {
        "source": {
            "path": "../data/catalog_2026-10-01.json"
        },
        "destination": {
            "sqlite_path": "../output/catalog.db"
        },
        "behavior": {
            "invalid_product": "fail"
        },
        "debug": True
    }
    
    with pytest.raises(ValueError):
        validate_config_file(config)
        
def test_none_source():
    config = {
        "source": None,
        "destination": {
            "sqlite_path": "../output/catalog.db"
        },
        "behavior": {
            "invalid_product": "fail"
        }
    }
    
    with pytest.raises(ValueError) as exc_info:
        validate_config_file(config)

    assert "source" in str(exc_info.value).lower()

def test_invalid_config_no_side_effect(tmp_path):
    config_path = tmp_path / "config.json"
    destination = tmp_path / "output" / "catalog.db"

    config = {
        "source": {"path": "catalog_2026-10-01.json"},
        "destination": {"sqlite_path": "output/catalog.db"},
        "behavior": {"invalid_product": "ignore"}
    }

    config_path.write_text(json.dumps(config), encoding="utf-8")

    main_path = Path(__file__).parent / "main.py"

    result = subprocess.run(
        [sys.executable, str(main_path), str(config_path)],
        capture_output=True,
        text=True
    )
    assert result.returncode != 0
    assert "ValueError" in result.stderr
    assert "ignore" in result.stderr
    assert not destination.exists()
    assert not destination.parent.exists()
    
def test_independent_cwd(tmp_path):
    config = {
        "source": {"path": "catalog_2026-10-01.json"},
        "destination": {"sqlite_path": "output/catalog.db"},
        "behavior": {"invalid_product": "fail"}
    }
    catalog = {
        "products": [
            {
                "product_id": "P001",
                "name": "Clavier",
                "unit_price_cents": 2500
            }
        ]
    }
    main_path = Path(__file__).resolve().parent / "main.py"
    config_path = tmp_path / "config.json"
    catalog_path = tmp_path / "catalog_2026-10-01.json"
    other_directory = tmp_path / "other_directory"
    other_directory.mkdir()
    catalog_path.write_text(json.dumps(catalog), encoding="utf-8")
    config_path.write_text(json.dumps(config), encoding="utf-8")
    result = subprocess.run(
        [sys.executable, str(main_path), str(config_path)],
        cwd=other_directory,
        capture_output=True,
        text=True
    )
    destination = tmp_path / "output" / "catalog.db"
    assert result.returncode == 0, result.stderr
    assert destination.is_file()