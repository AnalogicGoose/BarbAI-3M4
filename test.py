import openai
import os
from dotenv import load_dotenv

# Cargar las variables de entorno desde el archivo .env
load_dotenv()

# Verificar si la variable se cargó correctamente
api_key = os.getenv("OPENAI_API_KEY")
if api_key:
    openai.api_key = api_key
    print(f"Clave API cargada correctamente: {api_key}")
    
    # Enviar un mensaje de prueba a ChatGPT usando la nueva API
    client = openai.OpenAI(api_key=api_key)
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": "Hola, ¿cómo estás?"}]
    )
    print("Respuesta de ChatGPT:", response.choices[0].message.content)
else:
    print("Error: No se encontró la clave API en el archivo .env.")
