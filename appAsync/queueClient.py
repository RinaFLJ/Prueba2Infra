import redis
import json
import os

# Conectar a Redis usando la variable de entorno de Docker
redis_host = os.getenv('REDIS_HOST', 'localhost')
r = redis.Redis(host=redis_host, port=6379, db=0, decode_responses=True)

def encolar_tarea(tarea_id, archivo):
    """Envía la tarea a la cola de Redis."""
    mensaje = {"tareaId": tarea_id, "archivo": archivo, "estado": "pendiente"}
    r.lpush("colaAuditoria", json.dumps(mensaje))
    return True

def obtener_tarea():
    """Extrae la tarea más antigua de la cola de Redis."""
    tarea = r.rpop("colaAuditoria")
    if tarea:
        return json.loads(tarea)
    return None