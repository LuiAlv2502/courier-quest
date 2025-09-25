import json, time, random

class Weather:
    def __init__(self, file):
        with open(file, 'r') as f:
            data = json.load(f)["data"]
        
        self.city = data["city"]
        self.conditions = data["conditions"]
        self.transition = data["transition"]

        self.multipliers= {
            "clear": 1.0,
            "clouds": 0.98,
            "rain_light": 0.9,
            "rain" : 0.85,
            "storm": 0.75,
            "fog":0.88,
            "wind": 0.92,
            "heat": 0.90,
            "cold": 0.92
        }

        self.current_condition = data["initial"]["condition"]
        self.current_multiplier = self.multipliers[self.current_condition]
        self.intensity = data["initial"]["intensity"]

        self.burst_time = random.randint(45, 60)
        self.transitioning = False
        self.transition_duration = 0
        self.transition_time = 0
        self.target_condition = None
        self.target_multiplier = None

    def _next_condition(self):
        probs = self.transition[self.current_condition]
        return random.choices(
            population=list(probs.keys()),
            weights=list(probs.values())
        )[0]

    def _generate_intensity(self):
        return random.uniform(0.0, 1.0)

    def _interpolate(self, start, end, t, duration):
        alpha = min(1.0, t / duration)
        return (1 - alpha) * start + alpha * end

    def update(self, delta_time):
        #delta_time: tiempo transcurrido en segundos desde el último update
        

        if not self.transitioning:
            self.burst_time -= delta_time
            if self.burst_time <= 0:
                # elige el siguiente clima
                self.target_condition = self._next_condition()
                self.intensity = self._generate_intensity()
                self.target_multiplier = (
                    self.multipliers[self.target_condition] *
                    (0.8 + 0.2 * self.intensity)
                )

                # preparar transición
                self.transition_duration = random.uniform(3, 5)
                self.transition_time = 0
                self.transitioning = True
        else:
            # proceso de transición
            self.transition_time += delta_time
            self.current_multiplier = self._interpolate(
                self.multipliers[self.current_condition],
                self.target_multiplier,
                self.transition_time,
                self.transition_duration
            )

            if self.transition_time >= self.transition_duration:
                # finaliza transición
                self.current_condition = self.target_condition
                self.current_multiplier = self.target_multiplier
                self.burst_time = random.randint(45, 60)
                self.transitioning = False

    def get_status(self):
        #retorna el estado actual del clima
        return {
            "condition": self.current_condition,
            "multiplier": self.current_multiplier,
            "intensity": self.intensity,
            "burst_time": self.burst_time,
            "transitioning": self.transitioning
        }