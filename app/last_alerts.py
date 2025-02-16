import requests
import json
import os

GIST_ID = os.getenv("LAST_ALERTS_GIST_ID")
TOKEN = os.getenv("GIST_TOKEN")
HEADERS = {"Authorization": f"token {TOKEN}", "Accept": "application/vnd.github.v3+json"}

# Baixa o conteúdo do Gist e retorna como dicionário
def load_last_alerts():
    url = f"https://api.github.com/gists/{GIST_ID}"
    response = requests.get(url, headers=HEADERS)
    if response.status_code == 200:
        content: dict[str, list[str]] = json.loads(response.json()["files"]["last_alerts.json"]["content"])
        return content
  
    print(f"⚠️ Erro ao carregar os alertas anteriores: \n{response.json()}")


# Salva os alertas no Gist
def save_last_alerts(alerts: dict[str, list[str]]):
    url = f"https://api.github.com/gists/{GIST_ID}"
    data = {
        "files": {
            "last_alerts.json": {
                "content": json.dumps(alerts, indent=2)
            }
        }
    }
    response = requests.patch(url, headers=HEADERS, json=data)
    
    if response.status_code == 200:
        return True

    print(f"⚠️ Erro ao salvar os alertas: \n{response.json()}")

def handle_alerts(assets_notes: dict[str, list[str]]):
    last_alerts = load_last_alerts()

    for asset, notes in assets_notes.items():
        for note in notes:
            if note  in last_alerts.get(asset, []):
                assets_notes[asset].remove(note)

    assets_notes = {k: v for k, v in assets_notes.items() if v}

    if assets_notes:
        print("🔍 Novos alertas de preços:\n", assets_notes)
    else:
        print("✅ Nenhum alerta de preço.")

    save_last_alerts(assets_notes)
    return assets_notes