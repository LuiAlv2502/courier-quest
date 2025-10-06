import heapq

class JobManager:
    def __init__(self, jobs):
        self.job_priority_queue = []
        for job in jobs:
            self.add_job_to_queue(job)
        self.visible_jobs = []

    def add_job_to_queue(self, job):
        # Insertar en la cola de prioridad
        heapq.heappush(self.job_priority_queue, (job.get_release_time(), job.id, job))

    def get_pending_jobs(self):
        # Retorna solo los objetos Job de la cola de prioridad
        return [job for _, _, job in self.job_priority_queue]

    def update_visible_jobs(self, current_time):
        # Liberar trabajos de la cola de prioridad cuando el tiempo actual alcanza o supera el release_time
        while self.job_priority_queue and self.job_priority_queue[0][0] <= current_time:
            release_time, job_id, job = heapq.heappop(self.job_priority_queue)
            self.visible_jobs.append(job)

    def show_jobs(self):
        # Devuelve los trabajos visibles para mostrar en pantalla
        return self.visible_jobs

    def remove_job(self, job_id):
        # Eliminar de la cola de prioridad
        new_queue = []
        for release_time, jid, job in self.job_priority_queue:
            if jid != job_id:
                new_queue.append((release_time, jid, job))
        self.job_priority_queue = new_queue
        heapq.heapify(self.job_priority_queue)

        # Eliminar de visible_jobs
        self.visible_jobs = [job for job in self.visible_jobs if job.id != job_id]
