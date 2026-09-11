import json
from pathlib import Path
import pandas as pd
from load_fhir import flatten_ndjson

def _ndjson_to_df(input_path):
    """Helper to load and flatten FHIR ndjson to dataframe"""
    input_path = Path(input_path)
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

    return df[existing_id_cols + remaining_cols]

def ndjson_to_csv(input_path, output_path):
    """
    Flatten ndjson file to csv
    Each ndjson resource is represented by one csv row
    """
    input_path = Path(input_path)
    if output_path is None:
        output_path = input_path.with_suffix(".csv")
    output_path = Path(output_path)

    df = _ndjson_to_df(input_path)
    df.to_csv(output_path, index=False)
    return df

def ndjson_to_parquet(input_path, output_path=None, compression="snappy"):
    """Flatten ndjson and save as parquet"""
    input_path = Path(input_path)
    if output_path is None:
        output_path = input_path.with_suffix(".parquet")
    output_path = Path(output_path)

    df = _ndjson_to_df(input_path)

    # Ensure all col names are str for pyarrow
    df.columns = df.columns.astype(str)

    df.to_parquet(str(output_path), index=False, compression=compression) # type: ignore
    return df

def ndjson_to_pkl(input_path, output_path):
    """Flatten ndjson and save as pickle file"""
    input_path = Path(input_path)
    if output_path is None:
        output_path = input_path.with_suffix(".pkl")
    output_path = Path(output_path)

    df = _ndjson_to_df(input_path)
    df.to_pickle(output_path)
    return df