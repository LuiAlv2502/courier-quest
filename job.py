class Job:
    def __init__(self, id, pickup, dropoff, payout, deadline, weight, priority, release_time):
        self.id = id
        self.pickup = tuple(pickup)
        self.dropoff = tuple(dropoff)
        self.payout = payout
        self.deadline = deadline  # Puede ser string o datetime
        self.weight = weight
        self.priority = priority
        self.release_time = release_time
        self.recogido = False

    def get_release_time(self):
        """Devuelve el tiempo de liberación del trabajo como entero."""
        try:
            return int(self.release_time)
        except (ValueError, TypeError):
            return 0

    def is_recogido(self):
        return self.recogido

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
            'release_time': int(self.release_time)  # Siempre guardar como int
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
            int(data['release_time'])  # Siempre cargar como int
        )
