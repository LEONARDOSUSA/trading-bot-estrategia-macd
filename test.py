import os
import requests

print("🚀 test.py iniciado")

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
    print("❌ Variables de entorno no definidas correctamente.")
    exit()

mensaje = "🧪 Prueba de Telegram: esto es un test desde Render."

url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
payload = {
    "chat_id": TELEGRAM_CHAT_ID,
    "text": mensaje
}

try:
    response = requests.post(url, data=payload)
    print(f"📬 Telegram status: {response.status_code}")
    print(f"📬 Telegram response: {response.text}")
except Exception as e:
    print(f"❌ Error al enviar mensaje: {e}")
