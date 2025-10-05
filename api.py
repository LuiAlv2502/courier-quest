import requests
import json
import os
from datetime import datetime

def get_latest_cache_file(cache_dir, name):
    """Busca el archivo de caché más reciente para un endpoint específico."""
    if not os.path.exists(cache_dir):
        return None

    cache_files = []
    for fname in os.listdir(cache_dir):
        if fname.startswith(f"{name}_") and fname.endswith('.json'):
            cache_files.append(fname)

    if not cache_files:
        return None

    # Ordenar por fecha/hora en el nombre del archivo (más reciente primero)
    cache_files.sort(reverse=True)
    return os.path.join(cache_dir, cache_files[0])

def save_api_data(data, name, cache_dir="api_cache"):
    """Guarda los datos tanto en json_files como en el caché con timestamp."""
    os.makedirs("json_files", exist_ok=True)
    os.makedirs(cache_dir, exist_ok=True)

    # Guardar en json_files (archivo principal)
    main_file = f"json_files/{name}.json"
    with open(main_file, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    print(f"Archivo guardado: {name}.json")

    # Guardar en caché con timestamp
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    cache_file = os.path.join(cache_dir, f"{name}_{timestamp}.json")
    with open(cache_file, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    print(f"Caché guardado: {os.path.basename(cache_file)}")

def load_from_cache(name, cache_dir="api_cache"):
    """Carga los datos desde el caché más reciente y los copia a json_files."""
    latest_cache = get_latest_cache_file(cache_dir, name)

    if latest_cache and os.path.exists(latest_cache):
        print(f"Usando caché offline para {name}: {os.path.basename(latest_cache)}")
        with open(latest_cache, "r", encoding="utf-8") as f:
            data = json.load(f)

        os.makedirs("json_files", exist_ok=True)
        with open(f"json_files/{name}.json", "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

        return True
    else:
        print(f"No hay caché disponible para {name}.")
        return False

def api_request():
    """
    Realiza una solicitud a la API y guarda los datos en archivos JSON.
    Primero se define la url de la api y los endpoints que se van a consultar dentro de un diccionario.
    Luego se itera sobre el diccionario, haciendo una solicitud GET a cada endpoint.
    """
    base_url = "https://tigerds-api.kindflower-ccaf48b6.eastus.azurecontainerapps.io"
    endpoints = {
        "city_map": "/city/map",
        "city_jobs": "/city/jobs",
        "city_weather": "/city/weather"
    }
    cache_dir = "api_cache"
    os.makedirs(cache_dir, exist_ok=True)

    for name, endpoint in endpoints.items():
        url = base_url + endpoint
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                save_api_data(data, name, cache_dir)
            else:
                print(f"Error al obtener {name}: {response.status_code}")
                load_from_cache(name, cache_dir)

        except Exception as e:
            print(f"Error al conectar con la API para {name}: {e}")
            load_from_cache(name, cache_dir)
