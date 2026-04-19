import json, os, requests
from bs4 import BeautifulSoup

WEBHOOK_URL = os.environ.get("WEBHOOK_URL", "")
FICHIER_VUES = "tournois_vus.json"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "text/html,application/xhtml+xml,*/*;q=0.8",
}

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
    urls = [
        "https://matcherino.com/supercell/tournaments",
        "https://matcherino.com/t/featured",
    ]
    for url in urls:
        try:
            r = requests.get(url, headers=HEADERS, timeout=15)
            soup = BeautifulSoup(r.text, "html.parser")
            for lien in soup.find_all("a", href=True):
                href = lien["href"]
                texte = lien.get_text(strip=True)
                if "/tournaments/" in href and "EMEA" in texte.upper() and texte:
                    url_complete = "https://matcherino.com" + href if href.startswith("/") else href
                    entry = {"nom": texte, "url": url_complete}
                    if entry not in tournois:
                        tournois.append(entry)
        except Exception as e:
            print(f"Erreur {url}: {e}")
    print(f"Tournois EMEA détectés : {len(tournois)}")
    return tournois

def envoyer_alerte(tournoi):
    message = {
        "content": (
            f"🏆 **Nouveau tournoi EMEA Matcherino !**\n"
            f"**{tournoi['nom']}**\n"
            f"🔗 {tournoi['url']}"
        )
    }
    r = requests.post(WEBHOOK_URL, json=message)
    print(f"✅ Alerte envoyée : {tournoi['nom']} ({r.status_code})")

def main():
    vus = charger_vus()
    tournois = scraper_tournois()
    nouveaux = [t for t in tournois if t["url"] not in vus]
    for t in nouveaux:
        envoyer_alerte(t)
        vus.append(t["url"])
    sauvegarder_vus(vus)
    print(f"✅ Terminé — {len(nouveaux)} nouveau(x) tournoi(s).")

if __name__ == "__main__":
    main()
