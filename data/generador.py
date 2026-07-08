import random
from datetime import datetime, timedelta
import os

# Configuración del generador
NUM_LINEAS = 5000
ARCHIVO_SALIDA = "sampLogsMayo2026.log"

jugadores = ["CJ_Master", "xX_Sniper_Xx", "JugadorNuevo", "Tommy_V", "Kendal_G", "Ryder_Smoke"]
admins = ["Admin_Rogue", "Fabrizio_Larco", "Admin_System"]
cajas = ["Caja_Clásica", "Caja_Rara", "Caja_Épica", "Caja_Legendaria"]
premios_comunes = ["$1,000", "$5,000", "Skin_Civil", "Arma_9mm"]
premios_raros = ["Infernus", "Minigun", "Mansión", "$10,000,000"]

def generar_logs():
    ruta_completa = os.path.join(os.path.dirname(__file__), ARCHIVO_SALIDA)
    fecha_actual = datetime(2026, 5, 1, 0, 0, 0)
    
    with open(ruta_completa, "w", encoding="utf-8") as f:
        for i in range(NUM_LINEAS):
            # Avanzar el reloj entre 1 y 60 segundos por evento
            fecha_actual += timedelta(seconds=random.randint(1, 60))
            timestamp = fecha_actual.strftime("[%Y-%m-%d %H:%M:%S]")
            
            # Decidir qué tipo de evento ocurre
            tipo_evento = random.choices(
                ["LOOTBOX", "ECONOMÍA", "CHAT", "LOGIN"], 
                weights=[0.4, 0.3, 0.2, 0.1]
            )[0]
            
            linea = ""
            
            if tipo_evento == "LOOTBOX":
                usuario = random.choice(jugadores + admins)
                caja = random.choices(cajas, weights=[0.6, 0.25, 0.1, 0.05])[0]
                
                # Inyectar anomalía: Administradores sacando cosas legendarias muy seguido
                if usuario in admins and random.random() < 0.2:
                    premio = random.choice(premios_raros)
                    linea = f"{timestamp} [{tipo_evento}] Usuario: {usuario} abrió {caja}. Premio: {premio} (ANOMALÍA_PROB)\n"
                else:
                    premio = random.choice(premios_comunes)
                    linea = f"{timestamp} [{tipo_evento}] Usuario: {usuario} abrió {caja}. Premio: {premio}\n"
                    
            elif tipo_evento == "ECONOMÍA":
                remitente = random.choice(jugadores)
                destinatario = random.choice(jugadores)
                while destinatario == remitente:
                    destinatario = random.choice(jugadores)
                
                monto = random.randint(100, 50000)
                # Inyectar anomalía: JugadorNuevo moviendo millones
                if remitente == "JugadorNuevo" and random.random() < 0.1:
                    monto = random.randint(5000000, 15000000)
                    linea = f"{timestamp} [{tipo_evento}] Usuario: {remitente} transfirió ${monto:,} a {destinatario}\n"
                else:
                    linea = f"{timestamp} [{tipo_evento}] Usuario: {remitente} transfirió ${monto:,} a {destinatario}\n"
                    
            elif tipo_evento == "CHAT":
                usuario = random.choice(jugadores)
                mensajes = ["vendo infernus", "alguien para dm?", "admin ayuda", "lag"]
                linea = f"{timestamp} [{tipo_evento}] {usuario}: {random.choice(mensajes)}\n"
                
            elif tipo_evento == "LOGIN":
                usuario = random.choice(jugadores + admins)
                linea = f"{timestamp} [{tipo_evento}] El usuario {usuario} se ha conectado.\n"
                
            f.write(linea)

    print(f"✅ Generados {NUM_LINEAS} eventos en {ruta_completa}")

if __name__ == "__main__":
    generar_logs()