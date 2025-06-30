import os
import time
from datetime import datetime, time as dtime
from pytz import timezone

from utils.telegram import enviar_mensaje
from estrategias.evaluar_ruptura import evaluar_ruptura
from utils.data import obtener_datos

print("📍 Inicio alcanzado", flush=True)

NY_TZ = timezone('America/New_York')
HORA_INICIO = dtime(9, 48)
HORA_CORTE = dtime(14, 0)

tickers_activos = ["AAPL", "SPY", "TSLA", "MSFT", "NVDA", "AMD", "META"]

def notificar_inicio():
    hora_actual = datetime.now(NY_TZ).strftime("%Y-%m-%d %H:%M:%S")
    mensaje = f"✅ Bot MACD activo desde {hora_actual}. Escaneando rupturas intradía..."
    print("🟡 Ejecutando notificar_inicio()", flush=True)
    print(mensaje, flush=True)
    try:
        enviar_mensaje(mensaje)
        print("🟢 Mensaje enviado con éxito.", flush=True)
    except Exception as e:
        print(f"🔴 Error al enviar mensaje: {e}", flush=True)

notificar_inicio()

print("🚀 Bot iniciado, esperando ventana operativa...", flush=True)

while True:
    ahora = datetime.now(NY_TZ).time()

    if ahora < HORA_INICIO:
        time.sleep(30)
        continue

    if ahora >= HORA_CORTE or not tickers_activos:
        print("✅ Fin de jornada. Bot finalizado.", flush=True)
        enviar_mensaje("📴 Bot MACD finalizado. Jornada concluida.")
        break

    for ticker in tickers_activos[:]:
        try:
            df = obtener_datos(ticker, limit=150, timeframe="5Min")
            señal = evaluar_ruptura(ticker, df)

            if señal:
                print(f"📊 Señal detectada en {ticker}", flush=True)
                enviar_mensaje(señal)
                tickers_activos.remove(ticker)

        except Exception as e:
            print(f"⚠️ Error con {ticker}: {e}", flush=True)

    time.sleep(60)
