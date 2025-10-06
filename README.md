
# 🐎 Courier Quest - Estructuras y Algoritmos Principales 🧐
Este documento describe las estructuras de datos y algoritmos más importantes usados en el código fuente de **Courier Quest**.

---

### 📃 Requerimientos y cómo correrlo  
- **⚙️ Requerimientos:** Tener instalado `pygame` y `requests` para poder correr el juego.  
- **▶️ ¿Cómo correrlo?:** Abrir el archivo **main.py** y ejecutarlo con Python.

---

## 🎮 Controles del Juego  

### 🕹 Movimiento del Personaje  
- **Flechas direccionales (←↑↓→):** Mueve al personaje por el mapa  
- **Z:** Deshacer último movimiento  

### 🛠️ Gestión de Trabajos  
- **A:** Aceptar trabajo pendiente  
- **N:** Rechazar trabajo pendiente  

### 🎒 Inventario  
- **I:** Abrir/cerrar inventario de trabajos aceptados  
- **↑↓:** Navegar por los trabajos en el inventario  
- **D:** Ordenar trabajos por deadline (fecha límite)  
- **P:** Ordenar trabajos por prioridad  
- **C:** Cancelar trabajo seleccionado (-4 reputación)  

### ⏸️ Sistema de Pausa  
- **ESC:** Pausar el juego  
- **C:** Continuar partida  
- **G:** Guardar partida  
- **Q:** Salir del juego  

---

## 🧱 Stack (stack.py)
- **Propósito:** Historial de movimientos del jugador (deshacer movimientos).
- **Estructura:** Implementación clásica de pila (stack) con métodos push, pop, peek, is_empty.
- **Algoritmo:** LIFO (Last-In, First-Out) para almacenar y recuperar posiciones previas.

### Mecánicas Automáticas
- **Recoger trabajos:** Automático al estar en el punto de recogida o tile vecino
- **Entregar trabajos:** Automático al estar en el punto de entrega o tile vecino
- **Recuperación de resistencia:** Automática cuando el personaje está inmóvil

---

## 📦 Inventario (inventory.py)
- **Propósito:** Gestiona los trabajos aceptados y recogidos por el jugador con dos listas separadas.
- **Estructura:** 
  - `jobs[]`: Lista de todos los trabajos aceptados
  - `picked_jobs[]`: Lista de trabajos físicamente recogidos por el personaje
  - Sistema de peso máximo con validación
- **Algoritmos:**
  - **Heap Sort:** Para filtrar trabajos por prioridad usando `heapq` con prioridades negativas
  - **Insertion Sort:** Para ordenar trabajos por deadline (fecha límite)
  - **Búsqueda lineal:** Para cancelación de trabajos por ID
- **Funcionalidades:** Aceptar, recoger, entregar, cancelar trabajos, control de peso, detección de vecindad

---

## 🕰 JobManager (job_manager.py)
- **Propósito:** Controla la liberación temporal de trabajos disponibles usando cola de prioridad.
- **Estructura:** 
  - `job_priority_queue[]`: cola de prioridad para hacer release de trabajos basado en `release_time`
  - `visible_jobs[]`: Lista de trabajos disponibles para aceptar
- **Algoritmo:** 
  - **Priority Queue (Min-Heap):** Para liberar trabajos basado en `release_time`
  - **Búsqueda y filtrado:** Para eliminar trabajos por ID
- **Funcionalidades:** Liberación temporal automática, gestión de trabajos visibles

---

## 🧍 Character (character.py)
- **Propósito:** Representa al jugador con sistema complejo de reputación, resistencia y estadísticas.
- **Estructura:** 
  - Atributos de posición (tile_x, tile_y), estadísticas (reputación, resistencia, score)
  - Sistema de rachas y penalizaciones
  - Inventario integrado, sistema de movimiento con multiplicadores
- **Algoritmos:**
  - **Sistema de reputación:** Cálculos condicionales para bonos/penalizaciones
  - **Multiplicadores de velocidad:** Fórmula compleja basada en peso, clima, reputación
  - **Gestión de rachas:** Seguimiento de entregas consecutivas sin penalizaciones
