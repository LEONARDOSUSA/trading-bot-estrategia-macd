import os
import pandas as pd
import alpaca_trade_api as tradeapi

ALPACA_KEY = os.getenv("ALPACA_KEY")
ALPACA_SECRET = os.getenv("ALPACA_SECRET")
BASE_URL = "https://paper-api.alpaca.markets"

api = tradeapi.REST(ALPACA_KEY, ALPACA_SECRET, base_url=BASE_URL)

def obtener_datos(ticker, limit=150, timeframe="5Min"):
    try:
        bars = api.get_bars(symbol=ticker, timeframe=timeframe, limit=limit).df
        df = bars[['open', 'high', 'low', 'close', 'volume']].copy()
        df.index = df.index.tz_convert('America/New_York')
        print(f"✅ Datos cargados para {ticker} ({len(df)} velas)", flush=True)
        return df
    except Exception as e:
        print(f"⚠️ Error al obtener datos de {ticker}: {e}", flush=True)
        return pd.DataFrame()
