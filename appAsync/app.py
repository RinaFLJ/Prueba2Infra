import streamlit as st
import os
import time
import glob
import json
import uuid
import sys

# Agregar la ruta raiz para poder importar los modulos de blockchainAudit
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from queueClient import encolar_tarea
from blockchainAudit.blockchain import Block
from blockchainAudit.merkle import calculate_merkle_root
from datetime import datetime

st.set_page_config(layout="wide", page_title="SA-MP Auditoria")

st.title("SA-MP Control Panel - Auditoria")
st.write("Sistema asincrono para deteccion de anomalias en logs de economia y lootboxes.")

PATH_ESTADOS = "/app/outputs/estadosTareas.jsonl" if os.path.exists("/app/outputs") else "outputs/estadosTareas.jsonl"
PATH_DATA_DIR = "/app/data/" if os.path.exists("/app/data") else "data/"
RUTA_OUTPUTS = "/app/outputs/" if os.path.exists("/app/outputs") else "outputs/"
PATH_CHAIN = os.path.join(RUTA_OUTPUTS, "auditoriaCadena.json")
PATH_BENCH = os.path.join(RUTA_OUTPUTS, "benchmark_pow.csv")

def monitorear_tareas_multiples(tarea_ids, segundos_maximos=40):
    panel = st.empty()
    for tick in range(segundos_maximos):
        with panel.container():
            st.write("Monitoreando procesamiento de archivos en cola...")
            try:
                with open(PATH_ESTADOS, "r", encoding="utf-8") as f:
                    lineas = f.readlines()
                
                estados_tareas = {tid: {"estado": "pendiente", "avance": 0} for tid in tarea_ids}
                
                for linea in lineas:
                    try:
                        evento = json.loads(linea)
                        tid = evento.get("tareaId")
                        if tid in estados_tareas:
                            estados_tareas[tid]["estado"] = evento.get("estado", "pendiente")
                            estados_tareas[tid]["avance"] = evento.get("avance", 0)
                    except json.JSONDecodeError:
                        pass
                
                todas_terminadas = True
                for tid, info in estados_tareas.items():
                    st.write(f"Tarea {tid}: Progreso {info['avance']}% | Estado: {info['estado'].upper()}")
                    if info["estado"] not in ["completado", "fallido"]:
                        todas_terminadas = False
                
                if todas_terminadas:
                    time.sleep(1)
                    break
            except FileNotFoundError:
                st.info("Esperando a que el Worker genere el archivo de estado...")
        time.sleep(1.5)
    st.rerun()

def is_chain_valid(chain):
    for i in range(1, len(chain)):
        current = chain[i]
        previous = chain[i-1]
        if current.hash != current.calculate_hash():
            return False, f"El bloque {current.index} tiene un hash propio corrupto."
        if current.previous_hash != previous.hash:
            return False, f"Ruptura de enlace. El bloque {current.index} no conecta con el bloque {previous.index}."
    return True, "La cadena es criptograficamente valida y consistente."

# --- CREACION DE PESTAÑAS ---
tab_auditoria, tab_blockchain = st.tabs(["1. Auditoria Asincrona (Logs)", "2. Registro Verificable (Blockchain)"])

# ==========================================
# PESTAÑA 1: ORQUESTACION Y WORKERS
# ==========================================
with tab_auditoria:
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Ingesta y Orquestacion")
        archivos_subidos = st.file_uploader("Subir archivos de log SA-MP (.log)", type=["log"], accept_multiple_files=True)
        
        if archivos_subidos:
            for archivo_subido in archivos_subidos:
                ruta_destino = os.path.join(PATH_DATA_DIR, archivo_subido.name)
                if not os.path.exists(ruta_destino):
                    with open(ruta_destino, "wb") as f:
                        f.write(archivo_subido.getbuffer())
                    st.success(f"Archivo guardado: {archivo_subido.name}")

        st.markdown("---")
        ruta_busqueda = os.path.join(PATH_DATA_DIR, "*.log")
        archivos_disponibles = [os.path.basename(x) for x in glob.glob(ruta_busqueda)]
        archivos_seleccionados = st.multiselect("Seleccionar archivos para auditar en lote:", archivos_disponibles)
        iniciar_lote = st.button("Iniciar Auditoria de Archivos Seleccionados")

    with col2:
        st.subheader("Terminal del Worker (Polling)")
        if iniciar_lote:
            if not archivos_seleccionados:
                st.warning("Seleccione al menos un archivo.")
            else:
                lista_tareas = []
                for archivo in archivos_seleccionados:
                    tarea_id = f"AUD-{str(uuid.uuid4())[:8]}"
                    encolar_tarea(tarea_id, archivo)
                    lista_tareas.append(tarea_id)
                st.success("Lote enviado a Redis.")
                monitorear_tareas_multiples(lista_tareas, segundos_maximos=45)
        else:
            try:
                with open(PATH_ESTADOS, "r", encoding="utf-8") as f:
                    lineas = f.readlines()
                    if lineas:
                        st.code("".join(lineas[-10:]), language="json")
                    else:
                        st.info("El sistema esta en reposo.")
            except FileNotFoundError:
                st.info("El sistema esta en reposo.")
            if st.button("Refrescar Historial"):
                st.rerun()

    st.markdown("---")
    st.subheader("Resultados: Anomalias Detectadas")
    archivos_resultados = glob.glob(os.path.join(RUTA_OUTPUTS, "anomalias_*.log"))
    if archivos_resultados:
        archivos_ordenados = sorted(archivos_resultados, key=os.path.getctime, reverse=True)
        for ruta_reporte in archivos_ordenados[:4]:
            st.markdown(f"**Reporte: {os.path.basename(ruta_reporte)}**")
            with open(ruta_reporte, "r", encoding="utf-8") as f:
                anomalias = f.readlines()
                if anomalias:
                    st.code("".join(anomalias), language="text")
                else:
                    st.caption("No se detectaron fraudes.")
    else:
        st.info("No hay resultados de auditoria disponibles todavia.")

