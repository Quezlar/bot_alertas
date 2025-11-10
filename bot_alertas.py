import requests
import json
import datetime

# === CONFIGURACIÓN ===
API_URL = "https://limpiezasroquez.com/api/index.php"
TOKEN = "MI_TOKEN_SECRETO_123"  # mismo token que en el PHP

# === FUNCIÓN PARA ENVIAR ALERTAS ===
def enviar_alertas(alertas):
    headers = {'X-Auth-Token': TOKEN, 'Content-Type': 'application/json'}
    try:
        response = requests.post(API_URL, headers=headers, json=alertas)
        if response.status_code == 200:
            print("✅ Alertas enviadas correctamente:", response.json())
        else:
            print("⚠️ Error al enviar alertas:", response.text)
    except Exception as e:
        print("❌ Error de conexión:", e)


# === GENERADOR DE ALERTAS DE EJEMPLO ===
if __name__ == "__main__":
    hora = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    alertas_demo = [
        {
            "activo": "BTC/USD",
            "tipo": "COMPRA",
            "precio": 104900,
            "rsi": 33,
            "hora": hora
        },
        {
            "activo": "ETH/USD",
            "tipo": "VENTA",
            "precio": 3580,
            "rsi": 72,
            "hora": hora
        }
    ]
    enviar_alertas(alertas_demo)
