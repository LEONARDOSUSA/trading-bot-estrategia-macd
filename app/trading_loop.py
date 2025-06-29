import os
import time
from datetime import datetime, time as dtime
from estrategias.macd_breakout import evaluar_ruptura
from utils.telegram import enviar_mensaje
from utils.data import obtener_datos

# Horario operativo
HORA_INICIO = dtime(9, 48)   # 09:48 AM NY
HORA_CORTE  = dtime(14, 0)   # 02:00 PM NY

# Lista de tickers a monitorear (puedes modificarla)
tickers_activos = ["SPY", "QQQ", "AAPL", "TSLA", "MSFT", "NVDA", "AMD", "META"]

# Loop principal
print("🚀 Bot iniciado, esperando ventana operativa...")
while True:
    ahora = datetime.now().time()

    # Esperamos hasta 9:48 AM NY
    if ahora < HORA_INICIO:
        time.sleep(30)
        continue

    # Cortamos si pasó el límite diario
    if ahora >= HORA_CORTE or not tickers_activos:
        print("✅ Fin de jornada. Bot finalizado.")
        break

    # Escaneo activo cada minuto
    for ticker in tickers_activos[:]:
        try:
            df = obtener_datos(ticker)
            señal = evaluar_ruptura(ticker, df)

            if señal:
                enviar_mensaje(f"📢 Señal encontrada: {señal}")
                tickers_activos.remove(ticker)

        except Exception as e:
            print(f"⚠️ Error con {ticker}: {e}")

    time.sleep(60)
