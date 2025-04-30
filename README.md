# IBR Botnet Analysis Pipeline

This repository contains a modular pipeline developed to extract, enrich, and analyze Internet Background Radiation (IBR) data for identifying botnet infrastructure and payload behavior. The pipeline was designed as part of a bachelor's thesis and specifically focuses on botnets such as Mirai, Mozi, and Sora.

## 🧭 Overview

The pipeline consists of four scripts, which must be run in sequence. Each script expects a specific input/output directory structure and builds upon the results of the previous stage.

---

## 🧩 Script 1: `pcap_filter_and_geoenrich_MAIN.py`

This script scans through folders with PCAP files and does a few steps to find relevant traffic and add extra data:

\begin{enumerate}
    \item Filters for TCP traffic on ports 22, 23, 80, and 443, which are often used in botnet traffic.
    \item Pulls out the payloads from this filtered traffic.
    \item Decodes the payloads and looks up GeoIP details (like country, ASN, and coordinates) for each source IP.
    \item It saves out filtered PCAPs, extracted payloads, and enriched CSVs.
\end{enumerate}

\textbf{Dependencies:}
\begin{itemize}
    \item `tshark` – to filter and extract from the PCAPs.
    \item Python's `geoip2` – to look up IP info using the GeoLite2 database.
\end{itemize}

The script skips any files it's already processed and expects one PCAP per folder.

---

## 🧩 Script 2: `process_enriched_data_extract_c2_and_payloads_MAIN.py`

This script takes the enriched payload files and finds command-and-control (C2) IPs and filenames for downloaded payloads:

\begin{enumerate}
    \item Loads enriched CSVs from each region folder.
    \item Uses regular expressions to pull out C2 IPs and filenames from payload data.
    \item Removes any rows that didn’t contain valid C2 or payload entries.
    \item Puts together lists of all seen C2s and payloads and saves the results in CSV and GeoJSON formats.
\end{enumerate}

\textbf{Dependencies:}
\begin{itemize}
    \item `os` – to move through folders and find files.
    \item `pandas` – for processing large CSVs in chunks.
    \item `re` – to match C2 and filename patterns.
    \item `json` – to save map files in GeoJSON.
\end{itemize}

Outputs include filtered files per region, a full list of C2s with metadata, and a map of server locations.

## 🧩 Script 3: `enrich_unique_ipinfo_MAIN.py`

This script enriches the list of unique command-and-control (C2) server IPs using the IPinfo API. It collects additional metadata like ASN, geolocation, hosting provider, and whether the IP belongs to a VPN or hosting service. The enriched data helps improve botnet infrastructure mapping and supports geospatial analysis.

\begin{itemize}
    \item Input: CSV file with unique IP addresses.
    \item Output: CSV file with enriched metadata.
    \item Handles failed lookups gracefully and retries on timeout.
\end{itemize}

\textbf{Dependencies:}
\begin{itemize}
    \item `pandas` – for reading and writing CSV data.
    \item `requests` – for making API calls to IPinfo.
    \item 'API key' - api key for making calls to IPinfo
\end{itemize}
---

## 🧩 Script 4: `visualize_c2_aws_connections_MAIN.py`

This script reads C2 server data for each AWS region and creates GeoJSON files to show connections between botnet infrastructure and cloud sensors. It works by:

\begin{enumerate}
    \item Going through folders with filtered payload data.
    \item Picking out the C2 server IPs and their coordinates.
    \item Linking each C2 to the AWS region that captured its traffic.
    \item Saving everything as GeoJSON so it can be shown in tools like QGIS.
\end{enumerate}

\textbf{Dependencies:}
\begin{itemize}
    \item `pandas` – for working with CSV files.
    \item `json` – to write GeoJSON.
    \item `os` – for going through folders.
\end{itemize}

The script gives two output files:
\begin{itemize}
    \item \texttt{aws-nodes.geojson} – location points for AWS regions.
    \item \texttt{c2-to-aws-connections.geojson} – connection lines from C2 servers to AWS regions.
\end{itemize}
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
