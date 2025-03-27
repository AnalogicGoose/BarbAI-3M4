import streamlit as st
from chat_bot import ChatBot
from PIL import Image
import io
import base64
import tempfile

# Para modo planta, se permiten hasta 5 imágenes y selección de órgano
MAX_IMAGES = 5

# Opciones para la interfaz (en español) para plantas
ORGANS_UI_OPTIONS = [
    "(ninguno)",
    "Hoja",
    "Flor",
    "Fruta",
    "Corteza",
    "Hábito"
]

# Mapeo de las opciones en español a los valores en inglés que espera la API de PlantNet
ORGANS_MAP = {
    "Hoja": "leaf",
    "Flor": "flower",
    "Fruta": "fruit",
    "Corteza": "bark",
    "Hábito": "habit"
}

def initialize_chatbot():
    if 'chatbot' not in st.session_state:
        st.session_state['chatbot'] = ChatBot()

def handle_text_submission():
    user_input = st.session_state.user_input.strip()
    if not user_input:
        return  # No hace nada si no hay texto

    image_type = st.session_state.get("image_type", "Planta")
    
    if image_type == "Animal":
        # Para animales, se usa un solo uploader (clave "file_uploader_animal")
        file_obj = st.session_state.get("file_uploader_animal", None)
        if file_obj is not None:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".jpeg") as tmp_file:
                tmp_file.write(file_obj.getvalue())
                tmp_file_path = tmp_file.name
            # Se usa la función chat() del ChatBot (que en el código viejo utiliza _ask_image)
            response = st.session_state.chatbot.chat(user_input, image_path=tmp_file_path)
        else:
            response = st.session_state.chatbot.chat(user_input)
    else:  # Modo Planta
        uploaded_images = []
        organs = []
        for i in range(MAX_IMAGES):
            file_obj = st.session_state.get(f"file_uploader_{i}", None)
            organ_selected = st.session_state.get(f"organ_selector_{i}", None)
            if file_obj is not None:
                with tempfile.NamedTemporaryFile(delete=False, suffix=".jpeg") as tmp_file:
                    tmp_file.write(file_obj.getvalue())
                    tmp_file_path = tmp_file.name
                uploaded_images.append(tmp_file_path)
                if organ_selected and organ_selected != "(ninguno)":
                    organs.append(ORGANS_MAP.get(organ_selected, "leaf"))
                else:
                    organs.append("leaf")
        if len(uploaded_images) == 0:
            response = st.session_state.chatbot.chat(user_input)
        else:
            response = st.session_state.chatbot.chat_with_plantnet_if_plant(
                user_text=user_input,
                image_path=uploaded_images,
                organs=organs,
                project="all"
            )
    st.session_state.response = response

def main():
    st.set_page_config(page_title="Barb AI V3M4", layout="centered")
    initialize_chatbot()

    # Logo y título
    st.image("BarbAI.png", width=60)
    st.title("Barb AI V3M4")

    # Selección del tipo de imagen
    st.sidebar.subheader("Tipo de imagen")
    image_type = st.sidebar.selectbox("Selecciona el tipo de imagen:", options=["Planta", "Animal"], key="image_type")

    st.subheader("Sube tus imágenes")
    if image_type == "Animal":
        st.markdown("Sube una única imagen para identificar el animal.")
        uploaded_file = st.file_uploader("Subir imagen", type=["jpg", "jpeg", "png"], key="file_uploader_animal")
        if uploaded_file is not None:
            image = Image.open(uploaded_file)
            st.image(image, width=300)
    else:
        st.markdown("Selecciona de 1 a 5 imágenes para identificar la planta. Puedes asignar un órgano a cada imagen.")
        cols = st.columns(MAX_IMAGES)
        for i in range(MAX_IMAGES):
            with cols[i]:
                st.write(f"**Imagen #{i+1}**")
                uploaded_file = st.file_uploader("Subir imagen", type=["jpg", "jpeg", "png"], key=f"file_uploader_{i}")
                organ = st.selectbox("Selecciona órgano", options=ORGANS_UI_OPTIONS, key=f"organ_selector_{i}")
                if uploaded_file is not None:
                    image = Image.open(uploaded_file)
                    st.image(image, width=150)

    st.markdown("---")
    
    st.subheader("Chat")
    if 'response' not in st.session_state:
        st.session_state['response'] = ""
    
    st.text_area("Respuesta:", value=st.session_state.response if st.session_state.response else "No hay respuesta todavía.", height=250)
    
    st.text_input("Pregunta cualquier cosa sobre la(s) imagen(es)...", key="user_input", on_change=handle_text_submission)
    
    # Fuente personalizada (opcional)
    with open("SF-Pro-Text-Medium.otf", "rb") as font_file:
        font_data = font_file.read()
        font_base64 = base64.b64encode(font_data).decode()
    st.markdown(f"""
    <style>
    @font-face {{
        font-family: 'SF Pro Text Medium';
        src: url(data:font/truetype;charset=utf-8;base64,{font_base64}) format('truetype');
        font-weight: normal;
        font-style: normal;
    }}
    h1, h2, h3, h4, h5, h6 {{
        font-family: 'SF Pro Text Medium', sans-serif !important;
    }}
    body, p, span, div {{
        font-family: 'SF Pro Text Medium', sans-serif !important;
    }}
    textarea {{
        font-family: 'SF Pro Text Medium', sans-serif !important;
    }}
    </style>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
