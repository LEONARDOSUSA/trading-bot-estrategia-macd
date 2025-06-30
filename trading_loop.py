import os
import time
import requests
import pandas as pd
import alpaca_trade_api as tradeapi
import ta
import pytz
from datetime import datetime, timedelta, time as dtime
from pytz import timezone

# 🔐 Credenciales
ALPACA_KEY = os.getenv("ALPACA_KEY")
ALPACA_SECRET = os.getenv("ALPACA_SECRET")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# 🌎 Configuración Alpaca
BASE_URL = "https://paper-api.alpaca.markets"
NY_TZ = timezone('America/New_York')
api = tradeapi.REST(ALPACA_KEY, ALPACA_SECRET, base_url=BASE_URL)

# ⏰ Ventana operativa
HORA_INICIO = dtime(9, 48)
HORA_CORTE = dtime(14, 0)

tickers_activos = ["AAPL", "SPY", "TSLA", "MSFT", "NVDA", "AMD", "META"]

# 📨 Telegram
def enviar_mensaje(mensaje):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": mensaje}
    response = requests.post(url, data=payload)
    if not response.ok:
        raise Exception(f"Telegram error: {response.text}")

# 📈 Obtener datos desde Alpaca
def obtener_datos(ticker, limit=150, timeframe="5Min"):
    try:
        bars = api.get_bars(ticker, timeframe=timeframe, limit=limit).df
        df = bars[['open', 'high', 'low', 'close', 'volume']].copy()
        df.index = df.index.tz_convert('America/New_York')
        return df
    except Exception as e:
        print(f"⚠️ Error al obtener datos de {ticker}: {e}", flush=True)
        return pd.DataFrame()

# ⚙️ MACD cruce por timeframe
def obtener_macd_cruce(ticker, timeframe, momento, direccion="CALL"):
    try:
        fin = momento.astimezone(NY_TZ)
        inicio = fin - _delta_timeframe(timeframe, 100)

        bars = api.get_bars(ticker, timeframe, start=inicio.isoformat(), end=fin.isoformat()).df
        if bars.empty or len(bars) < 35:
            return False

        df = bars[["close"]].copy()
        macd = ta.trend.MACD(df["close"])
        df["macd"] = macd.macd()
        df["signal"] = macd.macd_signal()

        m0, m1 = df["macd"].iloc[-2], df["macd"].iloc[-1]
        s0, s1 = df["signal"].iloc[-2], df["signal"].iloc[-1]

        return m0 < s0 and m1 > s1 if direccion == "CALL" else m0 > s0 and m1 < s1

    except Exception as e:
        print(f"⚠️ Error MACD {timeframe} en {ticker}: {e}", flush=True)
        return False

def _delta_timeframe(tf_str, n):
    return timedelta(minutes=n) if tf_str == "1Min" else (
           timedelta(minutes=5 * n) if tf_str == "5Min" else (
           timedelta(minutes=15 * n) if tf_str == "15Min" else timedelta(minutes=60)))

def confirmar_macd_multiframe(ticker, momento, direccion):
    timeframes = ["1Min", "5Min", "15Min"]
    resultados = {tf: obtener_macd_cruce(ticker, tf, momento, direccion) for tf in timeframes}
    resultados["alineados"] = all(resultados.values())
    return resultados

def evaluar_ruptura(ticker, df):
    if df is None or df.empty:
        return False

    ultimo = df.iloc[-1]
    cuerpo = abs(ultimo["close"] - ultimo["open"])
    rango = ultimo["high"] - ultimo["low"]

    if rango == 0 or cuerpo < 0.4 * rango:
        return False

    direccion = "CALL" if ultimo["close"] > ultimo["open"] else "PUT"
    momento = df.index[-1].to_pydatetime()
    confirmaciones = confirmar_macd_multiframe(ticker, momento, direccion)

    if confirmaciones["alineados"]:
        hora = momento.strftime('%H:%M')
        return f"📈 Señal {direccion} confirmada en {ticker} — {hora}"

    return False

# 🚀 Inicio
print("📍 Inicio alcanzado", flush=True)

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
print("🚦 Esperando ventana operativa...\n", flush=True)

