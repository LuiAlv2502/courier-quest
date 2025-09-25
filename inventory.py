
import heapq

# Inventario: gestiona los trabajos aceptados y recogidos por el jugador
# Algoritmos clave:
# - Heap Sort para filtrar por prioridad
# - Insertion Sort para ordenar por deadline

class Inventory:
    def __init__(self, max_weight):
        self.max_weight = max_weight
        self.jobs = []  # lista de Job aceptados

    def pickup_job(self, job, character_pos, mapa=None):
        # Si el jugador está en el pickup (mismo tile), recoge el trabajo
        if character_pos == job.pickup:
            job.recogido = True
            return True
        return False

    def deliver_job(self, job, character_pos, mapa=None):
        # Si el jugador está en el dropoff (mismo tile), entrega el trabajo
        if character_pos == job.dropoff and job.recogido:
            self.remove_job(job.id)
            return True
        return False

    def total_weight(self):
        """Devuelve el peso total de los trabajos en el inventario."""
        return sum(job.weight for job in self.jobs)

    def accept_job(self, job):
        """Acepta un job si no excede el peso máximo."""
        if self.total_weight() + job.weight <= self.max_weight:
            self.jobs.append(job)
            return True
        return False

    def reject_job(self, job):
        """No lo añade, solo lógica de rechazo."""
        pass

    def remove_job(self, job_id):
        """Elimina un job por id."""
        self.jobs = [job for job in self.jobs if job.id != job_id]

    def traverse(self, reverse=False):
        """Recorre el inventario hacia adelante o atrás."""
        return self.jobs[::-1] if reverse else self.jobs

    def filter_by_priority(self):
        """Devuelve los jobs ordenados por prioridad (mayor primero) usando heap sort."""
        # heapq.nlargest usa heap sort internamente
        return heapq.nlargest(len(self.jobs), self.jobs, key=lambda job: job.priority)

    def filter_by_deadline(self):
        """Devuelve los jobs ordenados por deadline (más pronto primero) usando insertion sort."""
        jobs_sorted = self.jobs[:]
        for i in range(1, len(jobs_sorted)):
            key_job = jobs_sorted[i]
            j = i - 1
            while j >= 0 and jobs_sorted[j].deadline > key_job.deadline:
                jobs_sorted[j + 1] = jobs_sorted[j]
                j -= 1
            jobs_sorted[j + 1] = key_job

        return jobs_sorted
