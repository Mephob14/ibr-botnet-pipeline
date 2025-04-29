# This script processes the enriched PCAP data to extract and analyze command-and-control (C2) servers and payload names.
# It iterates through folders containing enriched CSV files, extracts C2 server IPs and payload names using regex, 
# and filters out irrelevant data. The script also counts occurrences of C2 IPs and payloads across the entire dataset.
# Key outputs include:
# - A CSV with filtered C2 server and payload data for each region
# - A global list of unique C2 servers with count and geographic information
# - A global count of payload occurrences
# - A GeoJSON file representing the geographic locations of the C2 servers

# Required libraries:
# - os: for directory and file management
# - pandas: for handling large CSV files in chunks and data manipulation
# - re: for regex operations to extract C2 server information
# - json: for generating the GeoJSON file

# Script is written by Mads Folkestad




import os
import pandas as pd
import re
import json

# Set data directories
BASE_DIR = "/mnt/d/Ibr-data/e2"
GLOBAL_OUTPUT_DIR = "/mnt/d/Ibr-data/global_outputs"

# Ensure the global output directory exists
os.makedirs(GLOBAL_OUTPUT_DIR, exist_ok=True)

# Regular expression for extracting C2 servers & filenames
c2_pattern = re.compile(
    r"(?:https?|ftp|tftp)://([\w\.-]+)(?::\d+)?/([\w\.-]+)?", re.IGNORECASE
)

# Valid file extensions (executable/script-related)
valid_extensions = {".sh", ".bin", ".exe", ".dat", ".m", ".txt", ".old", ".env", ".php", ".json"}

def extract_c2_and_payloads(payload):
    try:
        if not isinstance(payload, str) or payload.strip() == "":
            return "MISSING_C2", "MISSING_PAYLOAD"

        matches = c2_pattern.findall(payload)
        extracted_c2 = set()
        extracted_payloads = set()

        for match in matches:
            c2_ip = match[0]
            file_name = match[1] if match[1] else "UNKNOWN"

            if any(file_name.endswith(ext) for ext in valid_extensions):
                extracted_c2.add(c2_ip)
                extracted_payloads.add(file_name)

        if extracted_c2 and extracted_payloads:
            return ";".join(extracted_c2), ";".join(extracted_payloads)

        return "MISSING_C2", "MISSING_PAYLOAD"

    except Exception as e:
        print(f" Error processing payload: {payload[:50]}... | {e}")
        return "MISSING_C2", "MISSING_PAYLOAD"

# Initialize global data storage
global_c2_set = {}  # now with count
global_payload_counts = {}

# Process each region's folder
for region_folder in sorted(os.listdir(BASE_DIR)):
    folder_path = os.path.join(BASE_DIR, region_folder)

    if not os.path.isdir(folder_path):
        continue

    enriched_file = None
    for file in os.listdir(folder_path):
        if file.endswith("_enriched.csv"):
            enriched_file = os.path.join(folder_path, file)
            break

    if not enriched_file:
        print(f" Skipping {folder_path}: Expected _enriched.csv file, found none")
        continue

    region = file.replace("_enriched.csv", "")
    print(f" Processing folder: {region_folder} ({region})...")

    filtered_output_path = os.path.join(folder_path, f"{region}_filtered_c2_payload.csv")
    chunk_size = 50000
    filtered_chunks = []

    for chunk in pd.read_csv(enriched_file, chunksize=chunk_size, low_memory=False):
        chunk["c2_servers"], chunk["payload_names"] = zip(*chunk["decoded_payload"].apply(extract_c2_and_payloads))
        filtered_chunk = chunk[(chunk["c2_servers"] != "MISSING_C2") & (chunk["payload_names"] != "MISSING_PAYLOAD")]
        filtered_chunks.append(filtered_chunk)

        for _, row in filtered_chunk.iterrows():
            c2_ips = row["c2_servers"].split(";")
            for ip in c2_ips:
                if ip not in global_c2_set:
                    global_c2_set[ip] = {
                        "count": 1,
                        "country": row["country"],
                        "city": row["city"],
                        "latitude": row["latitude"],
                        "longitude": row["longitude"]
                    }
                else:
                    global_c2_set[ip]["count"] += 1

        for payload in filtered_chunk["payload_names"].str.split(";").explode().dropna():
            global_payload_counts[payload] = global_payload_counts.get(payload, 0) + 1

    if filtered_chunks:
        final_df = pd.concat(filtered_chunks)
        final_df.to_csv(filtered_output_path, index=False)
        print(f" Saved: {filtered_output_path}")

# Save Global C2 IPs for Mapping
c2_df = pd.DataFrame([
    {
        "c2_server": ip,
        "count": data["count"],
        "country": data["country"],
        "city": data["city"],
        "latitude": data["latitude"],
        "longitude": data["longitude"]
    }
    for ip, data in global_c2_set.items()
])
c2_df.sort_values(by="count", ascending=False, inplace=True)  # This sorts by activity
c2_mapping_output = os.path.join(GLOBAL_OUTPUT_DIR, "unique_c2_servers.csv")
c2_df.to_csv(c2_mapping_output, index=False)
print(f" C2 Mapping saved: {c2_mapping_output}")

# Save Global Payload Counts 
payload_count_output = os.path.join(GLOBAL_OUTPUT_DIR, "payload_counts.csv")
pd.DataFrame.from_dict(global_payload_counts, orient="index", columns=["count"]).reset_index().rename(columns={"index": "payload_name"}).to_csv(payload_count_output, index=False)
print(f" Payload Count saved: {payload_count_output}")


# Save GeoJSON map
geojson_data = {
    "type": "FeatureCollection",
    "features": []
}

for ip, data in global_c2_set.items():
    try:
        feature = {
            "type": "Feature",
            "properties": {
                "ip": ip,
                "count": data["count"],
                "country": data.get("country", "Unknown"),
                "city": data.get("city", "Unknown"),
            },
            "geometry": {
                "type": "Point",
                "coordinates": [float(data["longitude"]), float(data["latitude"])]
            }
        }
        geojson_data["features"].append(feature)
    except Exception as e:
        print(f" Skipping {ip}: Invalid coordinates. {e}")

geojson_output_path = os.path.join(GLOBAL_OUTPUT_DIR, "c2_servers_map.geojson")
with open(geojson_output_path, "w") as geojson_file:
    json.dump(geojson_data, geojson_file, indent=4)
print(f" GeoJSON map saved: {geojson_output_path}")

print(" Processing complete!")
