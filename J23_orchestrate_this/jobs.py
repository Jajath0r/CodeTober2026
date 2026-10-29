"""Provided business jobs for J23. The orchestrator must not edit them.

Call execute(task_id, project_root, work_dir, run_id) -> dict.
Tasks are replay-safe and write their artifacts under work_dir.
"""
import csv
import json
import os
from collections import defaultdict
from pathlib import Path

class TransientJobError(RuntimeError):
    """A recoverable error which is safe to retry."""

class PermanentJobError(RuntimeError):
    """An error for which retrying the same input is not useful."""


def _read_csv(p):
    with p.open(newline='', encoding='utf-8') as f:
        return list(csv.DictReader(f))


def _write_json(p, value):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(value, indent=2, sort_keys=True), encoding='utf-8')


def _read_json(p):
    return json.loads(p.read_text(encoding='utf-8'))


def execute(task_id: str, project_root: Path, work_dir: Path, run_id: str) -> dict:
    """Execute exactly one job; raise a typed error on failure.

    The orchestration layer owns scheduling, tracking, retry, and reporting.
    Environment J23_FAIL_ONCE=<task_id> injects one transient failure per
    (work_dir, task_id); J23_FAIL_ALWAYS=<task_id> injects a permanent failure.
    """
    project_root, work_dir = Path(project_root), Path(work_dir)
    work_dir.mkdir(parents=True, exist_ok=True)
    if os.getenv('J23_FAIL_ALWAYS') == task_id:
        raise PermanentJobError(f'injected permanent failure: {task_id}')
    marker = work_dir / f'.failed_once_{task_id}'
    if os.getenv('J23_FAIL_ONCE') == task_id and not marker.exists():
        marker.touch()
        raise TransientJobError(f'injected transient failure: {task_id}')

    if task_id == 'import_orders':
        rows = _read_csv(project_root / 'data' / 'orders.csv')
        _write_json(work_dir / 'orders.json', rows)
        return {'rows': len(rows)}
    if task_id == 'import_products':
        rows = _read_csv(project_root / 'data' / 'products.csv')
        _write_json(work_dir / 'products.json', rows)
        return {'rows': len(rows)}
    if task_id == 'check_orders':
        rows = _read_json(work_dir / 'orders.json')
        if any(not r.get('order_id') or not r.get('product_id') or not r.get('status') for r in rows):
            raise PermanentJobError('required orders fields missing')
        _write_json(work_dir / 'valid_orders.json', rows)
        return {'rows': len(rows)}
    if task_id == 'check_products':
        rows = _read_json(work_dir / 'products.json')
        if any(not r.get('product_id') or not r.get('category') for r in rows):
            raise PermanentJobError('required products fields missing')
        _write_json(work_dir / 'valid_products.json', rows)
        return {'rows': len(rows)}
    if task_id == 'aggregate':
        orders = _read_json(work_dir / 'valid_orders.json')
        categories = {r['product_id']: r['category'] for r in _read_json(work_dir / 'valid_products.json')}
        totals = defaultdict(lambda: {'orders': 0, 'items': 0, 'revenue_cents': 0})
        for r in orders:
            if r['status'] != 'completed':
                continue
            category = categories.get(r['product_id'])
            if category is None:
                raise PermanentJobError(f'unknown product {r["product_id"]}')
            t = totals[category]
            t['orders'] += 1
            t['items'] += int(r['quantity'])
            t['revenue_cents'] += int(r['quantity']) * int(r['unit_price_cents'])
        result = [{'category': category, **values} for category, values in sorted(totals.items())]
        _write_json(work_dir / 'aggregate.json', result)
        return {'categories': len(result)}
    if task_id == 'publish':
        rows = _read_json(work_dir / 'aggregate.json')
        target = work_dir / 'sales_by_category.csv'
        with target.open('w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=['category', 'orders', 'items', 'revenue_cents'])
            writer.writeheader()
            writer.writerows(rows)
        return {'published': str(target)}
    raise PermanentJobError(f'unknown task: {task_id}')
