import os
import sys
import pygame
import constants
from main_menu import MainMenu
from CourierQuestGame import CourierQuestGame

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    # Inicializar pygame para poder usar UI y fuentes desde el menú
    pygame.init()

    screen = pygame.display.set_mode((constants.WIDTH_SCREEN, constants.HEIGHT_SCREEN))
    pygame.display.set_caption("Courier Quest")
    
    while True:
        menu = MainMenu(screen)
        action = menu.run()
        if action == "exit":
            break
        elif action == "new_game":
            # Mostrar selector de dificultad antes de crear la partida
            from UI import UI
            ui = UI(screen)
            difficulty = ui.run_difficulty_selector(initial='medium')
            if difficulty is None:
                # Si el jugador cancela, usar 'medium' por defecto
                difficulty = 'medium'
            game = CourierQuestGame(ai_difficulty=difficulty)
            game.run()
        elif action == "load_game":
            # Cargar la partida única
            from SaveData import SaveData
            save_system = SaveData()
            game_state = save_system.load_game(slot_number=1)
            if game_state:
                # Para partidas cargadas, usar dificultad por defecto (medium) o la que quiera establecerse en el futuro
                game = CourierQuestGame(load_saved_game=True, saved_game_state=game_state, ai_difficulty='medium')
                game.run()
            else:
                print("No se pudo cargar la partida")
                # Volver al menú principal
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()