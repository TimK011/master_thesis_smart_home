import subprocess
import sys
import json
import csv
import re
import math

def main():
    # Check if the correct number of command-line arguments are provided
    if len(sys.argv) < 3:
        print("Usage: python3 wireshark_to_csv.py input.pcap output_base.csv")
        sys.exit(1)

    # Assign input and output file paths from command-line arguments
    input_pcap = sys.argv[1]
    output_base = sys.argv[2]

    # Step 1: Retrieve all data from TShark in JSON format
    tshark_cmd = [
        tshark_path,  # Use the full path to TShark
        "-r", input_pcap,  # Input pcap file
        "-T", "json"  # Output format set to JSON
    ]

    print("Executing TShark...")
    try:
        # Run the TShark command and capture the output
        result = subprocess.run(tshark_cmd, capture_output=True, text=True, check=True)
    except subprocess.CalledProcessError as e:
        # Handle errors during TShark execution
        print("Error executing TShark:", e.stderr)
        sys.exit(1)

    try:
        # Parse the JSON output from TShark
        frames = json.loads(result.stdout)
    except json.JSONDecodeError as e:
        # Handle JSON parsing errors
        print("Error parsing JSON output from TShark:", e)
        sys.exit(1)

    print(f"Number of frames loaded: {len(frames)}")

    def collect_fields(d, prefix=""):
        """
        Recursively collect all unique keys from a nested dictionary or list.

        Args:
            d (dict or list): The data structure to traverse.
            prefix (str): The prefix for nested keys.

        Returns:
            set: A set of unique, sanitized field names.
        """
        all_fields = set()
        if isinstance(d, dict):
            for k, v in d.items():
                full_key = prefix + k if prefix else k
                # Replace non-alphanumeric characters with underscores
                safe_key = re.sub(r'[^a-zA-Z0-9_]', '_', full_key)
                all_fields.add(safe_key)
                # Recursively collect fields from nested structures
                all_fields.update(collect_fields(v, safe_key + "."))
        elif isinstance(d, list):
            for item in d:
                all_fields.update(collect_fields(item, prefix))
        return all_fields

    # Collect all unique fields from all frames
    all_fields = set()
    for frame_data in frames:
        # Extract the 'layers' section from each frame
        layers = frame_data.get('_source', {}).get('layers', {})
        all_fields.update(collect_fields(layers))

    # Sort the fields for consistent ordering
    all_fields = sorted(all_fields)
    print(f"Number of collected fields: {len(all_fields)}")

    # Create a mapping from original field names to short field names (f1, f2, f3, ...)
    field_map = {field: f"f{i+1}" for i, field in enumerate(all_fields)}
    fields_final = [field_map[f] for f in all_fields]

    def extract_values(d, prefix="", val_dict=None):
        """
        Recursively extract values from a nested dictionary or list and map them to their sanitized keys.

        Args:
            d (dict or list): The data structure to traverse.
            prefix (str): The prefix for nested keys.
            val_dict (dict): The dictionary to store extracted values.

        Returns:
            dict: A dictionary mapping sanitized keys to their corresponding values.
        """
        if val_dict is None:
            val_dict = {}
        if isinstance(d, dict):
            for k, v in d.items():
                full_key = prefix + k if prefix else k
                safe_key = re.sub(r'[^a-zA-Z0-9_]', '_', full_key)
                if isinstance(v, (str, int, float, bool)) or v is None:
                    # Assign string representation of the value or empty string if None
                    val_dict[safe_key] = str(v) if v is not None else ""
                else:
                    # Recursively extract values from nested structures
                    extract_values(v, safe_key + ".", val_dict)
        elif isinstance(d, list):
            # Check if the list contains complex structures (dict or list)
            has_complex = any(isinstance(x, (dict, list)) for x in d)
            if has_complex:
                # Serialize complex structures as JSON strings
                val_dict[prefix[:-1]] = json.dumps(d)
            else:
                # Join simple list items with semicolons
                val_dict[prefix[:-1]] = ";".join(map(str, d))
        return val_dict

    # Extract all rows of data
    rows = []
    for idx, frame_data in enumerate(frames, 1):
        layers = frame_data.get('_source', {}).get('layers', {})
        val_dict = extract_values(layers)
        # Create a row with values ordered according to all_fields
        row = [val_dict.get(f, "") for f in all_fields]
        rows.append(row)
        # Print progress every 10,000 rows
        if idx % 10000 == 0:
            print(f"{idx} rows processed...")

    print("All rows extracted.")

    # Remove columns that are completely empty across all rows to save space
    num_fields = len(all_fields)
    remove_indices = []
    for i in range(num_fields):
        # Check if the entire column is empty
        if all(r[i] == "" for r in rows):
            remove_indices.append(i)

    if remove_indices:
        print(f"Removing {len(remove_indices)} completely empty columns.")
    else:
        print("No completely empty columns found.")

    # Create new lists excluding the empty columns
    filtered_all_fields = [all_fields[i] for i in range(num_fields) if i not in remove_indices]
    filtered_fields_final = [field_map[f] for f in filtered_all_fields]
    filtered_rows = [[r[i] for i in range(num_fields) if i not in remove_indices] for r in rows]

    print(f"Number of remaining fields after removing completely empty columns: {len(filtered_all_fields)}")

    # Additional Filtering: Remove columns with a high ratio of empty cells
    # Set the threshold, e.g., 90% empty
    max_empty_ratio = 0.9
    final_remove_indices = []
    for i, field in enumerate(filtered_all_fields):
        empty_count = sum(1 for row in filtered_rows if row[i] == "")
        if empty_count / len(filtered_rows) > max_empty_ratio:
            final_remove_indices.append(i)
            # Optionally, print progress for large datasets
            if (i + 1) % 100 == 0:
                print(f"Checking column {i+1}/{len(filtered_all_fields)}: {field} - {empty_count} empty cells")

    if final_remove_indices:
        print(f"Removing {len(final_remove_indices)} columns with > {max_empty_ratio*100}% empty cells.")
    else:
        print("No columns with a high ratio of empty cells found.")

    # Create final lists excluding columns with high empty ratios
    final_filtered_all_fields = [filtered_all_fields[i] for i in range(len(filtered_all_fields)) if i not in final_remove_indices]
    final_filtered_fields_final = [filtered_fields_final[i] for i in range(len(filtered_fields_final)) if i not in final_remove_indices]
    final_filtered_rows = [[row[i] for i in range(len(filtered_all_fields)) if i not in final_remove_indices] for row in filtered_rows]

    print(f"Number of remaining fields after additional filtering: {len(final_filtered_all_fields)}")

    # Create a single-line dictionary mapping short field names to original field names
    dictionary_pairs = [f"{short}={original}" for original, short in zip(final_filtered_all_fields, final_filtered_fields_final)]
    dictionary_line = "# DICTIONARY: " + ",".join(dictionary_pairs)

    # Output the dictionary line once
    print("Dictionary:")
    print(dictionary_line)

    # Define the number of output CSV files to create
    num_files = 5
    total_rows = len(final_filtered_rows)
    rows_per_file = math.ceil(total_rows / num_files)
    print(f"Total number of rows: {total_rows}")
    print(f"Rows per file: {rows_per_file}")

    # Split the data into chunks and write each chunk to a separate CSV file
    for i in range(num_files):
        start_index = i * rows_per_file
        end_index = start_index + rows_per_file
        chunk_rows = final_filtered_rows[start_index:end_index]

        # Define the output CSV file name with an index
        output_csv = f"{output_base.rstrip('.csv')}_{i+1}.csv"

        with open(output_csv, "w", newline="", encoding="utf-8") as out_f:
            # Write the dictionary line followed by an empty line
            out_f.write(dictionary_line + "\n\n")
            writer = csv.writer(out_f)
            # Write the header row with short field names
            writer.writerow(final_filtered_fields_final)
            # Write all data rows for this chunk
            writer.writerows(chunk_rows)

        # Print confirmation for each written file
        print(f"Part {i+1} written: {output_csv} ({len(chunk_rows)} rows)")

    print("Conversion completed.")

if __name__ == "__main__":
    main()
