import base64
import os
import json
import requests
from openai import OpenAI
from dotenv import load_dotenv
from clave_openai import obtener_api_key

load_dotenv()

class ChatBot:
    def __init__(self, 
                 api_key = obtener_api_key(), 
                 model='gpt-4o',
                 system=(
                    "Eres un(a) experto(a) botánico(a) y zoólogo(a) especializado(a) en la flora y fauna y me decis el nombre cientifico, donde usualmente se encuentra en nicaragua (si es de nicaragua el animal) y su status de peligro de extinción . "
                    "Cuando recibas resultados de identificación de la API de PlantNet, tu tarea es explicar y comparar, "
                    "asegurándote de mencionar que NO obtuviste los datos del API de PlantNet. "
                    "Si no es una planta, ayúdame a identificar el animal u objeto de la imagen y describe sus características."
                 )) -> None:
        self._api_key = api_key
        self._client = OpenAI(api_key=self._api_key)
        self._model = model
        self._system = system
        self._messages = []
        self._max_tokens = 2000

        # API key de PlantNet (se carga de .env)
        self._plantnet_api_key = os.getenv('PLANTNET_API_KEY', '')

        # Mensaje del sistema inicial
        self._add_message({"role": "system", "content": self._system})

    @property
    def _headers(self):
        return {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self._api_key}"
        }

    @property
    def _payload(self):
        return {
            "model": self._model,
            "messages": self.messages,
            "max_tokens": self._max_tokens
        }

    @property
    def messages(self):
        return self._messages

    def clear_messages(self):
        self._messages = []
        self._add_message({"role": "system", "content": self._system})

    def _add_message(self, message):
        self._messages.append(message)

    def _ask_text(self, text):
        self._add_message({"role": "user", "content": text})

        response = self._client.chat.completions.create(
            model=self._model,
            messages=self.messages,
            max_tokens=self._max_tokens
        )

        assistant_msg = response.choices[0].message
        self._add_message({
            "role": assistant_msg.role,
            "content": assistant_msg.content
        })

        return assistant_msg.content

    def chat(self, text, image_path=None, image_bytes=None):
        if not image_path and not image_bytes:
            return self._ask_text(text)
        else:
            return self._ask_image(text, image_path, image_bytes)

    def _ask_image(self, text, image_path=None, image_bytes=None):
        if image_bytes is None:
            if image_path is not None:
                with open(image_path, "rb") as image_file:
                    image_bytes = image_file.read()
            else:
                raise ValueError("No image provided. Please provide an image_path or image_bytes.")

        encoded_image = base64.b64encode(image_bytes).decode('utf-8')
        self.messages.append({
            "role": "user",
            "content": [
                {"type": "text", "text": text},
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{encoded_image}"}}
            ]
        })

        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers=self._headers,
            json=self._payload
        )

        if response.status_code == 200:
            message_content = response.json()['choices'][0]['message']['content']
            self._add_message({
                "role": "system" if "role" not in message_content else message_content["role"],
                "content": message_content
            })
            return message_content
        else:
            raise Exception("Error from the API: " + response.text)

    def identify_with_plantnet(self, image_paths, organs=['leaf'], project='all'):
        if not self._plantnet_api_key:
            raise ValueError("No se encontró la API key de PlantNet. Asegúrate de setear PLANTNET_API_KEY.")

        api_endpoint = f"https://my-api.plantnet.org/v2/identify/{project}?api-key={self._plantnet_api_key}"
        files = []
        for idx, img_path in enumerate(image_paths):
            image_data = open(img_path, 'rb')
            files.append(('images', (f"image_{idx}.jpeg", image_data, 'image/jpeg')))
        data = {
            'organs': organs
        }
        response = requests.post(api_endpoint, files=files, data=data)
        for _, (filename, f, mime) in files:
            f.close()
        if response.status_code != 200:
            if response.status_code == 404:
                return None, 0.0, response.json()
            else:
                raise Exception("Error desde la API de PlantNet: " + response.text)
        json_result = response.json()
        best_guess = None
        score = 0.0
        if 'results' in json_result and len(json_result['results']) > 0:
            best_guess = json_result['results'][0]['species']['scientificNameWithoutAuthor']
            score = json_result['results'][0]['score']
        return best_guess, score, json_result

    def chat_with_plantnet_if_plant(self, user_text, image_path, organs=['leaf', 'flower'], project='all'):
        if not isinstance(image_path, list):
            image_path = [image_path]
        best_guess, score, raw_result = self.identify_with_plantnet(
            image_paths=image_path,
            organs=organs,
            project=project
        )
        if not best_guess or score < 0.2:
            prompt_no_plant = (
                f"PlantNet no pudo identificar la imagen como una planta (score={score:.2f}). "
                "Basándote únicamente en el contenido visual y en tus conocimientos, indica cuál es el animal u objeto que aparece en la imagen. "
                "No proporciones múltiples opciones ni realices preguntas; solo da tu conjetura final en una oración concisa. "
                f"Mensaje del usuario: {user_text}"
            )
            return self._ask_text(prompt_no_plant)
        prompt_plant = (
            f"La API de PlantNet sugiere que la planta en la imagen podría ser '{best_guess}' "
            f"(score={score*100:.2f}%). "
            "Dame una explicación detallada: nombre científico, hábitat, características, "
            "distribución geográfica, si esta en peligro de extinción y cuidados. También menciona posibles confusiones con otras especies."
        )
        if user_text.strip():
            prompt_plant += f"\nEl usuario pregunta: {user_text}"
        return self._ask_text(prompt_plant)
