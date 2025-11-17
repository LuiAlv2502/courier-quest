import random
import time
import heapq
import networkx as nx
import inventory


class AIController:
    def __init__(self, dificulty="easy", game=None):
        self.dificulty = dificulty
        self.game = game
        # Horizonte de anticipación pequeño (2-3 acciones por delante)
        # Depth 2 significa: evalúa tu movimiento -> posibles eventos aleatorios -> tu próximo movimiento
        self.max_depth = 2  # Limited horizon: 2-3 actions ahead
        self.last_move_time = 0  # Track when the last move was made
        self.move_delay = 0.5  # 0.5 seconds delay between moves

        # Loop detection
        self.position_history = []  # Track recent positions
        self.max_history = 8  # Keep track of last 8 positions
        self.loop_detected = False
        self.loop_break_moves = 0  # Counter for how many moves to break loop

        # Dijkstra pathfinding state (hard difficulty) usando NetworkX
        self.current_path = []  # Lista de movimientos (dx, dy) a seguir
        self.current_target = None  # Objetivo actual (x, y)
        self.city_graph = None  # Grafo de la ciudad (NetworkX Graph)
        self.graph_needs_update = True  # Flag para actualizar el grafo

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
        elif self.dificulty == "hard":
            return self.dijkstra_move(character, weather, inventory)
        return (0, 0)

    def random_move(self, character):
        directions = [(0, -1), (0, 1), (-1, 0), (1, 0)]  # up, down, left, right
        return random.choice(directions)

    def expectimax_move(self, character, weather=None, inventory=None):
        """
        Medium difficulty: Expectimax con horizonte limitado (2-3 acciones adelante).

        EXPECTIMAX es un algoritmo de decisión que:
        1. Asume que TÚ maximizas tu puntuación (nodos MAX)
        2. Asume que eventos ALEATORIOS (clima, otros jugadores) no son adversarios,
           sino que tienen resultados probabilísticos (nodos CHANCE)

        Diferencia con MINIMAX:
        - MINIMAX: Asume un oponente inteligente que te quiere hacer perder
        - EXPECTIMAX: Asume eventos aleatorios con probabilidades uniformes
        """
        if character.resistencia_exhausto:
            return (0, 0)

        # Check if AI has any jobs to work on
        char_inventory = inventory if inventory is not None else getattr(character, 'inventory', None)
        has_jobs = False

        # Check for picked up jobs (ready for delivery)
        picked_jobs = char_inventory.get_picked_jobs()
        if picked_jobs:
            has_jobs = True

        # Check for accepted but not picked up jobs
        all_jobs = char_inventory.get_jobs()
        for job in all_jobs:
            if not job.is_picked_up():
                has_jobs = True
                break

        # If no jobs available, stay still
        if not has_jobs:
            return (0, 0)

        current_pos = (character.tile_x, character.tile_y)

        # Update position history (para detectar bucles infinitos)
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

        # Ejecutar el algoritmo Expectimax y obtener el mejor movimiento
        _, best_move = self.expectimax(character, self.max_depth, True, weather, inventory)

        # If expectimax returns None or invalid move, use random valid move
        if not best_move or not self.is_valid_move(character, best_move):
            directions = [(0, -1), (0, 1), (-1, 0), (1, 0)]
            valid_directions = [move for move in directions if self.is_valid_move(character, move)]
            if valid_directions:
                return random.choice(valid_directions)

        return best_move if best_move else (0, 0)

    def expectimax(self, character, depth, is_max_node, weather=None, inventory=None):
        """
        Algoritmo Expectimax recursivo.

        ESTRUCTURA DEL ÁRBOL:
        - Nivel 1: Nodo MAX (tu turno) - Eliges el mejor movimiento
        - Nivel 2: Nodo CHANCE (eventos aleatorios) - Calcula el promedio de todos los resultados posibles
        - Nivel 3: Nodo MAX (tu turno otra vez) - Eliges el mejor movimiento
        - ...y así hasta depth = 0

        EJEMPLO:
        Si depth = 2:
        1. Evalúas tus 4 movimientos posibles (arriba, abajo, izq, der)
        2. Para cada movimiento, calculas el PROMEDIO de los posibles eventos aleatorios
        3. Eliges el movimiento con el MEJOR valor esperado

        Args:
            character: El personaje AI
            depth: Qué tan profundo explorar (0 = evaluar inmediatamente)
            is_max_node: True si es tu turno (MAX), False si es chance node (eventos aleatorios)
            weather: Estado del clima
            inventory: Inventario del personaje

        Returns:
            (score, move): La puntuación esperada y el mejor movimiento
        """
        # Caso base: Si llegamos a depth 0, evaluamos el estado actual
        if depth == 0:
            return self.evaluate_state(character, weather, inventory), None

        moves = [(0, -1), (0, 1), (-1, 0), (1, 0)]  # up, down, left, right

        if is_max_node:  # NODO MAX: Tu turno - MAXIMIZA la puntuación
            best_score = float('-inf')
            best_move = None

            # Evalúa cada movimiento posible
            for move in moves:
                if self.is_valid_move(character, move):
                    # Simula el movimiento creando un personaje temporal en la nueva posición
                    temp_character = type('obj', (object,), {
                        'tile_x': character.tile_x + move[0],
                        'tile_y': character.tile_y + move[1],
                        'resistencia': character.resistencia,
                        'resistencia_exhausto': character.resistencia_exhausto,
                        'inventory': getattr(character, 'inventory', None)
                    })()

                    # Si estamos en el último nivel, evalúa directamente
                    if depth == 1:
                        score = self.evaluate_state(temp_character, weather, inventory)
                    else:
                        # Si no, recursivamente explora el siguiente nivel (CHANCE node)
                        score, _ = self.expectimax(temp_character, depth - 1, False, weather, inventory)

                    # Quedarse con el MEJOR movimiento (maximizar)
                    if score > best_score:
                        best_score = score
                        best_move = move

            return best_score, best_move

        else:  # NODO CHANCE: Eventos aleatorios - Calcula el VALOR ESPERADO (promedio)
            """
            En un nodo CHANCE, no sabemos qué va a pasar exactamente.
            Por ejemplo: el clima puede cambiar, otros jugadores pueden moverse, etc.
            
            Por simplicidad, asumimos que todos los movimientos son EQUIPROBABLES
            (tienen la misma probabilidad de ocurrir).
            
            Calculamos el VALOR ESPERADO = PROMEDIO de todas las puntuaciones posibles
            """
            total_score = 0.0
            count = 0

            # Suma las puntuaciones de todos los posibles resultados
            for move in moves:
                if self.is_valid_move(character, move):
                    # Simula un posible resultado aleatorio
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
                        # El siguiente nivel es un MAX node (tu turno otra vez)
                        score, _ = self.expectimax(temp_character, depth - 1, True, weather, inventory)

                    total_score += score
                    count += 1

            # Retorna el PROMEDIO (valor esperado)
            return total_score / count if count > 0 else 0, None


    def evaluate_state(self, character, weather=None, inventory=None):
        """
        Función de puntuación simple para evaluar qué tan bueno es un estado.

        FÓRMULA:
        score = α*(expected_payout) - β*(distance_cost) - γ*(weather_penalty)

        Donde:
        - α = 2.0: Peso del pago esperado (¡queremos ganar dinero!)
        - β = 1.0: Peso del costo de distancia (evitar movimientos costosos)
        - γ = 1.5: Peso de la penalización del clima (evitar mal clima)

        Un score ALTO significa que este estado es BUENO.
        Un score BAJO significa que este estado es MALO.
        """
        α, β, γ = 2.0, 1.0, 1.5

        # Calcula cada componente de la función de puntuación

        # α*(expected_payout): ¿Cuánto dinero puedo ganar desde aquí?
        expected_payout = self.calculate_payout(character, inventory)

        # β*(distance_cost): ¿Qué tan costoso es moverme? (stamina, peso, clima)
        distance_cost = self.calculate_distance_cost(character, weather, inventory)

        # γ*(weather_penalty): ¿Qué tan malo es el clima?
        weather_penalty = self.calculate_weather_penalty(weather)

        # Puntuación final: maximiza ganancias, minimiza costos
        return α * expected_payout - β * distance_cost - γ * weather_penalty

    def calculate_payout(self, character, inventory=None):
        """
        Calcula el pago esperado basado en:
        1. Trabajos ya recogidos (listos para entregar) - MÁS valor si están cerca del dropoff
        2. Trabajos aceptados pero no recogidos - valor si están cerca del pickup
        3. Trabajos visibles disponibles - oportunidades nuevas

        Usa la fórmula: payout / (distance + 1) * weight
        - Divide entre distancia para priorizar trabajos cercanos
        - Multiplica por peso según tipo y distancia
        """


        payout = 0.0

        # Use passed inventory or character's inventory
        char_inventory = inventory if inventory is not None else character.inventory

        # Check picked up jobs (ready for delivery) using get_picked_jobs()
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
        visible_jobs = self.game.job_manager.visible_jobs

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
        """
        Calcula el COSTO de movimiento basado en:
        1. Stamina baja (penalización si resistencia < 30)
        2. Peso del inventario (más peso = más costoso moverse)
        3. Clima malo (lluvia/tormenta = más costoso moverse)

        NOTA: La distancia a los trabajos ya se considera en calculate_payout()
        usando la fórmula payout / (distance + 1), que premia estar cerca.
        """
        cost = 0.0

        # Use passed inventory or character's inventory
        char_inventory = inventory

        # Stamina penalty (low stamina = high cost to move)
        if character.resistencia < 30:
            cost += 10.0

        # Weight penalty from inventory (more weight = harder to move)
        total_weight = char_inventory.get_current_weight()
        cost += total_weight * 0.5  # Weight increases movement cost

        # Weather movement penalty (bad weather = harder to move)
        weather_mult = weather.current_multiplier
        if weather_mult < 1.0:
            # Bad weather increases movement cost
            cost += (1.0 - weather_mult) * 3.0

        return cost

    def calculate_weather_penalty(self, weather=None):
        """
        Penalización por mal clima.
        Si weather_multiplier < 1.0 (mal clima), añade penalización.
        """
        if not weather:
            # Try to get weather from game if not passed
            weather = self.game.weather

        weather_multiplier = weather.current_multiplier
        return (1.0 - weather_multiplier) * 5.0 if weather_multiplier < 1.0 else 0.0



    def is_valid_move(self, character, move):
        """Check if move is valid."""

        new_x = character.tile_x + move[0]
        new_y = character.tile_y + move[1]

        if new_y < 0 or new_y >= self.game.mapa.height:
            return False
        if new_x < 0 or new_x >= self.game.mapa.width:
            return False

        return not self.game.mapa.is_blocked(new_x, new_y)

    def change_dificulty(self, new_dificulty):
        self.dificulty = new_dificulty

    def dijkstra_move(self, character, weather=None, inventory=None):
        """
        Hard difficulty: Dijkstra con grafo ponderado usando NetworkX.

        ALGORITMO:
        1. Construye un grafo de la ciudad con NetworkX (nodos = tiles, aristas = conexiones)
        2. Peso de arista = costo de superficie + modificador de clima
        3. Usa nx.dijkstra_path() para encontrar el camino óptimo
        4. Optimiza secuencia: maximiza ganancia/costo, prioriza entregas
        """
        if character.resistencia_exhausto:
            return (0, 0)

        char_inventory = inventory

        # Construir/actualizar el grafo de la ciudad si es necesario
        if self.city_graph is None or self.graph_needs_update:
            self.build_city_graph(weather)
            self.graph_needs_update = False

        # Si ya tenemos un camino válido, seguirlo
        if self.current_path and self.current_target:
            current_pos = (character.tile_x, character.tile_y)
            # Verificar si llegamos al objetivo
            if current_pos == self.current_target:
                self.current_path = []
                self.current_target = None
            elif self.current_path:
                next_move = self.current_path.pop(0)
                if self.is_valid_move(character, next_move):
                    return next_move
                else:
                    # Camino bloqueado, replanificar
                    self.current_path = []
                    self.current_target = None

        # Recolectar trabajos disponibles
        job_targets = self.collect_job_targets(char_inventory)

        if not job_targets:
            return (0, 0)

        # Elegir el mejor trabajo usando lógica de decisión
        best_target = self.choose_best_job(character, job_targets, weather)

        if not best_target:
            return (0, 0)

        # Calcular camino óptimo usando NetworkX Dijkstra
        start = (character.tile_x, character.tile_y)
        goal = best_target['position']

        try:
            # nx.dijkstra_path encuentra el camino de menor costo
            path = nx.dijkstra_path(self.city_graph, start, goal, weight='weight')

            if len(path) < 2:
                return (0, 0)

            # Guardar objetivo y convertir path a movimientos
            self.current_target = goal
            self.current_path = self.path_to_moves(path)

            # Ejecutar primer movimiento
            if self.current_path:
                next_move = self.current_path.pop(0)
                if self.is_valid_move(character, next_move):
                    return next_move

        except (nx.NetworkXNoPath, nx.NodeNotFound):
            # No hay camino válido al objetivo
            return (0, 0)

        return (0, 0)

    def build_city_graph(self, weather):
        """
        Construye un GRAFO PONDERADO de la ciudad usando NetworkX.

        REPRESENTACIÓN:
        - Cada tile accesible = NODO
        - Cada tile bloqueado ADYACENTE a tiles accesibles = NODO (para entregas)
        - Cada conexión entre tiles adyacentes = ARISTA
        - Peso de arista = costo de superficie + modificador de clima

        Usa nx.DiGraph() para grafo dirigido (aunque en este caso es simétrico)
        """

        mapa = self.game.mapa
        # Crear grafo dirigido
        self.city_graph = nx.DiGraph()

        # PASO 1: Agregar todos los tiles accesibles (NO bloqueados) como nodos
        for y in range(mapa.height):
            for x in range(mapa.width):
                if not mapa.is_blocked(x, y):
                    self.city_graph.add_node((x, y))

        # PASO 2: Agregar tiles bloqueados ADYACENTES a tiles accesibles
        tiles_to_add = set()
        for y in range(mapa.height):
            for x in range(mapa.width):
                if not mapa.is_blocked(x, y):
                    # Este tile es accesible, revisar sus vecinos bloqueados
                    for dx, dy in [(0, -1), (0, 1), (-1, 0), (1, 0)]:
                        neighbor_x, neighbor_y = x + dx, y + dy

                        # Verificar que el vecino está dentro del mapa
                        if (0 <= neighbor_x < mapa.width and
                            0 <= neighbor_y < mapa.height and
                            mapa.is_blocked(neighbor_x, neighbor_y)):
                            # Vecino bloqueado adyacente a tile accesible
                            tiles_to_add.add((neighbor_x, neighbor_y))

        # Agregar los tiles bloqueados adyacentes al grafo
        for tile in tiles_to_add:
            self.city_graph.add_node(tile)

        # PASO 3: Conectar tiles adyacentes con aristas ponderadas
        for y in range(mapa.height):
            for x in range(mapa.width):
                # Solo crear aristas desde nodos que están en el grafo
                if (x, y) in self.city_graph:
                    # Explorar 4 vecinos (arriba, abajo, izq, der)
                    for dx, dy in [(0, -1), (0, 1), (-1, 0), (1, 0)]:
                        neighbor_x, neighbor_y = x + dx, y + dy

                        # Verificar que el vecino está en el grafo
                        if (neighbor_x, neighbor_y) in self.city_graph:
                            # Verificar si el tile destino está bloqueado
                            if mapa.is_blocked(neighbor_x, neighbor_y):
                                # Si el tile está bloqueado, el camino hacia él tiene peso 10
                                edge_weight = 10.0
                            else:
                                # Calcular peso normal de la arista
                                edge_weight = self.get_tile_cost(neighbor_x, neighbor_y, weather)

                            # Agregar arista con peso
                            self.city_graph.add_edge((x, y), (neighbor_x, neighbor_y), weight=edge_weight)

    def get_tile_cost(self, x, y, weather):
        """
        Calcula el COSTO de moverse a un tile.

        Costo = peso_superficie + modificador_clima
        """

        mapa = self.game.mapa
        base_cost = 1.0

        # Obtener costo de superficie si está disponible
        base_cost = mapa.get_surface_weight(x, y)

        # Agregar modificador de clima
        weather_modifier = 0.0
        weather_mult = weather.current_multiplier
        if weather_mult < 1.0:
            # Mal clima aumenta el costo
            weather_modifier = (1.0 - weather_mult) * 2.0

        return base_cost + weather_modifier

    def collect_job_targets(self, inventory):
        """
        Recolecta todos los trabajos disponibles con prioridades.

        Usa los métodos de la clase Inventory:
        - get_picked_jobs(): trabajos recogidos (listos para entregar)
        - get_jobs(): todos los trabajos aceptados

        Returns: Lista de dicts con position, type, payout, priority
        """
        targets = []

        if not inventory:
            return targets

        # PRIORIDAD 3: Trabajos recogidos (ENTREGAS) - usar get_picked_jobs()
        picked_jobs = inventory.get_picked_jobs()
        for job in picked_jobs:
            targets.append({
                'position': job.dropoff,
                'type': 'delivery',
                'payout': job.payout,
                'priority': 1,
                'job': job
            })

        # PRIORIDAD 2: Trabajos aceptados pero NO recogidos (PICKUPS) - usar get_jobs()
        all_jobs = inventory.get_jobs()
        for job in all_jobs:
            if not job.is_picked_up():
                targets.append({
                    'position': job.pickup,
                    'type': 'pickup',
                    'payout': job.payout,
                    'priority': 2,
                    'job': job
                })



        return targets

    def choose_best_job(self, character, job_targets, weather):
        """
        LÓGICA DE DECISIÓN: Elige trabajo que maximiza ganancia/costo.

        Criterios:
        1. Minimiza desplazamientos (usa costo real de NetworkX Dijkstra)
        2. Maximiza ganancias
        3. Prioriza entregas > pickups > oportunidades

        Métrica: score = (payout * priority) / (costo_camino + 1)
        """
        if not job_targets or not self.city_graph:
            return None

        start = (character.tile_x, character.tile_y)
        best_target = None
        best_score = float('-inf')

        for target in job_targets:
            goal = target['position']

            try:
                # Calcular costo real usando NetworkX Dijkstra
                path_cost = nx.dijkstra_path_length(self.city_graph, start, goal, weight='weight')

                # Calcular score: maximiza (ganancia * prioridad) / costo
                payout = target['payout']
                priority = target['priority']
                score = (payout * priority) / (path_cost + 1)

                if score > best_score:
                    best_score = score
                    best_target = target

            except (nx.NetworkXNoPath, nx.NodeNotFound):
                # No hay camino a este trabajo, ignorar
                continue

        return best_target

    def path_to_moves(self, path):
        """
        Convierte lista de posiciones [(x1,y1), (x2,y2), ...] a movimientos [(dx,dy), ...]
        """
        moves = []
        for i in range(len(path) - 1):
            x1, y1 = path[i]
            x2, y2 = path[i + 1]
            moves.append((x2 - x1, y2 - y1))
        return moves
