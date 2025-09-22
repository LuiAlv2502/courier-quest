import requests
import json

# Realiza una solicitud a la API y guarda los datos en archivos JSON
# Primero se define la url de la api y los endpoints que se van a consultar dentro de un diccionario
# Luego se itera sobre el diccionario, haciendo una solicitud GET a cada
# endpoint utilizando la biblioteca requests.
def api_request():
    base_url = "https://tigerds-api.kindflower-ccaf48b6.eastus.azurecontainerapps.io"
    endpoints = {
    "city_map": "/city/map",
    "city_jobs": "/city/jobs",
    "city_weather": "/city/weather"
}
    import sys
    for name, endpoint in endpoints.items():
        url = base_url + endpoint
        try:
            response = requests.get(url, timeout=10)
        except requests.exceptions.Timeout:
            print(f"La API no respondió en 10 segundos para {name}. Cerrando el programa.")
            sys.exit()
        except Exception as e:
            print(f"Error al conectar con la API para {name}: {e}")
            sys.exit()
        if response.status_code == 200:
            data = response.json()
            with open(f"json_files/{name}.json", "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
            print(f"Archivo guardado: {name}.json")
        else:
            print(f"Error al obtener {name}: {response.status_code}")