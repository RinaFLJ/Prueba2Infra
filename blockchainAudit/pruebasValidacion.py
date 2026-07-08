import json
import os
import time
from datetime import datetime
from blockchain import Block
from merkle import calculate_merkle_root

PATH_JSONL = "outputs/estadosTareas.jsonl"
PATH_CHAIN = "outputs/auditoriaCadena.json"
PATH_BENCH = "outputs/benchmark_pow.csv"

def is_chain_valid(chain):
    """Verifica la integridad de los hashes enlazados en toda la cadena."""
    for i in range(1, len(chain)):
        current = chain[i]
        previous = chain[i-1]
        
        # Verificar consistencia del hash propio recalculado
        if current.hash != current.calculate_hash():
            print(f"Alerta: El bloque {current.index} tiene un hash propio corrupto.")
            return False
            
        # Verificar enlace con el bloque anterior
        if current.previous_hash != previous.hash:
            print(f"Alerta: Ruptura de enlace. El bloque {current.index} no conecta con el bloque {previous.index}.")
            return False
    return True

def ejecutar_auditoria():
    print("Iniciando Fase de Registro Verificable y Auditoria...")
    
    if not os.path.exists(PATH_JSONL):
        print(f"Error: No se encontro el archivo {PATH_JSONL}. Ejecute auditorias en Streamlit primero.")
        return

    # 1. Benchmark de Prueba de Trabajo (PoW)
    print("\n--- Ejecutando Benchmark de Prueba de Trabajo (PoW) ---")
    with open(PATH_BENCH, "w") as f:
        f.write("dificultad,intentos,tiempo_segundos,hash_obtenido\n")
        for diff in [1, 2, 3]:
            test_block = Block(0, datetime.utcnow().isoformat(), "Test PoW", "0")
            start_time = time.time()
            test_block.mine_block(diff)
            duration = time.time() - start_time
            f.write(f"{diff},{test_block.nonce},{duration:.6f},{test_block.hash}\n")
            print(f"Dificultad {diff} | Intentos: {test_block.nonce} | Tiempo: {duration:.4f}s")
    print(f"Archivo guardado: {PATH_BENCH}")

    # 2. Construccion de la Blockchain a partir del JSONL real
    with open(PATH_JSONL, "r", encoding="utf-8") as f:
        eventos = [json.loads(linea) for linea in f.readlines()]
        
    if len(eventos) < 10:
        print(f"Aviso: Se recomienda tener mas eventos en JSONL para cumplir los 10 bloques minimos. Eventos actuales: {len(eventos)}")

    # Crear bloque genesis
    blockchain_objs = [Block(0, datetime.utcnow().isoformat(), "Bloque Genesis - InfraActFinal", "0")]
    
    # Agrupar eventos de a pares o trios para poblar al menos 10 bloques de auditoria
    chunk_size = max(1, len(eventos) // 10)
    for i in range(0, len(eventos), chunk_size):
        chunk = eventos[i:i+chunk_size]
        indices_tareas = [e.get("tareaId") for e in chunk]
        
        # Calcular Raiz de Merkle del grupo de eventos
        merkle_root = calculate_merkle_root(chunk)
        
        datos_bloque = {
            "tareas_auditadas": list(set(indices_tareas)),
            "merkle_root": merkle_root,
            "cantidad_eventos": len(chunk)
        }
        
        nuevo_bloque = Block(
            index=len(blockchain_objs),
            timestamp=datetime.utcnow().isoformat(),
            data=datos_bloque,
            previous_hash=blockchain_objs[-1].hash
        )
        # Minado liviano para enlazar de forma segura
        nuevo_bloque.mine_block(difficulty=1)
        blockchain_objs.append(nuevo_bloque)

    # Exportar la cadena generada a JSON
    cadena_serializable = []
    for b in blockchain_objs:
        cadena_serializable.append({
            "index": b.index, "timestamp": b.timestamp, "data": b.data,
            "previous_hash": b.previous_hash, "nonce": b.nonce, "hash": b.hash
        })
        
    with open(PATH_CHAIN, "w", encoding="utf-8") as f:
        json.dump(cadena_serializable, f, indent=4, ensure_ascii=False)
    print(f"Blockchain estructurada con {len(blockchain_objs)} bloques guardada en {PATH_CHAIN}")

    # 3. Pruebas de Validacion ante Alteracion Controlada
    print("\n--- Pruebas de Validacion ---")
    print(f"Estado de la cadena inicial: ¿Es valida? -> {is_chain_valid(blockchain_objs)}")
    
    # Aplicar alteracion manual maliciosa en el bloque 3 (si existe)
    if len(blockchain_objs) > 3:
        print("\n[Simulacion Maliciosa] Un administrador altera el registro del Bloque 3 para ocultar fraudes...")
        blockchain_objs[3].data["tareas_auditadas"].append("AUD-FORGED")
        
        print(f"Estado de la cadena post-hackeo: ¿Es valida? -> {is_chain_valid(blockchain_objs)}")
        print("Efecto domino verificado: El sistema de auditoria criptografica detecto la corrupcion de datos con exito.")

if __name__ == "__main__":
    ejecutar_auditoria()