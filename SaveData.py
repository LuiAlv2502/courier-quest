import pickle
import os
from datetime import datetime
from typing import Dict, Any, Optional

class SaveData:
    def __init__(self, save_directory: str = "json_files"):
        """
        Inicializa el sistema de guardado
        
        Args:
            save_directory: Directorio donde se guardarán los archivos de guardado
        """
        self.save_directory = save_directory
        self.current_slot = None
        
        # Crear directorio de guardado si no existe
        if not os.path.exists(save_directory):
            os.makedirs(save_directory)
    
    def save_game(self, game_state: Dict[str, Any], slot_number: int = 1) -> bool:
        """
        Guarda el estado del juego en un slot específico
        
        Args:
            game_state: Diccionario con todo el estado del juego
            slot_number: Número del slot de guardado (1-10)
            
        Returns:
            bool: True si se guardó correctamente, False en caso de error
        """
        try:
            # Añadir metadata al guardado
            save_data = {
                "timestamp": datetime.now().isoformat(),
                "slot": slot_number,
                "version": "1.0",
                "game_state": game_state
            }
            
            filename = f"slot{slot_number}.sav"
            filepath = os.path.join(self.save_directory, filename)
            
            with open(filepath, 'wb') as file:
                pickle.dump(save_data, file)
            
            self.current_slot = slot_number
            print(f"Juego guardado en slot {slot_number}")
            return True
            
        except Exception as e:
            print(f"Error al guardar el juego: {e}")
            return False
    
    def load_game(self, slot_number: int = 1) -> Optional[Dict[str, Any]]:
        """
        Carga el estado del juego desde un slot específico
        
        Args:
            slot_number: Número del slot a cargar
            
        Returns:
            Dict con el estado del juego o None si no se pudo cargar
        """
        try:
            filename = f"slot{slot_number}.sav"
            filepath = os.path.join(self.save_directory, filename)
            
            if not os.path.exists(filepath):
                print(f"No existe guardado en slot {slot_number}")
                return None
            
            with open(filepath, 'rb') as file:
                save_data = pickle.load(file)
            
            self.current_slot = slot_number
            print(f"Juego cargado desde slot {slot_number}")
            return save_data["game_state"]
            
        except Exception as e:
            print(f"Error al cargar el juego: {e}")
            return None
    
    def delete_save(self, slot_number: int) -> bool:
        """
        Elimina un archivo de guardado
        
        Args:
            slot_number: Número del slot a eliminar
            
        Returns:
            bool: True si se eliminó correctamente
        """
        try:
            filename = f"slot{slot_number}.sav"
            filepath = os.path.join(self.save_directory, filename)
            
            if os.path.exists(filepath):
                os.remove(filepath)
                print(f"Guardado slot {slot_number} eliminado")
                return True
            else:
                print(f"No existe guardado en slot {slot_number}")
                return False
                
        except Exception as e:
            print(f"Error al eliminar guardado: {e}")
            return False
    
    def get_save_info(self, slot_number: int) -> Optional[Dict[str, Any]]:
        """
        Obtiene información básica de un guardado sin cargarlo completamente
        
        Args:
            slot_number: Número del slot
            
        Returns:
            Dict con información del guardado o None
        """
        try:
            filename = f"slot{slot_number}.sav"
            filepath = os.path.join(self.save_directory, filename)
            
            if not os.path.exists(filepath):
                return None
            
            with open(filepath, 'rb') as file:
                save_data = pickle.load(file)
            
            return {
                "slot": save_data["slot"],
                "timestamp": save_data["timestamp"],
                "version": save_data.get("version", "1.0"),
                "exists": True,
                "file_size": os.path.getsize(filepath)
            }
            
        except Exception as e:
            print(f"Error al obtener info del guardado: {e}")
            return None
    
    def list_saves(self) -> Dict[int, Dict[str, Any]]:
        """
        Lista todos los guardados disponibles
        
        Returns:
            Dict con información de todos los slots
        """
        saves = {}
        
        for slot in range(1, 11):  # Slots 1-10
            info = self.get_save_info(slot)
            if info:
                saves[slot] = info
        
        return saves
    
    def create_game_state(self, character_data: Dict, game_data: Dict, 
                         inventory_data: Dict, job_data: Dict, 
                         map_data: Dict, weather_data: Dict) -> Dict[str, Any]:
        """
        Crea un diccionario con el estado completo del juego
        
        Args:
            character_data: Datos del personaje (posición, stats, etc.)
            game_data: Datos generales del juego (nivel, puntuación, tiempo)
            inventory_data: Inventario del jugador
            job_data: Estado de los trabajos/misiones
            map_data: Estado del mapa
            weather_data: Estado del clima
            
        Returns:
            Dict con el estado completo del juego
        """
        return {
            "character": character_data,
            "game": game_data,
            "inventory": inventory_data,
            "jobs": job_data,
            "map": map_data,
            "weather": weather_data
        }
    
    def extract_game_components(self, game_state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extrae los componentes del estado del juego para facilitar la restauración
        
        Args:
            game_state: Estado del juego cargado
            
        Returns:
            Dict con los componentes separados
        """
        return {
            "character": game_state.get("character", {}),
            "ai_character": game_state.get("ai_character", {}),
            "game": game_state.get("game", {}),
            "inventory": game_state.get("inventory", {}),
            "ai_inventory": game_state.get("ai_inventory", {}),
            "jobs": game_state.get("jobs", {}),
            "map": game_state.get("map", {}),
            "weather": game_state.get("weather", {})
        }
    
    def auto_save(self, game_state: Dict[str, Any]) -> bool:
        """
        Guardado automático en slot especial (slot 0)
        
        Args:
            game_state: Estado del juego a guardar
            
        Returns:
            bool: True si se guardó correctamente
        """
        return self.save_game(game_state, slot_number=0)
    
    def load_auto_save(self) -> Optional[Dict[str, Any]]:
        """
        Carga el guardado automático
        
        Returns:
            Estado del juego o None
        """
        return self.load_game(slot_number=0)