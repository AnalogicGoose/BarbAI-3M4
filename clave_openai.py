# clave_openai.py
import os
import base64
from dotenv import load_dotenv

# Cargar las variables de entorno desde el archivo .env
load_dotenv()

def obtener_api_key():
    """Devuelve la clave API desencriptada o lanza una excepción si falla."""
    api_key_encriptada = os.getenv("OPENAI_API_KEY")
    if api_key_encriptada is None:
        raise ValueError("La variable de entorno OPENAI_API_KEY no está definida.")

    try:
        # Decodificar Base64
        bytes_desencriptados = base64.b64decode(api_key_encriptada)
        return bytes_desencriptados.decode("utf-8")
    except Exception as e:
        raise ValueError(f"Error al desencriptar la clave: {e}")
