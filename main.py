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
    pygame.font.init()  # Asegura que el módulo de fuentes esté inicializado
    print("[DEBUG] pygame y pygame.font inicializados correctamente")
    screen = pygame.display.set_mode((constants.WIDTH_SCREEN, constants.HEIGHT_SCREEN))
    pygame.display.set_caption("Courier Quest")
    
    while True:
        menu = MainMenu(screen)
        action = menu.run()
        if action == "exit":
            break
        elif action == "new_game":
            game = CourierQuestGame()
            game.run()
        elif action == "load_game":
            # Cargar la partida única
            from SaveData import SaveData
            save_system = SaveData()
            game_state = save_system.load_game(slot_number=1)
            if game_state:
                game = CourierQuestGame(load_saved_game=True, saved_game_state=game_state)
                game.run()
            else:
                print("No se pudo cargar la partida")
                # Volver al menú principal
    # Solo se llama a pygame.quit() y sys.exit() después de salir del bucle
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()