import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import random
import json
from io import StringIO
from datetime import datetime
import altair as alt

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
estadisticas_sheet = spreadsheet.worksheet("estadisticas")

# Funciones para manejar los datos
def cargar_personas():
    return personas_sheet.col_values(1)

def cargar_pagos():
    registros = pagos_sheet.get_all_records()
    return {registro['nombre']: registro['conteo'] for registro in registros}

def cargar_historial():
    registros = historial_sheet.get_all_records()
    return registros

def cargar_estadisticas():
    registros = estadisticas_sheet.get_all_records()
    return {registro['nombre']: {'asistencias': registro['asistencias'], 'pagos': registro['pagos']} for registro in registros}

def guardar_persona(nombre):
    personas_sheet.append_row([nombre])

def eliminar_persona(nombre):
    cell = personas_sheet.find(nombre)
    if cell:
        personas_sheet.delete_row(cell.row)

def registrar_pago(nombre, n_asistentes, asistentes):
    pagos = cargar_pagos()
    if nombre in pagos:
        pagos[nombre] += 1
        cell = pagos_sheet.find(nombre)
        pagos_sheet.update_cell(cell.row, 2, pagos[nombre])
    else:
        pagos_sheet.append_row([nombre, 1])
    fecha = datetime.now().strftime("%Y-%m-%d")
    historial_sheet.append_row([nombre, fecha, n_asistentes, ', '.join(asistentes)])
    actualizar_estadisticas(asistentes, nombre)

def actualizar_estadisticas(asistentes, pagador):
    estadisticas = cargar_estadisticas()
    for asistente in asistentes:
        if asistente in estadisticas:
            estadisticas[asistente]['asistencias'] += 1
        else:
            estadisticas[asistente] = {'asistencias': 1, 'pagos': 0}
    if pagador in estadisticas:
        estadisticas[pagador]['pagos'] += 1
    else:
        estadisticas[pagador] = {'asistencias': 0, 'pagos': 1}
    estadisticas_sheet.clear()
    estadisticas_sheet.append_row(['nombre', 'asistencias', 'pagos'])
    for nombre, datos in estadisticas.items():
        estadisticas_sheet.append_row([nombre, datos['asistencias'], datos['pagos']])

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
        estadisticas = cargar_estadisticas()
        min_ratio = min(
            (estadisticas.get(p, {'pagos': 0, 'asistencias': 0})['pagos'] / max(1, estadisticas.get(p, {'pagos': 0, 'asistencias': 0})['asistencias']))
            for p in asistentes
        )
        candidatos = [
            p for p in asistentes
            if (estadisticas.get(p, {'pagos': 0, 'asistencias': 0})['pagos'] / max(1, estadisticas.get(p, {'pagos': 0, 'asistencias': 0})['asistencias'])) == min_ratio
        ]
        pagador = random.choice(candidatos)
        registrar_pago(pagador, len(asistentes), asistentes)
        st.success(f"{pagador} paga la siguiente tortilla.")
    else:
        st.error("Selecciona al menos un asistente.")

# Mostrar historial de pagos
st.header("Historial de pagos")
historial = cargar_historial()
st.write(historial)

# Mostrar estadísticas
st.header("Estadísticas")
estadisticas = cargar_estadisticas()
df_estadisticas = pd.DataFrame.from_dict(estadisticas, orient='index').reset_index().rename(columns={'index': 'nombre'})
st.write(df_estadisticas)

# Gráfico comparativo
st.header("Gráfico comparativo")
chart = alt.Chart(df_estadisticas).mark_bar().encode(
    x='nombre',
    y='asistencias',
    color='nombre'
).properties(title='Asistencias por persona')
st.altair_chart(chart, use_container_width=True)

chart_pagos = alt.Chart(df_estadisticas).mark_bar().encode(
    x='nombre',
    y='pagos',
    color='nombre'
).properties(title='Pagos por persona')
st.altair_chart(chart_pagos, use_container_width=True)
