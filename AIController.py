import random
import time

import inventory


class AIController:
    def __init__(self, dificulty="easy", game=None):
        self.dificulty = dificulty
        self.game = game
        self.max_depth = 2  # Limited horizon: 2-3 actions ahead
        self.last_move_time = 0  # Track when the last move was made
        self.move_delay = 0.5  # 0.5 seconds delay between moves

        # Loop detection
        self.position_history = []  # Track recent positions
        self.max_history = 8  # Keep track of last 8 positions
        self.loop_detected = False
        self.loop_break_moves = 0  # Counter for how many moves to break loop

    def manage_move(self, character, weather=None, inventory=None):
        # Check if enough time has passed since the last move
        current_time = time.time()
        if current_time - self.last_move_time < self.move_delay:
            return (0, 0)  # No movement, not enough time has passed

        # Update the last move time
        self.last_move_time = current_time

        if self.dificulty == "easy":
            return self.random_move(character)
        elif self.dificulty == "medium":
            return self.expectimax_move(character, weather, inventory)
        return (0, 0)

    def random_move(self, character):
        directions = [(0, -1), (0, 1), (-1, 0), (1, 0)]  # up, down, left, right
        return random.choice(directions)

    def expectimax_move(self, character, weather=None, inventory=None):
        """Medium difficulty: Expectimax with simple scoring function."""
        if character.resistencia_exhausto:
            return (0, 0)

        # Check if AI has any jobs to work on
        char_inventory = inventory if inventory is not None else getattr(character, 'inventory', None)
        has_jobs = False

        # Check for picked up jobs (ready for delivery)
        if char_inventory and hasattr(char_inventory, 'get_picked_jobs'):
            picked_jobs = char_inventory.get_picked_jobs()
            if picked_jobs:
                has_jobs = True

        # Check for accepted but not picked up jobs
        if char_inventory and hasattr(char_inventory, 'get_jobs'):
            all_jobs = char_inventory.get_jobs()
            for job in all_jobs:
                if not job.is_picked_up():
                    has_jobs = True
                    break

        # Check for visible jobs from job_manager
        if not has_jobs and self.game and hasattr(self.game, 'job_manager'):
            visible_jobs = []
            if hasattr(self.game.job_manager, 'visible_jobs'):
                visible_jobs = self.game.job_manager.visible_jobs
            elif hasattr(self.game.job_manager, 'show_jobs'):
                visible_jobs = self.game.job_manager.show_jobs()

            if visible_jobs:
                has_jobs = True

        # If no jobs available, stay still
        if not has_jobs:
            return (0, 0)

        current_pos = (character.tile_x, character.tile_y)

        # Update position history
        self.position_history.append(current_pos)
        if len(self.position_history) > self.max_history:
            self.position_history.pop(0)

        # Check for loop detection
        if self.loop_break_moves > 0:
            # We're in loop-breaking mode, use random movement
            self.loop_break_moves -= 1
            directions = [(0, -1), (0, 1), (-1, 0), (1, 0)]  # up, down, left, right
            valid_directions = [move for move in directions if self.is_valid_move(character, move)]
            if valid_directions:
                return random.choice(valid_directions)
            else:
                return (0, 0)

        # Detect if we're in a loop (visiting same positions repeatedly)
        if len(self.position_history) >= 6:  # Need at least 6 positions to detect a loop
            position_counts = {}
            for pos in self.position_history[-6:]:  # Check last 6 positions
                position_counts[pos] = position_counts.get(pos, 0) + 1

            # If any position appears 3 or more times in recent history, we're likely in a loop
            max_count = max(position_counts.values()) if position_counts else 0
            if max_count >= 3:
                self.loop_detected = True
                self.loop_break_moves = 3  # Break loop for next 3 moves
                # Use random movement immediately
                directions = [(0, -1), (0, 1), (-1, 0), (1, 0)]
                valid_directions = [move for move in directions if self.is_valid_move(character, move)]
                if valid_directions:
                    return random.choice(valid_directions)

        # Normal expectimax behavior
        _, best_move = self.expectimax(character, self.max_depth, True, weather, inventory)

        # If expectimax returns None or invalid move, use random valid move
        if not best_move or not self.is_valid_move(character, best_move):
            directions = [(0, -1), (0, 1), (-1, 0), (1, 0)]
            valid_directions = [move for move in directions if self.is_valid_move(character, move)]
            if valid_directions:
                return random.choice(valid_directions)

        return best_move if best_move else (0, 0)

    def expectimax(self, character, depth, is_max_node, weather=None, inventory=None):
        """Expectimax algorithm."""
        if depth == 0:
            return self.evaluate_state(character, weather, inventory), None

        moves = [(0, -1), (0, 1), (-1, 0), (1, 0)]  # up, down, left, right, stay

        if is_max_node:  # AI turn
            best_score = float('-inf')
            best_move = None

            for move in moves:
                if self.is_valid_move(character, move):
                    # Create temporary character with new position for evaluation
                    temp_character = type('obj', (object,), {
                        'tile_x': character.tile_x + move[0],
                        'tile_y': character.tile_y + move[1],
                        'resistencia': character.resistencia,
                        'resistencia_exhausto': character.resistencia_exhausto,
                        'inventory': getattr(character, 'inventory', None)
                    })()

                    if depth == 1:
                        score = self.evaluate_state(temp_character, weather, inventory)
                    else:
                        score, _ = self.expectimax(temp_character, depth - 1, False, weather, inventory)

                    if score > best_score:
                        best_score = score
                        best_move = move

            return best_score, best_move

        else:  # Chance node
            total_score = 0.0
            count = 0

            for move in moves:
                if self.is_valid_move(character, move):
                    # Create temporary character with new position for evaluation
                    temp_character = type('obj', (object,), {
                        'tile_x': character.tile_x + move[0],
                        'tile_y': character.tile_y + move[1],
                        'resistencia': character.resistencia,
                        'resistencia_exhausto': character.resistencia_exhausto,
                        'inventory': getattr(character, 'inventory', None)
                    })()

                    if depth == 1:
                        score = self.evaluate_state(temp_character, weather, inventory)
                    else:
                        score, _ = self.expectimax(temp_character, depth - 1, True, weather, inventory)
                    total_score += score
                    count += 1

            return total_score / count if count > 0 else 0, None


    def evaluate_state(self, character, weather=None, inventory=None):
        """Simple scoring: score = α*(expected_payout) - β*(distance_cost) - γ*(weather_penalty)"""
        α, β, γ = 2.0, 1.0, 1.5

        # α*(expected_payout)
        expected_payout = self.calculate_payout(character, inventory)

        # β*(distance_cost)
        distance_cost = self.calculate_distance_cost(character, weather, inventory)

        # γ*(weather_penalty)
        weather_penalty = self.calculate_weather_penalty(weather)

        return α * expected_payout - β * distance_cost - γ * weather_penalty

    def calculate_payout(self, character, inventory=None):
        """Calculate expected payout from nearby jobs - considers both pickup and dropoff."""
        if not self.game or not hasattr(self.game, 'job_manager'):
            return 0.0

        payout = 0.0

        # Use passed inventory or character's inventory
        char_inventory = inventory if inventory is not None else getattr(character, 'inventory', None)

        # Check picked up jobs (ready for delivery) using get_picked_jobs()
        if char_inventory and hasattr(char_inventory, 'get_picked_jobs'):
            picked_jobs = char_inventory.get_picked_jobs()
            for job in picked_jobs:
                # Job is picked up, calculate distance to dropoff
                distance = abs(character.tile_x - job.dropoff[0]) + abs(character.tile_y - job.dropoff[1])
                # Always give value to picked up jobs regardless of distance (already committed)
                if distance <= 15:
                    # High value for nearby deliveries
                    payout += job.payout / (distance + 1) * 3.0
                elif distance <= 30:
                    # Medium value for moderately distant deliveries
                    payout += job.payout / (distance + 1) * 2.0
                else:
                    # Still some value for very distant deliveries
                    payout += job.payout / (distance + 1) * 1.5

        # Check accepted but not picked up jobs using get_jobs()
        if char_inventory and hasattr(char_inventory, 'get_jobs'):
            all_jobs = char_inventory.get_jobs()
            for job in all_jobs:
                if not job.is_picked_up():
                    # Job needs pickup
                    distance = abs(character.tile_x - job.pickup[0]) + abs(character.tile_y - job.pickup[1])
                    if distance <= 15:
                        # Good value for nearby pickups
                        payout += job.payout / (distance + 1) * 0.8
                    elif distance <= 30:
                        # Some value for distant pickups
                        payout += job.payout / (distance + 1) * 0.5
                    else:
                        # Minimal value for very distant pickups
                        payout += job.payout / (distance + 1) * 0.3

        # Also check visible jobs from job_manager for new opportunities
        visible_jobs = []
        if hasattr(self.game.job_manager, 'visible_jobs'):
            visible_jobs = self.game.job_manager.visible_jobs
        elif hasattr(self.game.job_manager, 'show_jobs'):
            visible_jobs = self.game.job_manager.show_jobs()

        for job in visible_jobs:
            if not job.is_picked_up():
                # Available job for pickup
                distance = abs(character.tile_x - job.pickup[0]) + abs(character.tile_y - job.pickup[1])
                if distance <= 15:
                    # Good value for nearby new jobs
                    payout += job.payout / (distance + 1) * 0.6
                elif distance <= 30:
                    # Some value for distant new jobs
                    payout += job.payout / (distance + 1) * 0.4
                else:
                    # Minimal value for very distant new jobs
                    payout += job.payout / (distance + 1) * 0.2

        return payout

    def calculate_distance_cost(self, character, weather=None, inventory=None):
        """Calculate movement costs considering weather and inventory weight."""
        cost = 0.0

        # Stamina penalty
        if character.resistencia < 30:
            cost += 10.0

        # Weight penalty from inventory
        if inventory and hasattr(inventory, 'get_total_weight'):
            total_weight = inventory.get_total_weight()
            cost += total_weight * 0.5  # Weight increases movement cost
        elif hasattr(character, 'total_weight'):
            cost += character.total_weight * 0.5

        # Weather movement penalty
        if weather and hasattr(weather, 'current_multiplier'):
            weather_mult = weather.current_multiplier
            if weather_mult < 1.0:
                # Bad weather increases movement cost
                cost += (1.0 - weather_mult) * 3.0

        return cost

    def calculate_weather_penalty(self, weather=None):
        """Calculate penalty based on weather conditions."""
        if not weather:
            # Try to get weather from game if not passed
            if self.game and hasattr(self.game, 'weather'):
                weather = self.game.weather
            else:
                return 0.0

        if hasattr(weather, 'current_multiplier'):
            weather_multiplier = weather.current_multiplier
            return (1.0 - weather_multiplier) * 5.0 if weather_multiplier < 1.0 else 0.0

        return 0.0

    def is_valid_move(self, character, move):
        """Check if move is valid."""
        if not self.game or not hasattr(self.game, 'mapa'):
            return True

        new_x = character.tile_x + move[0]
        new_y = character.tile_y + move[1]

        if new_y < 0 or new_y >= self.game.mapa.height:
            return False
        if new_x < 0 or new_x >= self.game.mapa.width:
            return False

        return not self.game.mapa.is_blocked(new_x, new_y)

    def change_dificulty(self, new_dificulty):
        self.dificulty = new_dificulty
