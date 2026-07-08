# SA-MP Control Panel - Auditoría y Registro Verificable

Este repositorio contiene la implementación de una **arquitectura asíncrona** y un **registro criptográfico verificable (Blockchain)** desarrollados para la asignatura de Infraestructura para Ciencia de Datos.

El sistema está diseñado para auditar grandes volúmenes de registros (*logs*) de un servidor de San Andreas Multiplayer (SA-MP), detectando anomalías en la economía in-game y manipulación de *lootboxes* de forma eficiente y segura.

## Arquitectura del Sistema

Para evitar el bloqueo computacional de la interfaz web al procesar archivos masivos, el sistema desacopla la carga de trabajo utilizando contenedores Docker:

1. **Frontend (Streamlit):** Panel de control interactivo que encola los trabajos y monitorea el progreso en tiempo real mediante un patrón de *Polling* acotado, manteniendo la interfaz siempre fluida.
2. **Broker (Redis):** Actúa como coordinador en memoria, gestionando la cola de tareas (`training_queue`) bajo el principio FIFO y almacenando el estado de progreso.
3. **Worker (Python):** Proceso en segundo plano que consume las tareas de Redis, analiza los logs con expresiones regulares y exporta las anomalías encontradas.

## Registro Verificable (Blockchain Didáctica)

Para garantizar la inmutabilidad de los reportes y evitar que administradores corruptos eliminen evidencia, el sistema implementa un protocolo de sellado criptográfico:

* **Árbol de Merkle:** Agrupa y resume los eventos de auditoría en una única huella digital.
* **Hashes Enlazados (SHA-256):** Empaqueta los registros en bloques secuenciales. Si un registro histórico es alterado, el *Efecto Avalancha* destruye el puntero del bloque siguiente, quebrando la cadena y exponiendo el fraude.
* **Prueba de Trabajo (PoW):** Implementación de un benchmark de minado determinista que exige prefijos de ceros según la dificultad.

## Tecnologías Utilizadas

* **Python 3.10**
* **Docker & Docker Compose**
* **Streamlit** (Interfaz interactiva)
* **Redis** (Cola de mensajería y caché de estados)
* **Hashlib** (Criptografía SHA-256)

## Instrucciones de Ejecución

Sigue estos pasos para levantar la infraestructura de manera local:

1. **Clonar el repositorio:**
   ```bash
   git clone [https://github.com/RinaFLJ/Prueba2Infra.git](https://github.com/RinaFLJ/Prueba2Infra.git)
   cd Prueba2Infra
