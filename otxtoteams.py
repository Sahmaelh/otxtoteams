#                           #
# Créer par Michael Lelon   #
# 24/04/2023                #
#                           #

import os
import requests
import json
import time
from datetime import datetime, timedelta
from requests.auth import HTTPBasicAuth

LAST_ID_FILE = "send_entries.txt"

def get_otx_data():
    while True:
        try:
            print("Récupération des données OTX...")
            url = "https://otx.alienvault.com:443/api/v1/pulses/subscribed"
            headers = {
                "X-OTX-API-KEY": "OTX_API_KEY",  # Remplacer "OTX_API_KEY" par votre clé api
            }
            response = requests.get(url, headers=headers, timeout=10)  # Ajout d'un timeout
            data = response.json()
            return data
        except requests.exceptions.Timeout:
            print("Timeout lors de la récupération des données OTX. Attente de 5 minutes avant de réessayer...")
            time.sleep(5 * 60)

def get_latest_entry(data):
    print("Obtention de la dernière entrée...")
    latest_entry = data["results"][0]  # Prendre la première entrée comme la dernière
    return latest_entry

def send_to_teams(entry):
    print("Envoi du message à Microsoft Teams...")
    webhook_url = "WEBHOOK URL" # Remplacer "WEBHOOK URL" par votre Webhook URL de Teams
    message = {
        "@context": "https://schema.org/extensions",
        "@type": "MessageCard",
        "themeColor": "0078D7",
        "title": entry["name"],
        "text": entry["description"] + f"\n\n\nhttps://otx.alienvault.com/pulse/" + entry["id"],
    }
    try:
        response = requests.post(webhook_url, json=message)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Erreur lors de l'envoi du message à Microsoft Teams: {e}")

def read_last_id_from_file():
    try:
        with open(LAST_ID_FILE, "r") as f:
            content = f.read().strip()
            return None if content == "" else content
    except FileNotFoundError:
        return None
    
def write_last_id_to_file(id):
    with open(LAST_ID_FILE, "w") as f:
        f.write(id)

def main():
    last_id = read_last_id_from_file()
    try:
        while True:
            print("Début de la boucle...")
            data = get_otx_data()
            latest_entry = get_latest_entry(data)

            if latest_entry and (last_id is None or latest_entry["id"] != last_id):
                send_to_teams(latest_entry)
                last_id = latest_entry["id"]
                write_last_id_to_file(last_id)

            print("Attente de 5 minutes...")
            time.sleep(5 * 60)
    except (KeyboardInterrupt, SystemExit):
        print("Script interrompu. Fermeture propre...")

if __name__ == "__main__":
    main()
