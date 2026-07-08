import time
import json
import os
import re
from datetime import datetime
from queueClient import obtener_tarea

ARCHIVO_SALIDA = "/app/outputs/estadosTareas.jsonl" if os.path.exists("/app/outputs") else "outputs/estadosTareas.jsonl"
RUTA_DATA = "/app/data/" if os.path.exists("/app/data") else "data/"
RUTA_OUTPUTS = "/app/outputs/" if os.path.exists("/app/outputs") else "outputs/"

def registrar_estado(tarea_id, estado, avance, mensaje):
    evento = {
        "timestamp": datetime.utcnow().isoformat(),
        "tareaId": tarea_id,
        "estado": estado,
        "avance": avance,
        "mensaje": mensaje
    }
    # ensure_ascii=False arregla el problema de los caracteres extraños
    with open(ARCHIVO_SALIDA, "a", encoding="utf-8") as f:
        f.write(json.dumps(evento, ensure_ascii=False) + "\n")
    print(f"[{evento['timestamp']}] {tarea_id} | {estado} | {avance}% | {mensaje}")

def procesar_logs(tarea):
    tarea_id = tarea["tareaId"]
    archivo = tarea["archivo"]
    ruta_archivo = os.path.join(RUTA_DATA, archivo)
    ruta_resultados = os.path.join(RUTA_OUTPUTS, f"anomalias_{tarea_id}.log")
    
    registrar_estado(tarea_id, "iniciado", 0, f"Iniciando lectura real de {archivo}")
    
    anomalias_detectadas = []
    try:
        with open(ruta_archivo, "r", encoding="utf-8") as f:
            lineas = f.readlines()
            total_lineas = len(lineas)
            
            for i, linea in enumerate(lineas):
                # Publicar estado cada 1000 líneas leídas
                if i % 1000 == 0 and i > 0:
                    avance = int((i / total_lineas) * 100)
                    registrar_estado(tarea_id, "procesando", avance, f"Analizadas {i} líneas. {len(anomalias_detectadas)} anomalías hasta ahora...")
                    time.sleep(1) # Pequeña pausa para poder observar el progreso en la interfaz
                
                # Reglas de detección de anomalías
                if "(ANOMALÍA_PROB)" in linea:
                    anomalias_detectadas.append(linea.strip())
                elif "transfirió" in linea:
                    match = re.search(r'\$([\d,]+)', linea)
                    if match:
                        monto = int(match.group(1).replace(",", ""))
                        if monto >= 5000000:
                            anomalias_detectadas.append(linea.strip() + " <-- [FRAUDE ECONÓMICO]")

        # Guardar las anomalías reales en un archivo de resultados
        with open(ruta_resultados, "w", encoding="utf-8") as f:
            for anomalia in anomalias_detectadas:
                f.write(anomalia + "\n")

        registrar_estado(tarea_id, "completado", 100, f"Auditoría finalizada. {len(anomalias_detectadas)} anomalías críticas detectadas y guardadas.")

    except Exception as e:
        registrar_estado(tarea_id, "fallido", 0, f"Error crítico: {str(e)}")

if __name__ == "__main__":
    print("Worker de Auditoría SA-MP iniciado. Esperando tareas...")
    while True:
        tarea = obtener_tarea()
        if tarea:
            procesar_logs(tarea)
        else:
            time.sleep(2)