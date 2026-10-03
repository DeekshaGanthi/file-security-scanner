import os
import requests

VT_API_URL = "https://www.virustotal.com/api/v3/files/"


def check_virustotal_hash(sha256: str):
    """
    Queries VirusTotal API v3 using file SHA-256.
    Requires VIRUSTOTAL_API_KEY in .env.
    """
    api_key = os.getenv("VIRUSTOTAL_API_KEY")

    if not api_key:
        return {
            "enabled": False,
            "message": "VirusTotal API key not configured in .env"
        }

    headers = {
        "x-apikey": api_key,
        "Accept": "application/json"
    }

    try:
        response = requests.get(f"{VT_API_URL}{sha256}", headers=headers, timeout=5)

        if response.status_code == 404:
            return {
                "enabled": True,
                "known_malware": False,
                "message": "Hash not found in VirusTotal database (New or unique file)"
            }

        if response.status_code == 200:
            data = response.json()
            stats = data.get("data", {}).get("attributes", {}).get("last_analysis_stats", {})
            malicious = stats.get("malicious", 0)
            suspicious = stats.get("suspicious", 0)
            undetected = stats.get("undetected", 0)

            return {
                "enabled": True,
                "known_malware": malicious > 0,
                "positives": malicious,
                "suspicious": suspicious,
                "total_engines": malicious + suspicious + undetected,
                "reputation": data.get("data", {}).get("attributes", {}).get("reputation", 0)
            }

        return {
            "enabled": True,
            "error": f"VirusTotal returned status {response.status_code}"
        }

    except Exception as e:
        return {
            "enabled": True,
            "error": str(e)
        }