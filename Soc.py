import csv
import json
import re
import sys
from typing import Dict, Any, Tuple

REGEX_PATTERNS = {
    "phone": re.compile(r"^\d{10}$"),
    "aadhar": re.compile(r"^\d{12}$"),
    "passport": re.compile(r"^[A-Z][0-9]{7}$"),
    "upi_id": re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+$"),
    "email": re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"),
    "ip_address": re.compile(r"^(?:\d{1,3}\.){3}\d{1,3}$"),
    "name": re.compile(r"^[A-Z][a-z]+(?:\s[A-Z][a-z]+)+$")
}

STANDALONE_PII_KEYS = {"phone", "aadhar", "passport", "upi_id"}
COMBINATORIAL_PII_KEYS = {"name", "email", "address", "ip_address", "device_id"}

def redact_phone(phone: str) -> str:
    return f"{phone[:2]}XXXXXX{phone[-2:]}"

def redact_aadhar(aadhar: str) -> str:
    return f"XXXXXXXX{aadhar[-4:]}"

def redact_passport(passport: str) -> str:
    return f"{passport[0]}XXXXX{passport[-2:]}"

def redact_email(email: str) -> str:
    try:
        user, domain = email.split("@", 1)
        if len(user) > 2:
            return f"{user[0]}{'*' * (len(user) - 2)}{user[-1]}@{domain}"
        return f"{user[0]}*@{domain}"
    except ValueError:
        return "[REDACTED_EMAIL]"

def redact_name(name: str) -> str:
    return " ".join([f"{p[0]}{'*' * (len(p) - 1)}" for p in name.split()])

def redact_generic(key: str) -> str:
    return f"[REDACTED_{key.upper()}]"

REDACTION_MAPPING = {
    "phone": redact_phone,
    "aadhar": redact_aadhar,
    "passport": redact_passport,
    "email": redact_email,
    "name": redact_name,
}

def redact_value(key: str, value: str) -> str:
    redaction_func = REDACTION_MAPPING.get(key, redact_generic)
    return redaction_func(value)

def process_record(data: Dict[str, Any]) -> Tuple[Dict[str, Any], bool]:
    is_pii = False
    redacted_data = data.copy()
    pii_keys_to_redact = set()
    for key, value in data.items():
        if key in STANDALONE_PII_KEYS and isinstance(value, str):
            if REGEX_PATTERNS.get(key) and REGEX_PATTERNS[key].fullmatch(value):
                is_pii = True
                pii_keys_to_redact.add(key)
    found_combinatorial = []
    for key, value in data.items():
        if key in COMBINATORIAL_PII_KEYS and isinstance(value, str):
            if key == "name" and " " not in value:
                continue
            if key == "address" and len(value.split()) < 3:
                continue
            found_combinatorial.append(key)
    if len(found_combinatorial) >= 2:
        is_pii = True
        pii_keys_to_redact.update(found_combinatorial)
    for key in pii_keys_to_redact:
        if redacted_data.get(key) is not None:
            redacted_data[key] = redact_value(key, str(redacted_data[key]))
    return redacted_data, is_pii

def main(input_file: str, output_file: str):
    try:
        with open(input_file, mode="r", encoding="utf-8") as infile, \
             open(output_file, mode="w", encoding="utf-8", newline="") as outfile:
            reader = csv.DictReader(infile)
            writer = csv.writer(outfile)
            if "record_id" not in reader.fieldnames or "data_json" not in reader.fieldnames:
                sys.exit(1)
            writer.writerow(["record_id", "redacted_data_json", "is_pii"])
            for row in reader:
                record_id = row.get("record_id", "")
                try:
                    data_dict = json.loads(row.get("data_json", "{}"))
                except json.JSONDecodeError:
                    continue
                redacted_data, is_pii = process_record(data_dict)
                writer.writerow([record_id, json.dumps(redacted_data), is_pii])
    except FileNotFoundError:
        sys.exit(1)
    except Exception:
        sys.exit(1)

if __name__ == "__main__":
    input_csv_file = "iscp_pii_dataset_-_Sheet1.csv"
    output_csv_file = "redacted_output.csv"
    main(input_csv_file, output_csv_file)
