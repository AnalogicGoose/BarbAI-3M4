import os
import base64
from dotenv import load_dotenv

# Cargar las variables de entorno desde el archivo .env
load_dotenv()

def obtener_api_key():
    """Devuelve la clave desencriptada desde la variable de entorno."""
    api_key_encriptada = os.getenv("OPENAI_API_KEY")
    if not api_key_encriptada:
        raise ValueError("La variable OPENAI_API_KEY no está definida.")

    try:
        # Elimina comillas simples o dobles si están presentes
        api_key_encriptada = api_key_encriptada.strip("'\"")
        # Decodificar base64
        api_key_desencriptada = base64.b64decode(api_key_encriptada).decode("utf-8")
        return api_key_desencriptada
    except Exception as e:
        raise ValueError(f"Error al desencriptar la clave: {e}")