class JobManager:
    def __init__(self, jobs):
        self.available_jobs = jobs  # lista de Job
        self.visible_jobs = []      # trabajos que se pueden mostrar/aceptar

    def update_visible_jobs(self, current_time):
        # Solo mostrar trabajos cuando (current_time - release_time) == 0
        nuevos_visibles = []
        for job in self.available_jobs:
            release_time = job.release_time if hasattr(job, 'release_time') else 0
            try:
                release_time = int(release_time)
            except (ValueError, TypeError):
                release_time = 0
            # Si el trabajo ya está visible, no lo agregues de nuevo
            if job in self.visible_jobs:
                continue
            # Solo liberar el trabajo exactamente en el frame correcto
            if current_time - release_time == 0:
                nuevos_visibles.append(job)
        self.visible_jobs.extend(nuevos_visibles)

    def show_jobs(self):
        # Devuelve los trabajos visibles para mostrar en pantalla
        return self.visible_jobs

    def remove_job(self, job_id):
        self.available_jobs = [job for job in self.available_jobs if job.id != job_id]
        self.visible_jobs = [job for job in self.visible_jobs if job.id != job_id]
