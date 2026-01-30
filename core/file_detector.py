import os

def detect_file_type(file_path: str) -> str:
    ext = os.path.splitext(file_path)[1].lower()

    if ext in [".csv"]:
        return "csv"
    elif ext in [".xls", ".xlsx"]:
        return "excel"
    elif ext in [".json"]:
        return "json"
    elif ext in [".txt"]:
        return "text"
    else:
        raise ValueError("Unsupported file format")