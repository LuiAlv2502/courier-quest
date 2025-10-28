import random

class AIController:
    dificulty = "easy"

    def __init__(self, dificulty="easy", inventory=None, game=None):
        self.dificulty = dificulty
        self.inventory = inventory
        self.game = game

    def manage_move(self, character):
        if self.dificulty == "easy":
            return self.random_move(character)
        # Future difficulty levels can be added here
        return None
    
    def random_move(self, character):
        directions = ['up', 'down', 'left', 'right']
        move = random.choice(directions)
        if move == 'up':
            return (0, -1)
        elif move == 'down':
            return (0, 1)
        elif move == 'left':
            return (-1, 0)
        elif move == 'right':
            return (1, 0)

    def dijkstra_move(self, character, target_tile):
        # Placeholder for Dijkstra's algorithm implementation
        pass
    def change_dificulty(self, new_dificulty):
        self.dificulty = new_dificulty