# 🔁 Loop operativo
while True:
    ahora = datetime.now(NY_TZ).time()

    if ahora < HORA_INICIO:
        print("⏳ Antes del horario de apertura. Durmiendo...", flush=True)
        time.sleep(60)
        continue

    if ahora >= HORA_CORTE:
        print("🕓 Fuera de horario. Esperando próxima jornada...", flush=True)
        time.sleep(300)  # Esperar 5 minutos
        continue

    if not tickers_activos:
        print("✅ Todos los tickers procesados. Esperando siguiente oportunidad...", flush=True)
        time.sleep(300)
        continue

    for ticker in tickers_activos[:]:
        try:
            df = obtener_datos(ticker)
            señal = evaluar_ruptura(ticker, df)

            if señal:
                print(f"📊 {señal}", flush=True)
                enviar_mensaje(señal)
                tickers_activos.remove(ticker)

        except Exception as e:
            print(f"⚠️ Error con {ticker}: {e}", flush=True)

    time.sleep(60)
def evaluar_ruptura_en_fecha(ticker, fecha_str, hora_str="11:20", timeframe="5Min", velas=200):
    """
    Evalúa si hubo una ruptura confirmada por MACD multiframe en una fecha y hora pasadas.
    """
    try:
        objetivo = datetime.strptime(f"{fecha_str} {hora_str}", "%Y-%m-%d %H:%M")
        momento = NY_TZ.localize(objetivo)

        print(f"🔎 Analizando ruptura para {ticker} el {fecha_str} a las {hora_str}...", flush=True)

        # Obtener datos históricos más extensos por si el horario está en medio de la sesión
        bars = api.get_bars(symbol=ticker, timeframe=timeframe, limit=velas).df
        if bars.empty:
            print("❌ No se obtuvieron datos de Alpaca.")
            return

        df = bars[['open', 'high', 'low', 'close', 'volume']].copy()
        df.index = df.index.tz_convert('America/New_York')

        # Filtrar solo hasta el momento deseado
        df_filtrado = df[df.index <= momento]
        if df_filtrado.empty:
            print("⛔ No hay datos anteriores al momento especificado.")
            return

        señal = evaluar_ruptura(ticker, df_filtrado)
        if señal:
            print(f"✅ Señal histórica: {señal}", flush=True)
        else:
            print(f"🟤 Sin ruptura confirmada para {ticker} en ese momento.", flush=True)

    except Exception as e:
        print(f"⚠️ Error en evaluación histórica: {e}", flush=True)
def escanear_dia_historico(tickers, fecha_str="2025-06-28", timeframe="5Min", enviar_por_telegram=True):
    """
    Recorre un día completo del pasado y muestra todas las señales confirmadas por ruptura + MACD multiframe.
    """
    print(f"\n📅 Escaneando señales del {fecha_str}...\n", flush=True)
    try:
        fecha_base = NY_TZ.localize(datetime.strptime(fecha_str, "%Y-%m-%d"))
        horas = [dtime(h, m) for h in range(9, 15) for m in range(0, 60, 5)]
        momentos = [datetime.combine(fecha_base.date(), h) for h in horas]
        momentos = [NY_TZ.localize(m) for m in momentos if h >= dtime(9, 48) and h < dtime(14, 0)]

        for ticker in tickers:
            print(f"\n🔍 {ticker}", flush=True)
            bars = api.get_bars(ticker, timeframe=timeframe, limit=1000).df
            if bars.empty:
                print("⛔ Sin datos")
                continue

            df = bars[['open', 'high', 'low', 'close', 'volume']].copy()
            df.index = df.index.tz_convert(NY_TZ)

            for momento in momentos:
                df_filtrado = df[df.index <= momento]
                if len(df_filtrado) < 35:
                    continue

                señal = evaluar_ruptura(ticker, df_filtrado)
                if señal:
                    print(f"✅ {señal}", flush=True)
                    if enviar_por_telegram:
                        try:
                            enviar_mensaje(f"[Histórico] {señal}")
                        except Exception as e:
                            print(f"🔴 Telegram error: {e}", flush=True)

    except Exception as e:
        print(f"❌ Error al escanear histórico: {e}", flush=True)

       


    
            
