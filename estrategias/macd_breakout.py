import pandas as pd
import ta

def evaluar_ruptura(ticker, df):
    try:
        if len(df) < 35:
            print(f"⏳ No hay suficientes datos para {ticker} ({len(df)} velas)", flush=True)
            return None

        macd = ta.trend.MACD(close=df['close'], window_slow=26, window_fast=12, window_sign=9)
        df['macd'] = macd.macd()
        df['signal'] = macd.macd_signal()

        macd_actual = df['macd'].iloc[-1]
        signal_actual = df['signal'].iloc[-1]
        macd_prev = df['macd'].iloc[-2]
        signal_prev = df['signal'].iloc[-2]

        if macd_prev < signal_prev and macd_actual > signal_actual:
            mensaje = f"{ticker} → Señal de entrada (MACD cruzando al alza)"
            print(f"📈 Ruptura detectada en {ticker}", flush=True)
            return mensaje
        else:
            print(f"🔍 Sin señal clara en {ticker}", flush=True)
            return None

    except Exception as e:
        print(f"❌ Error en evaluación de {ticker}: {e}", flush=True)
        return None

    