# ==========================================
# PESTAÑA 2: BLOCKCHAIN Y AUDITORIA
# ==========================================
with tab_blockchain:
    st.subheader("Sellado Criptografico de Evidencias")
    st.write("Convierte los registros del Worker en bloques inmutables protegidos por hashes SHA-256 y arboles de Merkle.")

    if st.button("Ejecutar Protocolo de Sellado y Validacion"):
        if not os.path.exists(PATH_ESTADOS):
            st.error("No hay eventos en el historial para encriptar. Ejecuta una auditoria en la primera pestaña.")
        else:
            with st.status("Procesando Blockchain...", expanded=True) as status:
                # 1. Benchmark PoW
                st.write("Ejecutando Benchmark de Prueba de Trabajo (PoW)...")
                bench_results = []
                for diff in [1, 2, 3]:
                    test_block = Block(0, datetime.utcnow().isoformat(), "Test PoW", "0")
                    start_time = time.time()
                    test_block.mine_block(diff)
                    duration = time.time() - start_time
                    bench_results.append({"Dificultad": diff, "Intentos (Nonce)": test_block.nonce, "Tiempo (s)": round(duration, 5), "Hash Resultante": test_block.hash})
                
                # Guardar CSV
                import pandas as pd
                df_bench = pd.DataFrame(bench_results)
                df_bench.to_csv(PATH_BENCH, index=False)
                st.dataframe(df_bench, hide_index=True)

                # 2. Construir Cadena
                st.write("Construyendo bloques a partir de los eventos...")
                with open(PATH_ESTADOS, "r", encoding="utf-8") as f:
                    eventos = [json.loads(linea) for linea in f.readlines()]

                blockchain_objs = [Block(0, datetime.utcnow().isoformat(), "Bloque Genesis - InfraActFinal", "0")]
                chunk_size = max(1, len(eventos) // 10)
                
                for i in range(0, len(eventos), chunk_size):
                    chunk = eventos[i:i+chunk_size]
                    indices_tareas = [e.get("tareaId") for e in chunk]
                    merkle_root = calculate_merkle_root(chunk)
                    
                    datos_bloque = {
                        "tareas_auditadas": list(set(indices_tareas)),
                        "merkle_root": merkle_root,
                        "cantidad_eventos": len(chunk)
                    }
                    nuevo_bloque = Block(len(blockchain_objs), datetime.utcnow().isoformat(), datos_bloque, blockchain_objs[-1].hash)
                    nuevo_bloque.mine_block(1)
                    blockchain_objs.append(nuevo_bloque)

                st.success(f"Cadena construida con {len(blockchain_objs)} bloques.")

                # Exportar JSON
                cadena_serializable = [{"index": b.index, "timestamp": b.timestamp, "data": b.data, "previous_hash": b.previous_hash, "nonce": b.nonce, "hash": b.hash} for b in blockchain_objs]
                with open(PATH_CHAIN, "w", encoding="utf-8") as f:
                    json.dump(cadena_serializable, f, indent=4, ensure_ascii=False)

                # 3. Validacion y Hackeo
                st.write("Validando integridad original de la cadena...")
                valida_orig, msg_orig = is_chain_valid(blockchain_objs)
                if valida_orig:
                    st.success(msg_orig)

                st.write("Simulando ataque: Administrador corrupto inyecta evento falso en el Bloque 1...")
                if len(blockchain_objs) > 1:
                    blockchain_objs[1].data["tareas_auditadas"].append("AUD-FORGED-HACK")
                    
                    valida_hack, msg_hack = is_chain_valid(blockchain_objs)
                    if not valida_hack:
                        st.error(f"INCONSISTENCIA DETECTADA: {msg_hack}")
                        st.info("Efecto domino verificado: El sistema rechazo la alteracion porque los hashes previos ya no coinciden.")
                
                status.update(label="Protocolo Finalizado", state="complete", expanded=True)