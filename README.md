# IBR Botnet Analysis Pipeline

This repository contains a modular pipeline developed to extract, enrich, and analyze Internet Background Radiation (IBR) data for identifying botnet infrastructure and payload behavior. The pipeline was designed as part of a bachelor's thesis and specifically focuses on botnets such as Mirai, Mozi, and Sora.

## 🧭 Overview

The pipeline consists of four scripts, which must be run in sequence. Each script expects a specific input/output directory structure and builds upon the results of the previous stage.

---

🧩 Script 1: pcap_filter_and_geoenrich_MAIN.py

This script scans through folders with PCAP files and performs the following steps to extract relevant traffic and enrich it with metadata:

Filters for TCP traffic on ports 22, 23, 80, and 443, which are commonly used in botnet traffic.

Extracts payloads from this filtered traffic.

Decodes the payloads and looks up GeoIP details (such as country, ASN, and coordinates) for each source IP.

Saves the filtered PCAPs, extracted payloads, and enriched CSVs.

Dependencies:

tshark – to filter and extract from the PCAPs.

Python's geoip2 – to look up IP info using the GeoLite2 database.

The script skips already-processed files and expects one PCAP per folder.


🧩 Script 2: process_enriched_data_extract_c2_and_payloads_MAIN.py

This script processes enriched payload files to extract command-and-control (C2) IPs and downloaded payload filenames:

Loads enriched CSVs from each region folder.

Uses regular expressions to extract C2 IPs and filenames from payload content.

Filters out rows that lack valid C2 or payload data.

Compiles lists of observed C2s and payloads, and saves the results as CSV and GeoJSON.

Dependencies:

os – for file and directory navigation.

pandas – to process large CSVs in chunks.

re – to match C2 and filename patterns.

json – to save output maps in GeoJSON format.

Outputs include filtered data per region, a full list of C2s with metadata, and a map of server locations.


🧩 Script 3: enrich_unique_ipinfo_MAIN.py

This script enriches a list of unique command-and-control (C2) server IPs using the IPinfo API. It collects metadata such as ASN, geolocation, hosting provider, and whether the IP belongs to a VPN or hosting service. The enriched data supports infrastructure mapping and geospatial analysis.

Input: CSV file with unique IP addresses.

Output: CSV file with enriched metadata.

Handles failed lookups gracefully and retries when needed.

Dependencies:

pandas – for reading and writing CSV data.

requests – for API calls to IPinfo.

API key – required to authenticate with the IPinfo API.


🧩 Script 4: visualize_c2_aws_connections_MAIN.py
This script reads C2 server data from each AWS region and creates GeoJSON files to visualize connections between botnet infrastructure and AWS sensors. It works by:

Iterating through folders with filtered payload data.

Extracting C2 server IPs and their coordinates.

Linking each C2 to the AWS region that captured its traffic.

Saving results as GeoJSON for use in visualization tools like QGIS.

Dependencies:

pandas – for handling CSV data.

json – to generate GeoJSON output.

os – for navigating folders.

Outputs:

aws-nodes.geojson – geographic points for AWS regions.

c2-to-aws-connections.geojson – lines connecting C2 servers to AWS sensors.



## 📁 Directory Structure (Example)
/ibr-data/ │ ├── e2/ │ ├── us-east-1/ │ │ └── data.pcap │ ├── eu-west-1/ │ │ └── data.pcap │ └── ... ├── geoip-databases/ │ ├── GeoLite2-ASN.mmdb │ └── GeoLite2-City.mmdb └── global_outputs/ ├── unique_c2_servers.csv ├── payload_counts.csv └── c2_servers_map.geojson



## 📜 License

This repository is released under the MIT License. Attribution appreciated.  
All code written by **Mads Folkestad** for academic use.

---

## 📚 Citation

If you use this pipeline in research or education, please cite:

> Mads Folkestad, *Cloud-Based Detection of Botnet Activity: A Script-Based Pipeline for Analyzing Internet Background Radiation*, Noroff University College, 2025.
