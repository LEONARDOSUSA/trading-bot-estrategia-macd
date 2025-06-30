import os
import sys
import time
from datetime import datetime, time as dtime

from utils.telegram import enviar_mensaje
print("📍 Inicio alcanzado", flush=True)

def notificar_inicio():
    hora_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    mensaje = f"✅ Bot MACD activo desde {hora_actual}. Escaneando rupturas intradía..."
    print("🟡 Ejecutando notificar_inicio()", flush=True)
    print(mensaje, flush=True)
    try:
        enviar_mensaje(mensaje)
        print("🟢 Mensaje enviado con éxito.", flush=True)
    except Exception as e:
        print(f"🔴 Error al enviar mensaje: {e}", flush=True)

# 🧭 Rutas relativas para importaciones
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from estrategias.macd_breakout import evaluar_ruptura
from utils.data import obtener_datos

# Horario operativo
HORA_INICIO = dtime(9, 48)   # 09:48 AM NY
HORA_CORTE  = dtime(14, 0)   # 02:00 PM NY

# Lista de tickers a monitorear
tickers_activos = ["AAPL", "SPY", "TSLA", "MSFT", "NVDA", "AMD", "META"]

# ✅ Notificación de arranque
notificar_inicio()

# Loop principal
print("🚀 Bot iniciado, esperando ventana operativa...", flush=True)
while True:
    ahora = datetime.now().time()

    if ahora < HORA_INICIO:
        time.sleep(30)
        continue

    if ahora >= HORA_CORTE or not tickers_activos:
        print("✅ Fin de jornada. Bot finalizado.", flush=True)
        enviar_mensaje("📴 Bot MACD finalizado. Jornada concluida.")
        break

    for ticker in tickers_activos[:]:
        try:
            df = obtener_datos(ticker)
            señal = evaluar_ruptura(ticker, df)

            if señal:
                print(f"📊 Señal detectada en {ticker}", flush=True)
                enviar_mensaje(f"📢 Señal encontrada: {señal}")
                tickers_activos.remove(ticker)

        except Exception as e:
            print(f"⚠️ Error con {ticker}: {e}", flush=True)

    time.sleep(60)

                
