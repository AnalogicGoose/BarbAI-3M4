
from openai import OpenAI
from clave_openai import obtener_api_key

try:
    api_key = obtener_api_key()
    client = OpenAI(api_key=api_key)

    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "Talk like a pirate."},
            {"role": "user", "content": "hello"},
        ],
    )

    print("Respuesta de ChatGPT:", completion.choices[0].message.content)

except Exception as e:
    print("Error:", e)
