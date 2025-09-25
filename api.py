# Versión restaurada con caché adicional en api_cache
def api_request():
    base_url = "https://tigerds-api.kindflower-ccaf48b6.eastus.azurecontainerapps.io"
    endpoints = {
        "city_map": "/city/map",
        "city_jobs": "/city/jobs",
        "city_weather": "/city/weather"
    }
    import sys
    cache_dir = "api_cache"
    os.makedirs(cache_dir, exist_ok=True)
    for name, endpoint in endpoints.items():
        url = base_url + endpoint
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                # Guardar en json_files (lógica original)
                with open(f"json_files/{name}.json", "w", encoding="utf-8") as f:
                    json.dump(data, f, ensure_ascii=False, indent=4)
                print(f"Archivo guardado: {name}.json")
                # Guardar también en api_cache con fecha/hora
                cache_file = os.path.join(cache_dir, f"{name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
                with open(cache_file, "w", encoding="utf-8") as f:
                    json.dump(data, f, ensure_ascii=False, indent=4)
            else:
                print(f"Error al obtener {name}: {response.status_code}")
                # Si falla, buscar la última versión cacheada
                latest_cache = None
                for fname in sorted(os.listdir(cache_dir), reverse=True):
                    if fname.startswith(name) and fname.endswith('.json'):
                        latest_cache = os.path.join(cache_dir, fname)
                        break
                if latest_cache and os.path.exists(latest_cache):
                    print(f"Usando caché offline para {name}: {latest_cache}")
                    with open(latest_cache, "r", encoding="utf-8") as f:
                        data = json.load(f)
                    with open(f"json_files/{name}.json", "w", encoding="utf-8") as f2:
                        json.dump(data, f2, ensure_ascii=False, indent=4)
                else:
                    print(f"No hay caché disponible para {name}.")
        except Exception as e:
            print(f"Error al conectar con la API para {name}: {e}")
            # Si falla, buscar la última versión cacheada
            latest_cache = None
            for fname in sorted(os.listdir(cache_dir), reverse=True):
                if fname.startswith(name) and fname.endswith('.json'):
                    latest_cache = os.path.join(cache_dir, fname)
                    break
            if latest_cache and os.path.exists(latest_cache):
                print(f"Usando caché offline para {name}: {latest_cache}")
                with open(latest_cache, "r", encoding="utf-8") as f:
                    data = json.load(f)
                with open(f"json_files/{name}.json", "w", encoding="utf-8") as f2:
                    json.dump(data, f2, ensure_ascii=False, indent=4)
            else:
                print(f"No hay caché disponible para {name}.")
import requests
import json
import os
from datetime import datetime

# Realiza una solicitud a la API y guarda los datos en archivos JSON
# Primero se define la url de la api y los endpoints que se van a consultar dentro de un diccionario
# Luego se itera sobre el diccionario, haciendo una solicitud GET a cada
# endpoint utilizando la biblioteca requests.
def get_data_with_cache(api_url, cache_name, fallback_path=None):
    cache_dir = "api_cache"
    os.makedirs(cache_dir, exist_ok=True)
    cache_file = os.path.join(cache_dir, f"{cache_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
    latest_cache = None
    # Buscar la última versión cacheada
    for fname in sorted(os.listdir(cache_dir), reverse=True):
        if fname.startswith(cache_name) and fname.endswith('.json'):
            latest_cache = os.path.join(cache_dir, fname)
            break
    try:
        response = requests.get(api_url, timeout=10)
        response.raise_for_status()
        data = response.json()
        # Guardar en caché con fecha/hora
        with open(cache_file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        return data
    except Exception:
        # Si falla, usar la última versión cacheada
        if latest_cache and os.path.exists(latest_cache):
            with open(latest_cache, "r", encoding="utf-8") as f:
                return json.load(f)
        # Si no hay caché, usar archivo local de respaldo
        if fallback_path and os.path.exists(fallback_path):
            with open(fallback_path, "r", encoding="utf-8") as f:
                return json.load(f)
        raise RuntimeError("No hay datos disponibles del API, caché ni respaldo local.")

# Maneja varios endpoints y cachea cada uno

# Ejemplo de uso:
# endpoints = {
#     "city_map": "/city/map",
#     "city_jobs": "/city/jobs",
#     "city_weather": "/city/weather"
# }
# fallback_map = {
#     "city_map": "data/ciudad.json",
#     "city_jobs": "data/pedidos.json",
#     "city_weather": "data/weather.json"
# }
# base_url = "https://tigerds-api.kindflower-ccaf48b6.eastus.azurecontainerapps.io"
# datos = fetch_all_endpoints_with_cache(base_url, endpoints, fallback_map)
# ciudad = get_data_with_cache("https://tigerds-api.kindflower-ccaf48b6.eastus.azurecontainerapps.io/city/map", "ciudad", "data/ciudad.json")
# pedidos = get_data_with_cache("https://tigerds-api.kindflower-ccaf48b6.eastus.azurecontainerapps.io/city/jobs", "pedidos", "data/pedidos.json")
# weather = get_data_with_cache("https://tigerds-api.kindflower-ccaf48b6.eastus.azurecontainerapps.io/city/weather", "weather", "data/weather.json")