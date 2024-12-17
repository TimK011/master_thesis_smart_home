import subprocess
import sys
import json
import csv
import re
import math

def main():
    if len(sys.argv) < 3:
        print("Usage: python3 all_fields_compact_split.py input.pcap output_base.csv")
        sys.exit(1)

    input_pcap = sys.argv[1]
    output_base = sys.argv[2]

    # Schritt 1: Alle Daten aus tshark als JSON holen
    tshark_cmd = [
        "tshark",
        "-r", input_pcap,
        "-T", "json"
    ]

    print("Führe tshark aus...")
    result = subprocess.run(tshark_cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print("Fehler beim Ausführen von tshark:", result.stderr)
        sys.exit(1)

    try:
        frames = json.loads(result.stdout)
    except json.JSONDecodeError as e:
        print("Fehler beim Parsen der JSON-Ausgabe von tshark:", e)
        sys.exit(1)

    print(f"Anzahl der Frames geladen: {len(frames)}")

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

    all_fields = sorted(all_fields)
    print(f"Anzahl gesammelter Felder: {len(all_fields)}")

    # Felder in Kurzform (f1, f2, f3, ...)
    field_map = {field: f"f{i+1}" for i, field in enumerate(all_fields)}
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
    for idx, frame_data in enumerate(frames, 1):
        layers = frame_data.get('_source', {}).get('layers', {})
        val_dict = extract_values(layers)
        # Erzeuge eine Zeile in der Reihenfolge von all_fields
        row = [val_dict.get(f, "") for f in all_fields]
        rows.append(row)
        if idx % 10000 == 0:
            print(f"{idx} Zeilen verarbeitet...")

    print("Alle Zeilen extrahiert.")

    # Entfernen von Spalten, die über alle Zeilen hinweg leer sind
    num_fields = len(all_fields)
    remove_indices = []
    for i in range(num_fields):
        if all(r[i] == "" for r in rows):
            remove_indices.append(i)

    if remove_indices:
        print(f"Entferne {len(remove_indices)} komplett leere Spalten.")
    else:
        print("Keine komplett leeren Spalten gefunden.")

    filtered_all_fields = [all_fields[i] for i in range(num_fields) if i not in remove_indices]
    filtered_fields_final = [field_map[f] for f in filtered_all_fields]
    filtered_rows = [[r[i] for i in range(num_fields) if i not in remove_indices] for r in rows]

    print(f"Anzahl verbleibender Felder nach Entfernung komplett leerer Spalten: {len(filtered_all_fields)}")

    # Zusätzliche Filterung: Entfernen von Spalten mit hoher Leerquote
    # Setze hier den Schwellenwert, z.B. 90% leer
    max_empty_ratio = 0.9
    final_remove_indices = []
    for i, field in enumerate(filtered_all_fields):
        empty_count = sum(1 for row in filtered_rows if row[i] == "")
        if empty_count / len(filtered_rows) > max_empty_ratio:
            final_remove_indices.append(i)
            if (i + 1) % 100 == 0:
                print(f"Überprüfe Spalte {i+1}/{len(filtered_all_fields)}: {field} - {empty_count} leere Zellen")

    if final_remove_indices:
        print(f"Entferne {len(final_remove_indices)} Spalten mit > {max_empty_ratio*100}% leeren Zellen.")
    else:
        print("Keine Spalten mit hoher Leerquote gefunden.")

    final_filtered_all_fields = [filtered_all_fields[i] for i in range(len(filtered_all_fields)) if i not in final_remove_indices]
    final_filtered_fields_final = [filtered_fields_final[i] for i in range(len(filtered_fields_final)) if i not in final_remove_indices]
    final_filtered_rows = [[row[i] for i in range(len(filtered_all_fields)) if i not in final_remove_indices] for row in filtered_rows]

    print(f"Anzahl verbleibender Felder nach zusätzlicher Filterung: {len(final_filtered_all_fields)}")

    # Einzeiliges Wörterbuch erstellen
    dictionary_pairs = [f"{short}={original}" for original, short in zip(final_filtered_all_fields, final_filtered_fields_final)]
    dictionary_line = "# DICTIONARY: " + ",".join(dictionary_pairs)

    # Dictionary einmalig ausgeben
    print("Dictionary:")
    print(dictionary_line)

    # Anzahl der Ausgabedateien
    num_files = 5
    total_rows = len(final_filtered_rows)
    rows_per_file = math.ceil(total_rows / num_files)
    print(f"Gesamtanzahl der Zeilen: {total_rows}")
    print(f"Zeilen pro Datei: {rows_per_file}")

    for i in range(num_files):
        start_index = i * rows_per_file
        end_index = start_index + rows_per_file
        chunk_rows = final_filtered_rows[start_index:end_index]

        output_csv = f"{output_base.rstrip('.csv')}_{i+1}.csv"

        with open(output_csv, "w", newline="", encoding="utf-8") as out_f:
            # Wörterbuch in einer Zeile, dann Leerzeile
            out_f.write(dictionary_line + "\n\n")
            writer = csv.writer(out_f)
            writer.writerow(final_filtered_fields_final)
            writer.writerows(chunk_rows)

        print(f"Teil {i+1} geschrieben: {output_csv} ({len(chunk_rows)} Zeilen)")

    print("Konvertierung abgeschlossen.")

if __name__ == "__main__":
    main()
