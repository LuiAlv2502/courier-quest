# Courier Quest - Estructuras y Algoritmos Principales

Este documento describe las estructuras de datos y algoritmos más importantes usados en el código fuente de Courier Quest.

## Stack (stack.py)
- **Propósito:** Historial de movimientos del jugador (deshacer movimientos).
- **Estructura:** Implementación clásica de pila (stack) con métodos push, pop, peek, is_empty.
- **Algoritmo:** LIFO (Last-In, First-Out) para almacenar y recuperar posiciones previas.

## Inventario (inventory.py)
- **Propósito:** Gestiona los trabajos aceptados y recogidos por el jugador.
- **Estructura:** Lista de objetos Job, con métodos para aceptar, recoger, entregar y eliminar trabajos.
- **Algoritmos:**
  - **Heap Sort:** Para filtrar trabajos por prioridad (`filter_by_priority` usando `heapq.nlargest`).
  - **Insertion Sort:** Para ordenar trabajos por deadline (`filter_by_deadline`).

## JobManager (job_manager.py)
- **Propósito:** Controla los trabajos disponibles y visibles en el juego.
- **Estructura:** Listas de trabajos disponibles y visibles. Métodos para liberar trabajos y eliminarlos.
- **Algoritmo:** Liberación de trabajos basada en tiempo de release.

## Character (character.py)
- **Propósito:** Representa al jugador, gestiona reputación, resistencia y lógica de penalizaciones/bonificaciones.
- **Estructura:** Atributos para posición, reputación, inventario, resistencia, score, rachas, etc.
- **Algoritmo:**
  - Penalizaciones y bonificaciones de reputación según entregas, tardanzas, cancelaciones y rachas.
  - Multiplicador de pago por reputación alta.

## API y Caché (api.py)
- **Propósito:** Descarga y almacena datos del juego desde la API, con sistema de caché offline.
- **Estructura:** Archivos JSON en `json_files` y `api_cache`.
- **Algoritmo:**
  - Descarga datos con `requests.get`.
  - Recupera la última versión cacheada si la API falla.

## Constantes (constants.py)
- **Propósito:** Define valores globales para el juego (tamaños, colores, límites, FPS).

## main.py y game.py
- **Propósito:** Inicializan y ejecutan el bucle principal del juego.
- **Estructura:** Instancia de `CourierQuestGame` y ciclo de eventos, lógica de victoria/derrota.

---

**Nota:** Para detalles adicionales, consulta los comentarios en el código fuente de cada módulo.
