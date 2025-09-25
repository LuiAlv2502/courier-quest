
class JobManager:
    def __init__(self, jobs):
        self.available_jobs = jobs  # lista de Job
        self.visible_jobs = []      # trabajos que se pueden mostrar/aceptar

    def update_visible_jobs(self, current_time):
        # Liberar trabajos cuando (release_time - current_time) == 0
        nuevos_visibles = []
        for job in self.available_jobs:
            release_time = job.get_release_time()
            tiempo_restante = release_time - current_time
            if job not in self.visible_jobs and tiempo_restante == 0:
                nuevos_visibles.append(job)
        self.visible_jobs.extend(nuevos_visibles)

    def show_jobs(self):
        # Devuelve los trabajos visibles para mostrar en pantalla
        return self.visible_jobs

    def remove_job(self, job_id):
        self.available_jobs = [job for job in self.available_jobs if job.id != job_id]
        self.visible_jobs = [job for job in self.visible_jobs if job.id != job_id]
