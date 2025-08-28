This Python script is designed to detect and redact Personally Identifiable Information (PII) from a dataset. It reads data from a source CSV file where one column contains a JSON string, processes each JSON record to find and mask PII, and then writes the results to a new output CSV file.

Key Features 

    PII Detection: Identifies two categories of PII:

        Standalone PII: Data that is sensitive on its own (e.g., phone number, Aadhar number).

        Combinatorial PII: Data that becomes sensitive when combined with other pieces of information (e.g., a name found with an IP address).

    Pattern Matching: Uses regular expressions (regex) to validate the format of standalone PII like phone numbers, passports, and Aadhar numbers.

    Custom Redaction: Applies specific, rule-based redaction for different PII types to preserve some context while masking sensitive parts (e.g., XXXXXXXX1234 for Aadhar).

    Robust Processing: Handles potential errors gracefully, such as missing files or malformed JSON data within the CSV.

    CSV I/O: Reads from and writes to CSV files, making it suitable for common data processing workflows.

How It Works 

The script's logic flows through these main steps:

    Initialization: It defines the types of PII to look for, splits them into STANDALONE and COMBINATORIAL categories, and sets up regex patterns for validation.

    File Handling: The main function opens the input CSV for reading and the output CSV for writing. It prepares the output file with a header row.

    Row Iteration: It reads the input CSV row by row. For each row, it parses the data_json column from a string into a Python dictionary.

    PII Processing (process_record): This is the core function.

        It first scans the dictionary for standalone PII keys. If a key exists and its value matches the corresponding regex pattern, the entire record is flagged as containing PII.

        Next, it checks for combinatorial PII keys. It counts how many of these keys are present in the dictionary. If two or more are found, the record is also flagged as PII. This prevents single, non-sensitive items like a first name from being redacted on their own.

        If the record is flagged as PII, the script redacts the identified sensitive values using a mapping of keys to specific redaction functions.

    Writing Output: The main function takes the processed (and possibly redacted) dictionary, converts it back into a JSON string, and writes a new row to the output CSV containing the record ID, the redacted JSON, and a boolean flag (is_pii) indicating if PII was found.

Code Breakdown

Global Constants and Configuration

These dictionaries and lists at the top of the file configure the script's behavior.

    REGEX_PATTERNS: A dictionary holding compiled regular expression objects. Each regex is used to validate the format of a specific PII type (e.g., ensuring a phone number is exactly 10 digits).

    STANDALONE_PII_KEYS: A list of keys that are considered PII by themselves if their value is valid.

    COMBINATORIAL_PII_KEYS: A list of keys that are only considered PII if at least two of them appear together in a single record.

    REDACTION_MAPPING: A dictionary that maps PII keys to their specific redaction functions. This allows for flexible and custom masking rules.

Redaction Functions

These are small, single-purpose functions that define how to mask a specific type of PII.

    redact_phone(phone: str): Masks the middle 6 digits of a 10-digit phone number (e.g., 98XXXXXX45).

    redact_aadhar(aadhar: str): Masks the first 8 digits of a 12-digit Aadhar number (e.g., XXXXXXXX4321).

    redact_passport(passport: str): Masks the middle 5 characters of a passport number (e.g., PXXXXX78).

    redact_email(email: str): Masks the middle characters of the username part of an email (e.g., j*******n@example.com).

    redact_name(name: str): Masks all but the first letter of each part of a name (e.g., J*** D**).

    redact_generic(key_name: str): A fallback function that replaces the value with a generic placeholder like [REDACTED_ADDRESS].

Core Logic Function

process_record(data: Dict[str, Any]) -> Tuple[Dict[str, Any], bool]

This is the central function where detection and redaction occur.

    Parameters: It takes a single dictionary (data) representing one record.

    Logic:

        It creates a copy of the data to avoid modifying the original.

        It uses a set (pii_keys_to_redact) to collect all keys that need redaction.

        It checks for standalone PII using STANDALONE_PII_KEYS and REGEX_PATTERNS.

        It checks for combinatorial PII by counting occurrences of keys from COMBINATORIAL_PII_KEYS. It includes simple filters to avoid flagging single names or short addresses.

        If the is_pii flag is set to True, it iterates through the collected keys and applies the appropriate redaction function looked up from REDACTION_MAPPING.

    Returns: It returns a tuple containing the modified (redacted) dictionary and the boolean is_pii flag.

Main Execution Block

main(input_file: str, output_file: str)

This function orchestrates the entire process of reading, processing, and writing the files. The if __name__ == "__main__": block at the end calls this main function with predefined input and output filenames, making the script directly executable.

Usage 

To use the script:

    Make sure you have a Python environment installed. The script uses only standard libraries, so no special installations are needed.

    Place the script in the same directory as your input CSV file, iscp_pii_dataset_-_Sheet1.csv.

    Run the script from your terminal:
    python3 Soc.py

The script will process the input file and generate a new file named redacted_output.csv in the same directory. This file will contain the original record_id, the potentially redacted JSON data, and the is_pii flag for each record.
