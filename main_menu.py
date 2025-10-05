import pygame
import constants
from SaveData import SaveData

class MainMenu:
    def __init__(self, screen):
        self.screen = screen
        self.save_system = SaveData()
        if not pygame.font.get_init():
            pygame.font.init()
        self.font_title = pygame.font.SysFont(None, 48)
        self.font_menu = pygame.font.SysFont(None, 32)
        self.font_info = pygame.font.SysFont(None, 24)
        
        # Verificar si existe un guardado
        has_save = self.save_system.get_save_info(1) is not None
        self.has_save = has_save
        
        # Cargar imagen de fondo del HUD para el menú
        try:
            self.hud_img = pygame.image.load("sprites/hud.png").convert_alpha()
            # Usar el tamaño original de la imagen
            self.menu_width = self.hud_img.get_width()
            self.menu_height = self.hud_img.get_height()
        except:
            self.hud_img = None
            self.menu_width = 400
            self.menu_height = 300
    
    def draw(self):
        """Dibuja el menú principal"""
        # Fondo negro
        self.screen.fill((0, 0, 0))
        
        # Centrar el menú en la pantalla
        menu_x = (constants.WIDTH_SCREEN - self.menu_width) // 2
        menu_y = (constants.HEIGHT_SCREEN - self.menu_height) // 2

        # Título del juego
        title_text = self.font_title.render("COURIER QUEST", True, (255, 255, 0))
        title_rect = title_text.get_rect(center=(constants.WIDTH_SCREEN // 2, menu_y + 60))
        self.screen.blit(title_text, title_rect)
        
        # Opciones del menú con teclas
        base_y = menu_y + 120
        
        # Nueva Partida
        new_game_text = self.font_menu.render("[N] Nueva Partida", True, (255, 255, 255))
        new_game_rect = new_game_text.get_rect(center=(constants.WIDTH_SCREEN // 2, base_y))
        self.screen.blit(new_game_text, new_game_rect)
        
        # Continuar Partida (solo si existe guardado)
        if self.has_save:
            continue_text = self.font_menu.render("[C] Continuar Partida", True, (255, 255, 255))
            continue_rect = continue_text.get_rect(center=(constants.WIDTH_SCREEN // 2, base_y + 50))
            self.screen.blit(continue_text, continue_rect)
            salir_y = base_y + 100
        else:
            salir_y = base_y + 50
        
        # Salir
        exit_text = self.font_menu.render("[S] Salir", True, (255, 255, 255))
        exit_rect = exit_text.get_rect(center=(constants.WIDTH_SCREEN // 2, salir_y))
        self.screen.blit(exit_text, exit_rect)
        
        pygame.display.flip()
    
    def handle_input(self, event):
        """Maneja la entrada del usuario en el menú"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_n:  # Nueva Partida
                return "new_game"
            elif event.key == pygame.K_c and self.has_save:  # Continuar Partida
                return "load_game"
            elif event.key == pygame.K_s:  # Salir
                return "exit"
            elif event.key == pygame.K_ESCAPE:  # También ESC para salir
                return "exit"
        
        return None
    
    def run(self):
        """Ejecuta el bucle principal del menú"""
        clock = pygame.time.Clock()
        running = True
        
        while running:
            try:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        return "exit"

                    action = self.handle_input(event)
                    if action:
                        return action

                self.draw()
                clock.tick(60)
            except pygame.error as e:
                print(f"[ERROR] {e}")
                return "exit"
