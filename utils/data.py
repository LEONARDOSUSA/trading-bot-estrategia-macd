import os
import pandas as pd
from alpaca_trade_api.rest import REST
from dotenv import load_dotenv
from datetime import datetime, timedelta

load_dotenv()

ALPACA_KEY = os.getenv("ALPACA_KEY")
ALPACA_SECRET = os.getenv("ALPACA_SECRET")

api = REST(ALPACA_KEY, ALPACA_SECRET, base_url="https://paper-api.alpaca.markets")

def obtener_datos(ticker, timeframe="1Min", limit=200):
    fin = datetime.now()
    inicio = fin - timedelta(days=2)

    df = api.get_bars(
        ticker,
        timeframe,
        start=inicio.isoformat(),
        end=fin.isoformat(),
        limit=limit,
        adjustment='raw'
    ).df

    df = df[df["symbol"] == ticker]
    df = df.rename(columns={
        "t": "datetime", "o": "open", "h": "high", "l": "low", "c": "close", "v": "volume"
    })

    return df.reset_index(drop=True)
