
import os
import sys
import pygame
import constants
from game import CourierQuestGame
from main_menu import MainMenu

def main():
    # Cambiar al directorio donde está el script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    # Inicializar Pygame
    pygame.init()
    screen = pygame.display.set_mode((constants.WIDTH_SCREEN, constants.HEIGHT_SCREEN))
    pygame.display.set_caption("Courier Quest")
    
    while True:
        # Mostrar menú principal
        menu = MainMenu(screen)
        action = menu.run()
        
        if action == "exit":
            break
        elif action == "new_game":
            # Iniciar nueva partida
            game = CourierQuestGame()
            game.run()
        elif action == "load_game":
            # Cargar la partida única
            game = CourierQuestGame()
            if game.load_game(slot_number=1):
                game.run()
            else:
                print("No se pudo cargar la partida")
                # Volver al menú principal
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()