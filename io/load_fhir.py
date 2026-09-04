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
    """Recursively flattens dictionaries and lists into csv"""
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

def ndjson_to_csv(input_path, output_path):
    """
    Flatten ndjson file to csv
    Each ndjson resource is represented by one csv row
    """
    input_path = Path(input_path)
    if output_path is None:
        output_path = input_path.with_suffix(".csv")
    output_path = Path(output_path)

    rows = []
    with input_path.open("r", encoding="utf-8") as f:
        for line_num, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue

            try:
                record = json.loads(line)
            except json.JSONDecodeError as e:
                print(f"Skipping invalid json on line {line_num}: {e}")
                continue

            flattened = flatten_ndjson(record)
            flattened["_source_file"] = input_path.name
            flattened["_source_line"] = line_num
            rows.append(flattened)

    df = pd.DataFrame(rows)

    # Put id cols first
    id_cols = [
        "resourceType",
        "id",
        "identifier[0].value",
        "subject.reference",
        "subject.display",
        "_source_file",
        "_source_line"
    ]

    existing_id_cols = [col for col in id_cols if col in df.columns]
    remaining_cols = [col for col in df.columns if col not in existing_id_cols]
    df = df[existing_id_cols + remaining_cols]
    df.to_csv(output_path, index=False, encoding="utf-8")

    return df, output_path