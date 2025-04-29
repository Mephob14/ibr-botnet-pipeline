# This script processes PCAP files located in subdirectories of a given directory.
# It performs the following steps:
# 1. Filters the PCAP file for traffic on commonly targeted ports (22, 23, 80, and 443).
# 2. Extracts payload data from the filtered PCAP file.
# 3. Decodes the extracted payloads and enriches the data with GeoIP information for the source IP addresses, including ASN, country, city, and geographical coordinates.
# 4. The script outputs filtered PCAPs, extracted payloads, and enriched CSV files containing the decoded payload data and GeoIP details.
# 
# Requirements:
# - `tshark` (a command-line version of Wireshark) to filter and extract data from the PCAP files.
# - `geoip2` library to enrich IP addresses with GeoIP information.
# - The GeoLite2 ASN and City databases for GeoIP enrichment.
#
# The script handles files sequentially and only processes each file once by checking if the output files already exist.
# It operates on a directory structure where each subdirectory contains a single PCAP file.

# This script was written by Mads Folkestad

import os
import subprocess
import pandas as pd
import geoip2.database

# Paths to GeoIP databases
geoip_asn_db = '/mnt/d/ibr-data/geoip-databases/GeoLite2-ASN/GeoLite2-ASN.mmdb'
geoip_city_db = '/mnt/d/ibr-data/geoip-databases/GeoLite2-City/GeoLite2-City.mmdb'

# Initialize GeoIP readers
asn_reader = geoip2.database.Reader(geoip_asn_db)
city_reader = geoip2.database.Reader(geoip_city_db)

# Function to enrich source IPs with GeoIP data
def enrich_ip(ip):
    try:
        # ASN Info
        asn_response = asn_reader.asn(ip)
        asn = asn_response.autonomous_system_organization

        # City and Country Info
        city_response = city_reader.city(ip)
        country = city_response.country.name
        city = city_response.city.name
        latitude = city_response.location.latitude
        longitude = city_response.location.longitude

        return pd.Series([asn, country, city, latitude, longitude])
    except:
        return pd.Series([None, None, None, None, None])

# Directory containing folders with PCAP files
input_dir = "/mnt/d/Ibr-data/e2/"

# Process PCAPs sequentially, one step at a time
for root, dirs, _ in os.walk(input_dir):
    for subdir in dirs:
        subdir_path = os.path.join(root, subdir)

        # Find the PCAP file in the folder
        pcap_files = [f for f in os.listdir(subdir_path) if f.endswith(".pcap")]
        if len(pcap_files) != 1:
            print(f"Skipping {subdir_path}: Expected 1 PCAP file, found {len(pcap_files)}")
            continue

        pcap_path = os.path.join(subdir_path, pcap_files[0])
        base_name = os.path.splitext(pcap_files[0])[0]

        print(f"Processing {pcap_files[0]} in {subdir_path}...")

        # Step 1: Filter PCAP for ports 22, 23, 80, and 443
        filtered_pcap = os.path.join(subdir_path, f"{base_name}_filtered.pcap")
        if not os.path.exists(filtered_pcap):  # Skip if already filtered
            print("Filtering PCAP...")
            filter_command = [
                "tshark", "-r", pcap_path,
                "-Y", "tcp.port == 22 || tcp.port == 23 || tcp.port == 80 || tcp.port == 443",
                "-w", filtered_pcap
            ]
            subprocess.run(filter_command)
        else:
            print("Filtered PCAP already exists, skipping filtering.")

        # Step 2: Extract Payloads
        extracted_payloads = os.path.join(subdir_path, f"{base_name}_extracted_payloads.csv")
        if not os.path.exists(extracted_payloads):  # Skip if already extracted
            print("Extracting payloads...")
            extract_command = [
                "tshark", "-r", filtered_pcap,
                "-T", "fields",
                "-e", "frame.time",
                "-e", "ip.src",
                "-e", "ip.dst",
                "-e", "tcp.dstport",
                "-e", "tcp.payload",
                "-Y", "tcp.payload"
            ]
            with open(extracted_payloads, "w") as outfile:
                subprocess.run(extract_command, stdout=outfile)
        else:
            print("Payloads already extracted, skipping extraction.")

        # Step 3: Decode Payloads
        enriched_output = os.path.join(subdir_path, f"{base_name}_enriched.csv")
        if not os.path.exists(enriched_output):  # Skip if already enriched
            print("Decoding and enriching payloads...")
            # Read extracted payloads in chunks to avoid memory issues
            chunk_size = 10000
            chunks = pd.read_csv(extracted_payloads, delimiter="\t", names=["timestamp", "src_ip", "dst_ip", "dst_port", "payload"], chunksize=chunk_size)

            # Process each chunk
            for i, chunk in enumerate(chunks):
                chunk["decoded_payload"] = chunk["payload"].apply(
                    lambda x: bytes.fromhex(x).decode('utf-8', errors='ignore') if pd.notnull(x) else None
                )
                chunk[['asn', 'country', 'city', 'latitude', 'longitude']] = chunk['src_ip'].apply(enrich_ip)
                # Append to the final enriched output
                chunk.to_csv(enriched_output, mode='a', index=False, header=(i == 0))
        else:
            print("Enriched file already exists, skipping enrichment.")

        print(f"Finished processing {pcap_files[0]}.")
