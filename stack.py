# Clase Stack para historial de movimientos
class Stack:
    def __init__(self):
        self.items = []

    def push(self, item):
        self.items.append(item)

    def pop(self):
        if self.items:
            return self.items.pop()
        return None

    def is_empty(self):
        return len(self.items) == 0

    def peek(self):
        if self.items:
            return self.items[-1]
        return None
