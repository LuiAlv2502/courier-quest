
import pygame
import json
import sys
import constants

class Mapa:
    def __init__(self, archivo_json, tile_size=20):
        self.tile_size = tile_size
        self.tiles = []
        self.legend = {}
        self.width = 0
        self.height = 0

        # Colores por defecto
        self.colors = {
            "C": (200, 200, 200),  # Calles
            "B": (100, 50, 50),    # Edificios
            "P": (50, 200, 50)     # Parques
        }

        # Cargar datos
        self.cargar_desde_json(archivo_json)

    def cargar_desde_json(self, archivo_json):
        try:
            with open(archivo_json, "r", encoding="utf-8") as f:
                data = json.load(f)["data"]
        except Exception as e:
            print("Error al leer el archivo JSON:", e)
            sys.exit()

        self.tiles = data["tiles"]
        self.legend = data["legend"]
        self.width = data["width"]
        self.height = data["height"]

    def dibujar(self, screen):
        for y, row in enumerate(self.tiles):
            for x, tile in enumerate(row):
                color = self.colors.get(tile, (0, 0, 0))  # negro si no está definido
                rect = pygame.Rect(
                    x * self.tile_size,
                    y * self.tile_size,
                    self.tile_size,
                    self.tile_size
                )
                pygame.draw.rect(screen, color, rect)
