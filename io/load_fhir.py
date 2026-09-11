import json
from concurrent.futures import ProcessPoolExecutor
import os
from pathlib import Path
import pandas as pd

def read_ndjson(path):
    path = Path(path)
    records = []

    with path.open("r", encoding="utf-8") as f:
        for line_num, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue

            try:
                record = json.loads(line)
            except json.JSONDecodeError as e:
                print(f"Skipping invalid JSON on line {line_num}: {e}")
                continue

            if isinstance(record, dict):
                records.append(record)

    return records

def parse_line_batch(lines):
    """Worker function executed in parallel across CPU cores"""
    records = []
    for line in lines:
        line = line.strip()
        if line:
            try:
                records.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return records

def read_ndjson_parallel(path, chunk_size=50000):
    """Reads large ndjson files using all available CPU cores"""
    records = []
    max_workers = os.cpu_count() or 4
    
    with open(path, "r", encoding="utf-8") as f, ProcessPoolExecutor(max_workers=max_workers) as executor:
        batch = []
        futures = []
        
        for line in f:
            batch.append(line)
            if len(batch) >= chunk_size:
                futures.append(executor.submit(parse_line_batch, batch))
                batch = []
        if batch:
            futures.append(executor.submit(parse_line_batch, batch))

        for future in futures:
            records.extend(future.result())

    return records

def flatten_ndjson(obj, parent_key="", sep="."):
    """Recursively flattens dictionaries and lists"""
    items = {}

    if isinstance(obj, dict):
        for key, value in obj.items():
            new_key = f"{parent_key}{sep}{key}" if parent_key else key
            if isinstance(value, (dict, list)):
                items.update(flatten_ndjson(value, new_key, sep))
            else:
                items[new_key] = value

    elif isinstance(obj, list):
        for index, value in enumerate(obj):
            new_key = f"{parent_key}[{index}]"
            if isinstance(value, (dict, list)):
                items.update(flatten_ndjson(value, new_key, sep))
            else:
                items[new_key] = value

    else:
        items[parent_key] = obj

    return items
