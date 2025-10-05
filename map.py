import pygame
import json
import sys
import constants
import os

class Map:
    def __init__(self, archivo_json, tile_size, hud_height = 60, top_bar_height = 40):
        self.tile_size = tile_size
        self.tiles = []
        self.legend = {}
        self.width = 0
        self.height = 0
        self.top_bar_height = top_bar_height
        self.hud_height = hud_height

        # Colores por defecto
        self.colors = {
            "C": (200, 200, 200),  # Calles
            "B": (100, 50, 50),    # Edificios
            "P": (50, 200, 50)     # Parques
        }

        # Cargar sprites de edificios
        self.building_sprites = self.load_building_sprites()

        # Cargar datos
        self.cargar_desde_json(archivo_json)

    def load_building_sprites(self):
        """Carga todos los sprites de edificios desde la carpeta sprites/buildings/"""
        sprites = {}
        building_path = "sprites/buildings"

        if not os.path.exists(building_path):
            print(f"Warning: Building sprites folder not found: {building_path}")
            return sprites

        sprite_files = {
            "top_left": "top_left_edge.png",
            "top_right": "top_right_edge.png",
            "bottom_left": "bottom_left_edge.png",
            "bottom_right": "bottom_right_edge.png",
            "left_border": "left_border.png",
            "right_border": "right_border.png",
            "bottom_border": "bottom_border.png",
            "center": "center.png"
        }

        for sprite_type, filename in sprite_files.items():
            sprite_path = os.path.join(building_path, filename)
            if os.path.exists(sprite_path):
                try:
                    sprite = pygame.image.load(sprite_path).convert_alpha()
                    sprites[sprite_type] = pygame.transform.scale(sprite, (self.tile_size, self.tile_size))
                except Exception as e:
                    print(f"Error loading sprite {filename}: {e}")
            else:
                print(f"Sprite not found: {sprite_path}")

        return sprites

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

    # Dibuja el mapa completo recorriendo los tiles dados por el json y se colorea dependiendo de su tipo
    def draw_map(self, screen):
        for y, row in enumerate(self.tiles):
            for x, tile in enumerate(row):
                rect = pygame.Rect(
                    x * self.tile_size,
                    y * self.tile_size + self.top_bar_height,
                    self.tile_size,
                    self.tile_size
                )

                if tile == "B" and self.building_sprites:
                    # Usar sprites para edificios
                    sprite_type = self.get_building_sprite_type(x, y)
                    if sprite_type in self.building_sprites:
                        screen.blit(self.building_sprites[sprite_type], rect.topleft)
                    else:
                        # Fallback a color sólido si no hay sprite
                        color = self.colors.get(tile, (0, 0, 0))
                        pygame.draw.rect(screen, color, rect)
                else:
                    # Usar colores sólidos para otros tipos de tiles
                    color = self.colors.get(tile, (0, 0, 0))  # negro si no está definido
                    pygame.draw.rect(screen, color, rect)

    def get_hud_bottom_y(self):
        # Devuelve la posición Y donde debe ir el HUD inferior
        return self.height * self.tile_size + self.top_bar_height

    def is_blocked(self, tile_x, tile_y):
        # fuera del mapa
        if tile_x < 0 or tile_x >= self.width or tile_y < 0 or tile_y >= self.height:
            return True
        tile = self.tiles[tile_y][tile_x]
        info = self.legend.get(tile, {})
        return info.get("blocked", False)
    
    def get_surface_weight(self, tile_x, tile_y):
        tile = self.tiles[tile_y][tile_x]
        info = self.legend.get(tile, {})
        return info.get("surface_weight", 1.0)

    def is_building(self, tile_x, tile_y):
        """Verifica si una posición específica es un edificio"""
        if tile_x < 0 or tile_x >= self.width or tile_y < 0 or tile_y >= self.height:
            return False
        return self.tiles[tile_y][tile_x] == "B"

    def get_building_sprite_type(self, tile_x, tile_y):
        """Determina qué tipo de sprite de edificio usar basado en los tiles vecinos"""
        if not self.is_building(tile_x, tile_y):
            return "center"  # fallback

        # Verificar vecinos en las 8 direcciones
        neighbors = {
            "top": self.is_building(tile_x, tile_y - 1),
            "bottom": self.is_building(tile_x, tile_y + 1),
            "left": self.is_building(tile_x - 1, tile_y),
            "right": self.is_building(tile_x + 1, tile_y),
            "top_left": self.is_building(tile_x - 1, tile_y - 1),
            "top_right": self.is_building(tile_x + 1, tile_y - 1),
            "bottom_left": self.is_building(tile_x - 1, tile_y + 1),
            "bottom_right": self.is_building(tile_x + 1, tile_y + 1)
        }

        # Determinar tipo de sprite basado en vecinos
        has_top = neighbors["top"]
        has_bottom = neighbors["bottom"]
        has_left = neighbors["left"]
        has_right = neighbors["right"]

        # Esquinas
        if not has_top and not has_left:
            return "top_left"
        elif not has_top and not has_right:
            return "top_right"
        elif not has_bottom and not has_left:
            return "bottom_left"
        elif not has_bottom and not has_right:
            return "bottom_right"

        # Bordes
        elif not has_left and (has_top or has_bottom):
            return "left_border"
        elif not has_right and (has_top or has_bottom):
            return "right_border"
        elif not has_bottom and (has_left or has_right):
            return "bottom_border"

        # Centro por defecto
        else:
            return "center"
