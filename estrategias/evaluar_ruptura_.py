from datetime import datetime
from utils.macd_multi_tf import confirmar_macd_multiframe

def evaluar_ruptura(ticker, df):
    if df is None or df.empty:
        return False

    ultimo = df.iloc[-1]
    cuerpo = abs(ultimo['close'] - ultimo['open'])
    rango = ultimo['high'] - ultimo['low']

    if cuerpo < 0.4 * rango:
        return False

    direccion = "CALL" if ultimo['close'] > ultimo['open'] else "PUT"
    momento = df.index[-1].to_pydatetime()

    confirmaciones = confirmar_macd_multiframe(ticker, momento, direccion)

    if confirmaciones["alineados"]:
        return f"📈 Señal {direccion} confirmada en {ticker} ({momento.strftime('%H:%M')})"

    return False
