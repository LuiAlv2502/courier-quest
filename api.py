import requests
import json

def api_request():
    base_url = "https://tigerds-api.kindflower-ccaf48b6.eastus.azurecontainerapps.io"
    endpoints = {
    "city_map": "/city/map",
    "city_jobs": "/city/jobs",
    "city_weather": "/city/weather"
}
    for name, endpoint in endpoints.items():
        url = base_url + endpoint
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            with open(f"json_files/{name}.json", "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
            print(f"Archivo guardado: {name}.json")
        else:
            print(f"Error al obtener {name}: {response.status_code}")