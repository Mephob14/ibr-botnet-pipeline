import pandas as pd
import requests
import time

# === CONFIG ===
API_TOKEN = "insert your api token here"
INPUT_FILE = "/mnt/d/Ibr-data/global_outputs/unique_c2_servers.csv"
OUTPUT_FILE = "/mnt/d/Ibr-data/global_outputs/unique_c2_servers_enriched.csv"
API_URL = "https://ipinfo.io/{ip}?token=" + API_TOKEN
DELAY = 0.8  # polite delay

# === Load Input ===
df = pd.read_csv(INPUT_FILE)
print(f" Loaded {len(df)} IPs from {INPUT_FILE}")

# === Prepare for Enrichment ===
enriched_data = []

# === Loop through IPs ===
for idx, ip in enumerate(df["c2_server"], 1):
    print(f" [{idx}/{len(df)}] Enriching: {ip}")

    try:
        response = requests.get(API_URL.format(ip=ip), timeout=10)
        data = response.json()

        enriched_data.append({
            "c2_server": ip,
            "count": df.loc[idx - 1, "count"],  # retain original count
            "country": df.loc[idx - 1, "country"],
            "city": df.loc[idx - 1, "city"],
            "latitude": df.loc[idx - 1, "latitude"],
            "longitude": df.loc[idx - 1, "longitude"],
            "asn": data.get("org"),
            "hostname": data.get("hostname"),
            "region": data.get("region"),
            "timezone": data.get("timezone"),
            "anycast": data.get("anycast"),
            "abuse_contact": data.get("abuse", {}).get("address") if "abuse" in data else None,
            "privacy_vpn": data.get("privacy", {}).get("vpn") if "privacy" in data else None,
            "privacy_proxy": data.get("privacy", {}).get("proxy") if "privacy" in data else None,
            "privacy_tor": data.get("privacy", {}).get("tor") if "privacy" in data else None,
            "carrier": data.get("carrier", {}).get("name") if "carrier" in data else None,
        })

    except Exception as e:
        print(f" Failed to enrich {ip}: {e}")
        enriched_data.append({
            "c2_server": ip,
            "count": df.loc[idx - 1, "count"],
            "country": df.loc[idx - 1, "country"],
            "city": df.loc[idx - 1, "city"],
            "latitude": df.loc[idx - 1, "latitude"],
            "longitude": df.loc[idx - 1, "longitude"],
            "asn": "ERROR",
            "hostname": "ERROR",
            "region": "ERROR",
            "timezone": "ERROR",
            "anycast": "ERROR",
            "abuse_contact": "ERROR",
            "privacy_vpn": "ERROR",
            "privacy_proxy": "ERROR",
            "privacy_tor": "ERROR",
            "carrier": "ERROR"
        })

    time.sleep(DELAY)

# === Save Results ===
enriched_df = pd.DataFrame(enriched_data)
enriched_df.to_csv(OUTPUT_FILE, index=False)
print(f"\n Enriched dataset saved to: {OUTPUT_FILE}")
