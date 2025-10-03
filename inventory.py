import heapq

# Inventario: gestiona los trabajos aceptados y recogidos por el jugador
# Algoritmos clave:
# - Heap Sort para filtrar por prioridad
# - Insertion Sort para ordenar por deadline

class Inventory:
    def __init__(self, max_weight):
        self.max_weight = max_weight
        self.jobs = []  # lista de Job aceptados (todos)
        self.picked_jobs = []  # lista de Job recogidos (solo los que están físicamente con el personaje)

    def pickup_job(self, job, character_pos, mapa=None):
        # Si el jugador está en el pickup (mismo tile), recoge el trabajo
        if character_pos == job.pickup:
            job.recogido = True
            # Mover el trabajo a la lista de recogidos si no está ya ahí
            if job not in self.picked_jobs:
                self.picked_jobs.append(job)
            return True
        return False

    def deliver_job(self, job, character_pos, mapa=None):
        # Si el jugador está en el dropoff (mismo tile), entrega el trabajo
        if character_pos == job.dropoff and job.recogido:
            self.remove_job(job.id)
            return True
        return False

    def total_weight(self):
        """Devuelve el peso total de los trabajos recogidos en el inventario."""
        return sum(job.weight for job in self.picked_jobs)

    def accept_job(self, job):
        """Acepta un job si no excede el peso máximo."""
        # Usar get_total_jobs_weight() para considerar todos los trabajos (recogidos y no recogidos)
        if self.get_total_jobs_weight() + job.weight <= self.max_weight:
            self.jobs.append(job)
            return True
        return False

    def reject_job(self, job):
        """No lo añade, solo lógica de rechazo."""
        pass

    def remove_job(self, job_id):
        """Elimina un job por id de ambas listas."""
        # Eliminar de la lista principal
        self.jobs = [job for job in self.jobs if job.id != job_id]
        # Eliminar de la lista de recogidos
        self.picked_jobs = [job for job in self.picked_jobs if job.id != job_id]

    def traverse(self, reverse=False):
        """Recorre el inventario hacia adelante o atrás."""
        return self.jobs[::-1] if reverse else self.jobs

    def filter_by_priority(self):
        """Devuelve los jobs ordenados por prioridad (mayor primero) usando un heap.
        Se agrega un desempate por id (o índice) para evitar comparar objetos Job directamente.
        """
        heap = []
        for idx, job in enumerate(self.jobs):
            tiebreaker = getattr(job, 'id', idx)
            # Usamos prioridad negativa para que mayor prioridad salga primero
            heap.append((-job.priority, tiebreaker, job))
        heapq.heapify(heap)
        sorted_jobs = []
        while heap:
            _, _, job = heapq.heappop(heap)
            sorted_jobs.append(job)
        return sorted_jobs

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

    def get_max_weight(self):
        """Devuelve el peso máximo del inventario."""
        return self.max_weight

    def get_current_weight(self):
        """Devuelve el peso actual del inventario (solo trabajos recogidos)."""
        return self.total_weight()

    def get_total_jobs_weight(self):
        """Devuelve el peso total de todos los trabajos (recogidos y no recogidos)."""
        return sum(job.weight for job in self.jobs)

    def get_jobs(self):
        """Devuelve la lista de trabajos en el inventario."""
        return self.jobs

    def get_picked_jobs(self):
        """Devuelve la lista de trabajos recogidos."""
        return self.picked_jobs
