import os
import streamlit as st
from bokeh.models.widgets import Button
from bokeh.models import CustomJS
from streamlit_bokeh_events import streamlit_bokeh_events
from PIL import Image
import time
import paho.mqtt.client as paho
import json
import base64  # Para convertir la imagen a base64

from gtts import gTTS
from googletrans import Translator

# Función para convertir la imagen a base64
def get_base64_of_bin_file(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

# Convertir la imagen de fondo local a base64
background_image = get_base64_of_bin_file("Fondo.png")  # Cambia a la ruta de tu imagen local

# CSS para imagen de fondo
page_bg_img = f'''
<style>
.stApp {{
    background-image: url("data:image/jpg;base64,{background_image}");
    background-size: cover;
}}
</style>
'''
st.markdown(page_bg_img, unsafe_allow_html=True)

def on_publish(client, userdata, result):  # Función de callback
    print("el dato ha sido publicado \n")
    pass

def on_message(client, userdata, message):
    global message_received
    time.sleep(2)
    message_received = str(message.payload.decode("utf-8"))
    st.write(message_received)

# Configuración del cliente MQTT
broker = "157.230.214.127"
port = 1883
client1 = paho.Client("GIT-HUB")
client1.on_message = on_message

st.title("Control por voz")

# Mostrar una imagen en el encabezado
image = Image.open('Control por voz.png')
st.image(image, width=200)

st.write("Toca el Botón y habla ")

# Botón de reconocimiento de voz
stt_button = Button(label="Inicio", width=200)

stt_button.js_on_event("button_click", CustomJS(code="""
    var recognition = new webkitSpeechRecognition();
    recognition.continuous = true;
    recognition.interimResults = true;

    recognition.onresult = function (e) {
        var value = "";
        for (var i = e.resultIndex; i < e.results.length; ++i) {
            if (e.results[i].isFinal) {
                value += e.results[i][0].transcript;
            }
        }
        if (value != "") {
            document.dispatchEvent(new CustomEvent("GET_TEXT", {detail: value}));
        }
    }
    recognition.start();
    """))

# Escuchar eventos del botón
result = streamlit_bokeh_events(
    stt_button,
    events="GET_TEXT",
    key="listen",
    refresh_on_update=False,
    override_height=75,
    debounce_time=0)

if result:
    if "GET_TEXT" in result:
        st.write(result.get("GET_TEXT"))
        client1.on_publish = on_publish
        client1.connect(broker, port)
        message = json.dumps({"Act1": result.get("GET_TEXT").strip()})
        ret = client1.publish("camila_control", message)

    # Crear directorio temporal si no existe
    try:
        os.mkdir("temp")
    except:
        pass



