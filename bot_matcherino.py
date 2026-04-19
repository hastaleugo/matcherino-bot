import requests
import json
import os
from playwright.sync_api import sync_playwright

WEBHOOK_URL = os.environ.get("WEBHOOK_URL")
FICHIER_VUES = "tournois_vus.json"
URL_MATCHERINO = "https://matcherino.com/supercell/tournaments"

def charger_vus():
    if os.path.exists(FICHIER_VUES):
        with open(FICHIER_VUES, "r") as f:
            return json.load(f)
    return []

def sauvegarder_vus(liste):
    with open(FICHIER_VUES, "w") as f:
        json.dump(liste, f)

def scraper_tournois():
    tournois = []
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(URL_MATCHERINO, timeout=30000)
            page.wait_for_load_state("networkidle", timeout=20000)
            liens = page.query_selector_all("a[href*='/tournaments/']")
            for lien in liens:
                texte = lien.inner_text().strip()
                href = lien.get_attribute("href")
                if not texte or not href:
                    continue
                if "EMEA" in texte.upper():
                    url = "https://matcherino.com" + href if href.startswith("/") else href
                    tournois.append({"nom": texte, "url": url})
            browser.close()
    except Exception as e:
        print(f"Erreur scraping : {e}")
    return tournois

def envoyer_alerte(tournoi):
    message = {
        "content": (
            f"🏆 **Nouveau tournoi EMEA Matcherino !**\n"
            f"**{tournoi['nom']}**\n"
            f"🔗 {tournoi['url']}"
        )
    }
    requests.post(WEBHOOK_URL, json=message)
    print(f"✅ Alerte envoyée : {tournoi['nom']}")

def main():
    envoyer_alerte({"nom": "TEST - Bot opérationnel ✅", "url": "https://matcherino.com"})

if __name__ == "__main__":
    main()
