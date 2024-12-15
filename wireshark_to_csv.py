import subprocess
import sys
import json
import csv
import re
import math

if len(sys.argv) < 3:
    print("Usage: python3 wireshark_to_csv.py input.pcap output_base.csv")
    sys.exit(1)

input_pcap = sys.argv[1]
output_base = sys.argv[2]

# Schritt 1: Alle Daten aus tshark als JSON holen
tshark_cmd = [
    "tshark",
    "-r", input_pcap,
    "-T", "json"
]

result = subprocess.run(tshark_cmd, capture_output=True, text=True)
if result.returncode != 0:
    print("Error running tshark:", result.stderr)
    sys.exit(1)

frames = json.loads(result.stdout)

def collect_fields(d, prefix=""):
    """Rekursiv alle Keys sammeln."""
    all_fields = set()
    if isinstance(d, dict):
        for k, v in d.items():
            full_key = prefix + k if prefix else k
            # Nur alphanumerische Zeichen und Unterstrich verwenden
            safe_key = re.sub(r'[^a-zA-Z0-9_]', '_', full_key)
            all_fields.add(safe_key)
            all_fields.update(collect_fields(v, safe_key + "."))
    elif isinstance(d, list):
        for item in d:
            all_fields.update(collect_fields(item, prefix))
    return all_fields

# Alle Felder sammeln
all_fields = set()
for frame_data in frames:
    layers = frame_data.get('_source', {}).get('layers', {})
    all_fields.update(collect_fields(layers))

all_fields = list(all_fields)
all_fields.sort()

# Felder in Kurzform (f1, f2, f3, ...)
field_map = {all_fields[i]: f"f{i+1}" for i in range(len(all_fields))}
fields_final = [field_map[f] for f in all_fields]

def extract_values(d, prefix="", val_dict=None):
    if val_dict is None:
        val_dict = {}
    if isinstance(d, dict):
        for k, v in d.items():
            full_key = prefix + k if prefix else k
            safe_key = re.sub(r'[^a-zA-Z0-9_]', '_', full_key)
            if isinstance(v, (str, int, float, bool)) or v is None:
                val_dict[safe_key] = str(v) if v is not None else ""
            else:
                extract_values(v, safe_key + ".", val_dict)
    elif isinstance(d, list):
        # Prüfen, ob komplexe Strukturen vorliegen
        has_complex = any(isinstance(x, (dict, list)) for x in d)
        if has_complex:
            val_dict[prefix[:-1]] = json.dumps(d)
        else:
            val_dict[prefix[:-1]] = ";".join(map(str, d))
    return val_dict

# Alle Zeilen extrahieren
rows = []
for frame_data in frames:
    layers = frame_data.get('_source', {}).get('layers', {})
    val_dict = extract_values(layers)
    # Erzeuge eine Zeile in der Reihenfolge von all_fields
    row = [val_dict.get(f, "") for f in all_fields]
    rows.append(row)

# Entfernen von Spalten, die über alle Zeilen hinweg leer sind, um Tokens zu sparen
# Herausfinden, welche Spalten leer sind
num_fields = len(all_fields)
remove_indices = []
for i in range(num_fields):
    # Prüfen, ob die gesamte Spalte leer ist
    if all(r[i] == "" for r in rows):
        remove_indices.append(i)

# Neue Feld- und Datenlisten ohne leere Spalten
filtered_all_fields = [all_fields[i] for i in range(num_fields) if i not in remove_indices]
filtered_fields_final = [field_map[f] for f in filtered_all_fields]
filtered_rows = [[r[i] for i in range(num_fields) if i not in remove_indices] for r in rows]

# Einzeiliges Wörterbuch erstellen:
# Beispiel: "# DICTIONARY: f1=ip_src,f2=ip_dst,f3=http_method"
dictionary_pairs = []
for original, short in zip(filtered_all_fields, filtered_fields_final):
    # Optional: Originalfeldnamen noch kürzer in der Doku halten,
    # hier belassen wir es bei der reinen Zuordnung
    dictionary_pairs.append(f"{short}={original}")

dictionary_line = "# DICTIONARY: " + ",".join(dictionary_pairs)

# Dictionary einmalig ausgeben
print(dictionary_line)

# Anzahl der Ausgabedateien
num_files = 5
total_rows = len(filtered_rows)
rows_per_file = math.ceil(total_rows / num_files)

for i in range(num_files):
    start_index = i * rows_per_file
    end_index = start_index + rows_per_file
    chunk_rows = filtered_rows[start_index:end_index]

    output_csv = f"{output_base.rstrip('.csv')}_{i+1}.csv"

    with open(output_csv, "w", newline="", encoding="utf-8") as out_f:
        # Wörterbuch in einer Zeile, dann Leerzeile
        out_f.write(dictionary_line + "\n\n")
        writer = csv.writer(out_f)
        writer.writerow(filtered_fields_final)
        for row in chunk_rows:
            writer.writerow(row)

    print(f"Teil {i+1} geschrieben: {output_csv}")

print("Konvertierung abgeschlossen.")
