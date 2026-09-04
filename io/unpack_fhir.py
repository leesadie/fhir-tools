import zipfile
import tarfile
import gzip
import shutil
import tempfile
from pathlib import Path

ARCHIVE_EXT = ['.zip', '.tar', '.tar.gz', '.tgz', '.tar.bz2', '.gz']
FHIR_EXT = ['.ndjson', '.json']

def get_unique_path(path: Path) -> Path:
    if not path.exists():
        return path
    counter = 1
    while True:
        new_path = path.parent / f"{path.stem}_{counter}{path.suffix}"
        if not new_path.exists():
            return new_path
        counter += 1

def unpack_fhir(source_path: str, dest_path: str) -> list[Path]:
    """
    Extracts archive files recursively and puts ndjson/json in dest_path
    Returns a list of all ndjson/json files found
    """
    source = Path(source_path)
    dest = Path(dest_path)
    dest.mkdir(parents=True, exist_ok=True)

    extracted_files = []

    # Case: source already dir
    if source.is_dir():
        for item in source.rglob('*'):
            if not item.is_file():
                continue
            if item.suffix.lower() in FHIR_EXT:
                # Copy directly to dest and avoid overwriting
                target = dest / item.name
                if target.exists():
                    target = get_unique_path(target)
                shutil.copy2(item, target)
                extracted_files.append(target)
            elif item.suffix.lower() in ARCHIVE_EXT:
                extracted_files.extend(unpack_fhir(str(item), str(dest)))
        return extracted_files

    # Case: source is .zip
    if source.is_file() and source.name.lower().endswith('.zip'):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            with zipfile.ZipFile(source, 'r') as zf:
                zf.extractall(tmp_path)
            extracted_files.extend(unpack_fhir(str(tmp_path), str(dest)))
        return extracted_files

    # Case: source contains .tar extension
    if source.is_file() and any(
        source.name.lower().endswith(ext) for ext in ['.tar', '.tar.gz', '.tgz', '.tar.bz2']
    ):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            with tarfile.open(source, 'r:*') as tf:
                tf.extractall(tmp_path)
            extracted_files.extend(unpack_fhir(str(tmp_path), str(dest)))
        return extracted_files

    # Case: standalone .gz file
    if source.is_file() and source.name.lower().endswith('.gz') and not source.name.lower().endswith('.tar.gz'):
        out_file_name = source.name[:-3]
        out_file_path = dest / out_file_name

        if out_file_path.exists():
            out_file_path = get_unique_path(out_file_path)

        with gzip.open(source, 'rb') as f_in:
            with open(out_file_path, 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)

        if out_file_path.suffix.lower() in ARCHIVE_EXT:
            result = unpack_fhir(str(out_file_path), str(dest))
            out_file_path.unlink(missing_ok=True)
            return result
        if out_file_path.suffix.lower() in FHIR_EXT:
            return [out_file_path]
        return []

    # Base case: already ndjson/json
    if source.is_file() and source.suffix.lower() in FHIR_EXT:
        if source.parent.resolve() == dest.resolve():
            return [source]
        target = dest / source.name
        if target.exists():
            target = get_unique_path(target)
        shutil.copy2(source, target)
        return [target]

    return []