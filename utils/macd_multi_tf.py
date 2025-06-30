import os
import pandas as pd
import alpaca_trade_api as tradeapi
import ta
import pytz
from datetime import timedelta

ALPACA_KEY = os.getenv("ALPACA_KEY")
ALPACA_SECRET = os.getenv("ALPACA_SECRET")
BASE_URL = "https://paper-api.alpaca.markets"

api = tradeapi.REST(ALPACA_KEY, ALPACA_SECRET, base_url=BASE_URL)

def obtener_macd_cruce(ticker, timeframe, momento, direccion="CALL"):
    try:
        ny_tz = pytz.timezone("America/New_York")
        fin = momento.astimezone(ny_tz)
        inicio = fin - _delta_timeframe(timeframe, 100)

        bars = api.get_bars(
            symbol=ticker,
            timeframe=timeframe,
            start=inicio.isoformat(),
            end=fin.isoformat()
        ).df

        if bars.empty or len(bars) < 35:
            return False

        df = bars[['close']].copy()
        macd = ta.trend.MACD(df["close"])
        df["macd"] = macd.macd()
        df["signal"] = macd.macd_signal()

        m0, m1 = df["macd"].iloc[-2], df["macd"].iloc[-1]
        s0, s1 = df["signal"].iloc[-2], df["signal"].iloc[-1]

        if direccion == "CALL":
            return m0 < s0 and m1 > s1
        else:
            return m0 > s0 and m1 < s1

    except Exception as e:
        print(f"⚠️ Error MACD {timeframe} en {ticker}: {e}", flush=True)
        return False

def confirmar_macd_multiframe(ticker, momento, direccion):
    timeframes = ["1Min", "5Min", "15Min"]
    resultados = {}

    for tf in timeframes:
        resultados[tf] = obtener_macd_cruce(ticker, tf, momento, direccion)

    resultados["alineados"] = all(resultados.values())
    return resultados

def _delta_timeframe(tf_str, n):
    if tf_str == "1Min":
        return timedelta(minutes=n)
    elif tf_str == "5Min":
        return timedelta(minutes=5 * n)
    elif tf_str == "15Min":
        return timedelta(minutes=15 * n)
    else:
        return timedelta(minutes=60)
       
