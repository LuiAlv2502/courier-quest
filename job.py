class Job:
    def __init__(self, id, pickup, dropoff, payout, deadline, weight, priority, release_time):
        self.id = id
        self.pickup = tuple(pickup)
        self.dropoff = tuple(dropoff)
        self.payout = payout
        self.deadline = deadline
        self.weight = weight
        self.priority = priority
        self.release_time = release_time
        self.picked_up = False

    def get_release_time(self):
        """Devuelve el tiempo de liberación del trabajo como entero."""
        try:
            return int(self.release_time)
        except (ValueError, TypeError):
            return 0

    def is_picked_up(self):
        return self.picked_up

    def __repr__(self):
        return (
            f"Job(id={self.id}, prioridad={self.priority}, peso={self.weight}, "
            f"deadline={self.deadline})"
        )

    def to_dict(self):
        """Serializa el trabajo a un diccionario."""
        return {
            'id': self.id,
            'pickup': self.pickup,
            'dropoff': self.dropoff,
            'payout': self.payout,
            'deadline': self.deadline,
            'weight': self.weight,
            'priority': self.priority,
            'release_time': int(self.release_time)
        }

    @classmethod
    def from_dict(cls, data):
        """Crea un objeto Job a partir de un diccionario."""
        return cls(
            data['id'],
            data['pickup'],
            data['dropoff'],
            data['payout'],
            data['deadline'],
            data['weight'],
            data['priority'],
            int(data['release_time'])
        )

    def is_expired(self, elapsed_seconds):
        """
        Devuelve True si el trabajo ha expirado (el tiempo actual ha superado el deadline).
        El deadline se espera en formato 'HH:MM:SS', 'HH:MM' o puede terminar en 'Z'.
        """
        try:
            if 'T' in self.deadline:
                time_part = self.deadline.split('T')[1]
            else:
                time_part = self.deadline
            time_part = time_part.rstrip('Z')
            parts = time_part.split(":")
            if len(parts) == 2:
                min_deadline = int(parts[0])
                sec_deadline = int(parts[1])
                deadline_seconds = min_deadline * 60 + sec_deadline
            elif len(parts) == 3:
                hour_deadline = int(parts[0])
                min_deadline = int(parts[1])
                sec_deadline = int(parts[2])
                deadline_seconds = hour_deadline * 3600 + min_deadline * 60 + sec_deadline
            else:
                return False
            return elapsed_seconds > deadline_seconds
        except Exception:
            return False
