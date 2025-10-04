import json
from job import Job
from collections import deque

def nearest_accessible(tile, mapa):
    visited = set()
    queue = deque()
    queue.append((tile[0], tile[1], 0))
    while queue:
        x, y, dist = queue.popleft()
        if (x, y) in visited:
            continue
        visited.add((x, y))
        if 0 <= x < mapa.width and 0 <= y < mapa.height and not mapa.is_blocked(x, y):
            return (x, y)
        for dx, dy in [(-1,0),(1,0),(0,-1),(0,1)]:
            nx, ny = x+dx, y+dy
            if (nx, ny) not in visited:
                queue.append((nx, ny, dist+1))
    return tile  # Si no encuentra accesible, regresa el original

def load_jobs(jobs_json_path):
    """
    Carga los trabajos tal cual están en el JSON, sin ajustar pickup/dropoff a tiles accesibles.
    Útil para pruebas rápidas o para validar el contenido del JSON sin lógica extra.
    """
    with open(jobs_json_path, "r", encoding="utf-8") as f:
        jobs_data = json.load(f)["data"]
    jobs_list = []
    for job in jobs_data:
        job_obj = Job(
            id=job["id"],
            pickup=tuple(job["pickup"]),
            dropoff=tuple(job["dropoff"]),
            payout=job["payout"],
            deadline=job["deadline"],
            weight=job["weight"],
            priority=job["priority"],
            release_time=job["release_time"],
        )
        jobs_list.append(job_obj)
    return jobs_list
