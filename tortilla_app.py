import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import json
from datetime import datetime
import altair as alt

# Configuración de la conexión con Google Sheets
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds_dict = json.loads(st.secrets["GOOGLE_SERVICE_ACCOUNT"])
creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
client = gspread.authorize(creds)

# Abrir la hoja de cálculo
sh = client.open("TortillaPagos")

# Cargar datos de las hojas
ws_participantes = sh.worksheet("personas")
ws_historial = sh.worksheet("historial")

# Cargar participantes
participantes = ws_participantes.col_values(1)

# Función para guardar historial
def guardar_evento(fecha, pagador, asistentes):
    fila = [pagador, fecha, len(asistentes), ", ".join(asistentes)]
    ws_historial.append_row(fila)

# --- GESTIÓN DE PARTICIPANTES ---
st.sidebar.header("Gestión de Participantes")

nuevo = st.sidebar.text_input("Añadir participante")
if st.sidebar.button("Añadir"):
    if nuevo and nuevo not in participantes:
        ws_participantes.append_row([nuevo])
        st.sidebar.success(f"{nuevo} añadido.")
        st.rerun()

eliminar = st.sidebar.selectbox("Eliminar participante", [""] + participantes)
if st.sidebar.button("Eliminar") and eliminar:
    celda = ws_participantes.find(eliminar)
    if celda:
        ws_participantes.delete_rows(celda.row)
        st.sidebar.success(f"{eliminar} eliminado.")
        st.rerun()

# --- NUEVO EVENTO ---
st.header("Nuevo Evento de Tortilla")

asistentes_hoy = st.multiselect("¿Quién asistió hoy?", options=participantes)

if st.button("Calcular quién paga"):
    if not asistentes_hoy:
        st.warning("Selecciona al menos un asistente.")
    else:
        # Cargar historial
        datos_historial = ws_historial.get_all_records()
        eventos = pd.DataFrame(datos_historial)
        eventos['asistentes'] = eventos['asistentes'].apply(lambda x: [p.strip() for p in x.split(',') if p.strip()])

        # Calcular asistencias
        asistencias = {}
        creditos = {}

        for _, row in eventos.iterrows():
            for persona in row['asistentes']:
                asistencias[persona] = asistencias.get(persona, 0) + 1
            creditos[row['pagador']] = creditos.get(row['pagador'], 0) + len(row['asistentes'])

        for persona in asistentes_hoy:
            asistencias[persona] = asistencias.get(persona, 0)
            creditos[persona] = creditos.get(persona, 0)

        balance = pd.DataFrame({
            'nombre': list(set(asistencias.keys()) | set(creditos.keys())),
            'asistencias': [asistencias.get(p, 0) for p in participantes],
            'creditos': [creditos.get(p, 0) for p in participantes]
        })
        balance['deuda'] = balance['asistencias'] - balance['creditos']
        balance = balance.sort_values(by='deuda', ascending=False)

        pagador = balance.iloc[0]['nombre']
        guardar_evento(str(date.today()), pagador, asistentes_hoy)

        st.success(f"Hoy paga **{pagador}** 🍳")
        st.dataframe(balance)

        # Mostrar gráfico
        resumen = balance[['nombre', 'asistencias', 'creditos']].melt(id_vars='nombre', var_name='tipo', value_name='valor')
        chart = alt.Chart(resumen).mark_bar().encode(
            x=alt.X('nombre:N', title='Persona'),
            y=alt.Y('valor:Q', title='Cantidad'),
            color=alt.Color('tipo:N', title='Tipo')
        ).properties(
            title='Resumen de Asistencias e Invitaciones'
        )
        st.altair_chart(chart, use_container_width=True)
