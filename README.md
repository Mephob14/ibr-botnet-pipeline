# IBR Botnet Analysis Pipeline

This repository contains a modular pipeline developed to extract, enrich, and analyze Internet Background Radiation (IBR) data for identifying botnet infrastructure and payload behavior. The pipeline was designed as part of a bachelor's thesis and specifically focuses on botnets such as Mirai, Mozi, and Sora.

## 🧭 Overview

The pipeline consists of four scripts, which must be run in sequence. Each script expects a specific input/output directory structure and builds upon the results of the previous stage.

---

## 🧩 Script 1: `pcap_filter_and_geoenrich_MAIN.py`

**Purpose**:  
Filters raw PCAP traffic and enriches source IPs with geolocation and ASN metadata.

**Steps performed**:
- Filters TCP traffic for ports 22, 23, 80, and 443.
- Extracts payloads using `tshark`.
- Decodes TCP payloads from hex to readable form.
- Enriches source IPs with country, city, latitude, longitude, and ASN using GeoLite2 databases.

**Requirements**:
- `tshark`
- `geoip2`
- MaxMind GeoLite2 City and ASN `.mmdb` databases.

---

## 🧩 Script 2: `process_enriched_data_extract_c2_and_payloads_MAIN.py`

**Purpose**:  
Parses decoded payloads to extract C2 servers and malware filenames using regex.

**Steps performed**:
- Identifies C2 URLs from payload strings.
- Extracts payload filenames and filters by known extensions.
- Creates global output files:
  - `unique_c2_servers.csv` with geographic data.
  - `payload_counts.csv` with frequency of filenames.
  - GeoJSON map of all observed C2 locations.

---

## 🧩 Script 3: `enrich_unique_ipinfo_MAIN.py`

**Purpose**:  
Enriches each unique C2 IP address using IPinfo’s public API.

**Steps performed**:
- Queries ASN, geolocation, and hosting data.
- Outputs enriched CSV with extra metadata (e.g., organization, type, abuse contacts).

**Requirements**:
- Free IPinfo API key.
- Creates `enriched_c2_servers.csv`.

---

## 🧩 Script 4: `visualize_c2_aws_connections_MAIN.py`

**Purpose**:  
Generates visual outputs to map botnet targeting behavior against AWS regions.

**Steps performed**:
- Loads AWS sensor regions and enriched C2 data.
- Builds a matrix of connections between sensors and observed botnet infrastructure.
- Saves interactive or static graphs for use in reporting.

---

## 📁 Directory Structure (Example)
/ibr-data/ │ ├── e2/ │ ├── us-east-1/ │ │ └── data.pcap │ ├── eu-west-1/ │ │ └── data.pcap │ └── ... ├── geoip-databases/ │ ├── GeoLite2-ASN.mmdb │ └── GeoLite2-City.mmdb └── global_outputs/ ├── unique_c2_servers.csv ├── payload_counts.csv └── c2_servers_map.geojson



## 📜 License

This repository is released under the MIT License. Attribution appreciated.  
All code written by **Mads Folkestad** for academic use.

---

## 📚 Citation

If you use this pipeline in research or education, please cite:

> Mads Folkestad, *Cloud-Based Detection of Botnet Activity: A Script-Based Pipeline for Analyzing Internet Background Radiation*, Noroff University College, 2025.
