# This script processes filtered C2 payload data for each AWS region and visualizes the
# connections between botnet C2 servers and AWS regions using GeoJSON. The main steps 
# include:
# 1. Iterating through the region directories to find and load the filtered C2 payload data.
# 2. Extracting unique C2 server IPs and their geographic coordinates from the data.
# 3. Mapping the connections between C2 servers and their corresponding AWS region on a global scale.
# 4. Saving the AWS region nodes and the C2-to-AWS connections as GeoJSON files for further analysis or visualization.
# 
# Required Libraries:
# - pandas: For reading and processing the CSV files.
# - json: For saving the output as GeoJSON.
# - os: For navigating the file system and managing directories.
# 
# The output includes two GeoJSON files: 
# 1. `aws_nodes.geojson` - Containing the geographical locations of AWS regions.
# 2. `c2_to_aws_connections.geojson` - Showing the connections between C2 servers and AWS regions.

# Script made by Mads Folkestad

import os
import pandas as pd
import json

# Base directory containing region folders
BASE_DIR = "/mnt/d/Ibr-data/e2"
GLOBAL_OUTPUT_DIR = "/mnt/d/Ibr-data/global_outputs"

# AWS region coordinates (approximate lat/lon for mapping)
AWS_REGION_COORDS = {
    "af-south-1": (-33.9249, 18.4241),  # Cape Town, South Africa
    "ap-east-1": (22.3193, 114.1694),  # Hong Kong
    "ap-northeast-1": (35.6895, 139.6917),  # Tokyo, Japan
    "ap-northeast-2": (37.5665, 126.9780),  # Seoul, South Korea
    "ap-northeast-3": (34.6937, 135.5023),  # Osaka, Japan
    "ap-south-1": (19.0760, 72.8777),  # Mumbai, India
    "ap-south-2": (17.3850, 78.4867),  # Hyderabad, India
    "ap-southeast-1": (1.3521, 103.8198),  # Singapore
    "ap-southeast-2": (-33.8688, 151.2093),  # Sydney, Australia
    "ap-southeast-3": (-6.2088, 106.8456),  # Jakarta, Indonesia
    "ca-central-1": (45.4215, -75.6972),  # Canada (Montreal)
    "eu-central-1": (50.1109, 8.6821),  # Frankfurt, Germany
    "eu-central-2": (47.3769, 8.5417),  # Zurich, Switzerland
    "eu-north-1": (59.3293, 18.0686),  # Stockholm, Sweden
    "eu-south-1": (41.9028, 12.4964),  # Rome, Italy
    "eu-south-2": (40.4168, -3.7038),  # Madrid, Spain
    "eu-west-1": (53.3498, -6.2603),  # Dublin, Ireland
    "eu-west-2": (51.5074, -0.1278),  # London, UK
    "eu-west-3": (48.8566, 2.3522),  # Paris, France
    "me-central-1": (25.276987, 55.296249),  # Dubai, UAE
    "me-south-1": (-26.2041, 28.0473),  # Johannesburg, South Africa
    "sa-east-1": (-23.5505, -46.6333),  # São Paulo, Brazil
    "us-east-1": (39.0438, -77.4874),  # N. Virginia, USA
    "us-east-2": (40.4173, -82.9071),  # Ohio, USA
    "us-west-1": (37.7749, -122.4194),  # San Francisco, USA
    "us-west-2": (45.5234, -122.6762),  # Oregon, USA
}

# Ensure output directory exists
os.makedirs(GLOBAL_OUTPUT_DIR, exist_ok=True)

# Initialize storage for geojson files
aws_nodes = []
c2_to_aws_connections = []
seen_connections = set()  # To prevent duplicate (C2 IP, AWS Region) pairs

# Process each region folder
for region_folder in sorted(os.listdir(BASE_DIR)):
    folder_path = os.path.join(BASE_DIR, region_folder)

    if not os.path.isdir(folder_path):
        continue  # Skip non-folders

    # Identify the filtered C2 payload file
    filtered_file = None
    for file in os.listdir(folder_path):
        if file.endswith("_filtered_c2_payload.csv"):
            filtered_file = os.path.join(folder_path, file)
            break

    if not filtered_file:
        print(f" Skipping {folder_path}: No _filtered_c2_payload.csv found")
        continue

    region = region_folder.replace("e2_", "").replace(".pcap", "")  # Extract AWS region name

    # Ensure region is valid
    if region not in AWS_REGION_COORDS:
        print(f" Warning: No coordinates found for {region}, skipping...")
        continue

    aws_lat, aws_lon = AWS_REGION_COORDS[region]  # Get AWS region coordinates

    # Add AWS region node (only once)
    if not any(node["properties"]["region"] == region for node in aws_nodes):
        aws_nodes.append({
            "type": "Feature",
            "properties": {"region": region},
            "geometry": {"type": "Point", "coordinates": [aws_lon, aws_lat]},
        })

    # Load filtered CSV
    df = pd.read_csv(filtered_file, low_memory=False)

    # Extract unique C2 IPs for this AWS region
    for _, row in df.iterrows():
        c2_ip = row["c2_servers"]
        c2_lat = row["latitude"]
        c2_lon = row["longitude"]

        # Skip invalid C2 entries
        if pd.isna(c2_ip) or pd.isna(c2_lat) or pd.isna(c2_lon):
            continue

        # Ensure uniqueness (each C2 is mapped only once per AWS region)
        if (c2_ip, region) not in seen_connections:
            c2_to_aws_connections.append({
                "type": "Feature",
                "properties": {"c2_ip": c2_ip, "aws_region": region},
                "geometry": {
                    "type": "LineString",
                    "coordinates": [[float(c2_lon), float(c2_lat)], [aws_lon, aws_lat]]
                }
            })
            seen_connections.add((c2_ip, region))  # Mark as seen

# Save AWS nodes to GeoJSON
aws_nodes_geojson = {
    "type": "FeatureCollection",
    "features": aws_nodes
}
aws_nodes_path = os.path.join(GLOBAL_OUTPUT_DIR, "aws_nodes.geojson")
with open(aws_nodes_path, "w") as f:
    json.dump(aws_nodes_geojson, f, indent=4)
print(f" AWS nodes saved to: {aws_nodes_path}")

# Save C2-to-AWS connections to GeoJSON
c2_connections_geojson = {
    "type": "FeatureCollection",
    "features": c2_to_aws_connections
}
c2_connections_path = os.path.join(GLOBAL_OUTPUT_DIR, "c2_to_aws_connections.geojson")
with open(c2_connections_path, "w") as f:
    json.dump(c2_connections_geojson, f, indent=4)
print(f" C2 to AWS connections saved to: {c2_connections_path}")

print("🚀 Processing complete!")