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

    def __repr__(self):
        return f"Job(id={self.id}, prioridad={self.priority}, peso={self.weight}, deadline={self.deadline})"
