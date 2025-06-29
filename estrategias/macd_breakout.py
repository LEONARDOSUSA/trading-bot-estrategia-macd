import ta

def evaluar_ruptura(ticker, df):
    try:
        df = df.copy()
        df["MACD_12_26"] = ta.trend.macd(df["close"], window_slow=26, window_fast=12)
        df["MACD_signal_12_26"] = ta.trend.macd_signal(df["close"], window_slow=26, window_fast=12)

        df["MACD_19_39"] = ta.trend.macd(df["close"], window_slow=39, window_fast=19)
        df["MACD_signal_19_39"] = ta.trend.macd_signal(df["close"], window_slow=39, window_fast=19)

        df["MACD_50_200"] = ta.trend.macd(df["close"], window_slow=200, window_fast=50)
        df["MACD_signal_50_200"] = ta.trend.macd_signal(df["close"], window_slow=200, window_fast=50)

        macd1 = df["MACD_12_26"].iloc[-1] > df["MACD_signal_12_26"].iloc[-1]
        macd2 = df["MACD_19_39"].iloc[-1] > df["MACD_signal_19_39"].iloc[-1]
        macd3 = df["MACD_50_200"].iloc[-1] > df["MACD_signal_50_200"].iloc[-1]

        if macd1 and macd2 and macd3:
            return f"{ticker} → 🚀 Ruptura detectada con confirmación triple MACD"
        return None

    except Exception as e:
        print(f"Error en evaluación de {ticker}: {e}")
        return None
