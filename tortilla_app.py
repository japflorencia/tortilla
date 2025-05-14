import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import random
import json
from io import StringIO

# Configuración de la conexión con Google Sheets
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds_dict = json.loads(st.secrets["GOOGLE_SERVICE_ACCOUNT"])
creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
client = gspread.authorize(creds)

# Abrir la hoja de cálculo
spreadsheet = client.open("TortillaPagos")

# Cargar datos de las hojas
personas_sheet = spreadsheet.worksheet("personas")
pagos_sheet = spreadsheet.worksheet("pagos")
historial_sheet = spreadsheet.worksheet("historial")

# Funciones para manejar los datos
def cargar_personas():
    return personas_sheet.col_values(1)

def cargar_pagos():
    registros = pagos_sheet.get_all_records()
    return {registro['nombre']: registro['conteo'] for registro in registros}

def cargar_historial():
    return historial_sheet.col_values(1)

def guardar_persona(nombre):
    personas_sheet.append_row([nombre])

def eliminar_persona(nombre):
    cell = personas_sheet.find(nombre)
    if cell:
        personas_sheet.delete_row(cell.row)

def registrar_pago(nombre):
    pagos = cargar_pagos()
    if nombre in pagos:
        pagos[nombre] += 1
        cell = pagos_sheet.find(nombre)
        pagos_sheet.update_cell(cell.row, 2, pagos[nombre])
    else:
        pagos_sheet.append_row([nombre, 1])
    historial_sheet.append_row([nombre])

# Interfaz de la aplicación
st.title("¿Quién paga la tortilla?")

# Sección para añadir y eliminar personas
st.header("Gestión de personas")
nombre = st.text_input("Nombre de la persona")
if st.button("Añadir persona"):
    guardar_persona(nombre)
    st.success(f"{nombre} ha sido añadido a la lista.")
if st.button("Eliminar persona"):
    eliminar_persona(nombre)
    st.success(f"{nombre} ha sido eliminado de la lista.")

# Mostrar lista de personas
st.subheader("Lista de personas")
personas = cargar_personas()
st.write(personas)

# Sección para marcar asistentes
st.header("Asistentes")
asistentes = st.multiselect("Selecciona los asistentes", personas)

# Selección del pagador
if st.button("¿Quién paga?"):
    if asistentes:
        pagos = cargar_pagos()
        min_pagos = min(pagos.get(persona, 0) for persona in asistentes)
        candidatos = [persona for persona in asistentes if pagos.get(persona, 0) == min_pagos]
        pagador = random.choice(candidatos)
        registrar_pago(pagador)
        st.success(f"{pagador} paga la siguiente tortilla.")
    else:
        st.error("Selecciona al menos un asistente.")

# Mostrar historial de pagos
st.header("Historial de pagos")
historial = cargar_historial()
st.write(historial)