- **Funcionalidades:** Movimiento inteligente, sistema de fatiga, bonificaciones por reputación alta (≥90)

---

## 🌐 API y Caché (api.py)
- **Propósito:** Sistema modular de descarga y caché de datos de la API con fallback offline.
- **Estructura:** 
  - Funciones especializadas: `save_api_data()`, `load_from_cache()`, `get_latest_cache_file()`
  - Archivos JSON en `json_files/` (principal) y `api_cache/` (con timestamp)
- **Algoritmos:**
  - **Ordenamiento por timestamp:** Para encontrar caché más reciente
  - **Fallback automático:** API → caché más reciente → error
  - **Timestamp con formato:** YYYYMMDD_HHMMSS para versionado de caché
- **Funcionalidades:** Descarga de 3 endpoints, caché automático, recuperación offline

---

## 🔄️ CourierQuestGame (CourierQuestGame.py)
- **Propósito:** Controlador principal del juego con gestión completa de estado y ciclo de vida.
- **Estructura:**
  - Variables de estado del juego (running, paused, show_inventory, selected_job_index)
  - Sistemas integrados: Map, Character, JobManager, UI, Weather, SaveData
  - Stack para deshacer movimientos
- **Algoritmos:**
  - **Event handling:** Procesamiento de eventos de teclado con estados múltiples
  - **State management:** Guardado/carga de estado completo del juego
  - **Game loop:** Actualización de lógica, rendering, detección win/loss
- **Funcionalidades:** Menú de pausa, sistema de guardado binario, navegación de inventario, gestión temporal

---

## 💻 UI (UI.py)
- **Propósito:** Gestiona toda la interfaz gráfica del jugador, incluyendo HUD, inventario, clima, menús y pantallas de fin de juego.
- **Estructura:**
  - Fuentes personalizadas para distintos textos y escalado de imágenes HUD.
  - Integración con Scoreboard para mostrar y guardar puntajes.
- **Algoritmos:**
  - Renderizado dinámico: Actualiza en tiempo real reputación, score, tiempo y clima.
  - Ordenamiento visual: Muestra trabajos ordenados por prioridad (Heap Sort) o deadline (Insertion Sort).
  - Gestión de eventos: Navegación con teclado en inventario y menús.
- **Funcionalidades:**
  - Topbar: Muestra puntuación y clima.
  - Downbar: Indica peso, reputación y tiempo restante.
  - Resistencia: Usa sprites escalados según estamina.
  - Inventario: Ventana emergente con trabajos ordenables y seleccionables.
  - Menús: Pausa, Game Over y Victoria con guardado y tabla de puntajes.
  - Mapa: Dibuja puntos de recogida (azul) y entrega (naranja).

---

## 🌦 Weather (Weather.py)
- **Propósito:** Controla el sistema climático dinámico del juego, afectando el entorno y el rendimiento del jugador.
- **Estructura:**
  - Carga configuraciones desde un archivo JSON con condiciones, transiciones y valores iniciales.
  - Define multiplicadores de rendimiento según el tipo de clima.
- **Algoritmos:**
  - Markov: El clima cambia según probabilidades de transición entre estados.
  - Interpolación lineal: Suaviza el paso entre condiciones (transiciones graduales).
- **Funcionalidades:**
  - Actualiza clima cada 45–60 segundos con intensidad aleatoria.
  - Aplica un multiplicador de rendimiento al jugador según la condición actual.
  - Gestiona transiciones progresivas entre climas (lluvia, sol, viento, etc.).
  - Devuelve el estado climático actual con intensidad y factor de impacto.

---

## ⚠️ Aclaración sobre las *deadlines* en el inventario y confusion de velocidad con stamina
- No se pudo hacer correctamente la representación de los *deadlines* del juego por un cambio en el JSON de la API a último momento.  
Por lo tanto, los *deadlines* se representan de una manera distinta a la planeada originalmente.
- La stamina y la velocidad fueron tratadas como el mismo valor por error y por tiempo no pudimos añadir al juego una funcion de velocidad
