import streamlit as st
from chat_bot import ChatBot
from PIL import Image
import io

# Inicializar la instancia del chatbot en la sesión
def initialize_chatbot():
    if 'chatbot' not in st.session_state:
        st.session_state['chatbot'] = ChatBot()

# Manejar el envío del texto
def handle_text_submission():
    user_input = st.session_state.user_input
    if user_input:
        with st.spinner("Pensando..."):
            if 'image_bytes' in st.session_state and st.session_state.image_bytes is not None:
                response = st.session_state.chatbot.chat(
                    user_input.strip(),
                    image_bytes=st.session_state.image_bytes
                )
            else:
                response = st.session_state.chatbot.chat(user_input.strip())
            st.session_state.response = response
        st.session_state.user_input = ""

# Borrar la imagen subida
def clear_uploaded_image():
    if 'image_bytes' in st.session_state:
        del st.session_state.image_bytes
    if 'file_uploader' in st.session_state:
        del st.session_state.file_uploader
    st.experimental_rerun()

# Inicializar variables de sesión
if 'response' not in st.session_state:
    st.session_state['response'] = ""
if 'image_bytes' not in st.session_state:
    st.session_state['image_bytes'] = None

# Iniciar chatbot
initialize_chatbot()

# Barra lateral para subir/borrar imagen
st.sidebar.header("Sube una imagen")
uploaded_file = st.sidebar.file_uploader("Elige una imagen...", type=["jpg", "jpeg", "png"], key="file_uploader")

if uploaded_file is not None:
    st.session_state.image_bytes = uploaded_file.getvalue()

if st.sidebar.button("Borrar Imagen"):
    clear_uploaded_image()

# ------------------------
# Diseño principal
# ------------------------

# Logo y título
st.image("BarbAI.png", width=60)
st.title("Barb AI V3M4")

# Mostrar la imagen si existe, con tamaño limitado
if st.session_state.image_bytes:
    st.subheader("Imagen Subida")
    image = Image.open(io.BytesIO(st.session_state.image_bytes))
    st.image(image, use_column_width=False, width=350)  # <-- Ajusta el width a tu preferencia

# Sección de chat
st.subheader("Chat")

# Respuesta
if st.session_state.response:
    st.text_area("Respuesta:", value=st.session_state.response, height=250)
else:
    st.text_area("Respuesta:", value="No hay respuesta todavía.", height=250)

# Caja de texto para preguntas
st.text_input(
    "Pregunta cualquier cosa sobre la imagen...",
    key="user_input",
    on_change=handle_text_submission
)

# Botón para limpiar el historial de chat
if st.button("Limpiar Conversación"):
    st.session_state.chatbot.clear_messages()
    st.session_state.response = ""
    st.experimental_rerun()
