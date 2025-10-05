import json
from job import Job

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
