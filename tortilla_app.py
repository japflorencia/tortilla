import streamlit as st
import random

# Initialize session state variables
if 'people' not in st.session_state:
    st.session_state.people = []
if 'payments' not in st.session_state:
    st.session_state.payments = {}
if 'history' not in st.session_state:
    st.session_state.history = []

# Function to add a person
def add_person(name):
    if name and name not in st.session_state.people:
        st.session_state.people.append(name)
        st.session_state.payments[name] = 0

# Function to remove a person
def remove_person(name):
    if name in st.session_state.people:
        st.session_state.people.remove(name)
        st.session_state.payments.pop(name, None)

# Function to select who pays
def select_payer(attendees):
    if not attendees:
        st.warning("No attendees selected!")
        return None
    min_payments = min(st.session_state.payments[attendee] for attendee in attendees)
    candidates = [attendee for attendee in attendees if st.session_state.payments[attendee] == min_payments]
    payer = random.choice(candidates)
    st.session_state.payments[payer] += 1
    st.session_state.history.append(payer)
    return payer

# Streamlit app layout
st.title("¿Quién paga la tortilla?")
st.header("Lista de personas")

# Add person
new_person = st.text_input("Añadir persona")
if st.button("Añadir"):
    add_person(new_person)
    st.success(f"{new_person} ha sido añadido a la lista.")

# Remove person
remove_person_name = st.selectbox("Eliminar persona", [""] + st.session_state.people)
if st.button("Eliminar"):
    remove_person(remove_person_name)
    st.success(f"{remove_person_name} ha sido eliminado de la lista.")

# Display list of people
st.subheader("Personas en el grupo")
st.write(st.session_state.people)

# Mark attendees
st.header("Marcar asistentes")
attendees = st.multiselect("Selecciona los asistentes", st.session_state.people)

# Select who pays
if st.button("¿Quién paga?"):
    payer = select_payer(attendees)
    if payer:
        st.success(f"{payer} debe pagar la tortilla esta vez.")

# Display payment history
st.header("Historial de pagos")
st.write(st.session_state.history)

# Display payment counts
st.header("Conteo de pagos")
st.write(st.session_state.payments)

