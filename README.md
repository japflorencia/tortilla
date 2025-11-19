# 🌯 TortillaApp

A fun and fair way to decide who pays for tortillas using a balance-based system!

## Overview

**TortillaApp** is a Streamlit-based application that helps groups of friends fairly determine who should pay for the next round of tortillas. It uses a clever algorithm that tracks attendance history and calculates debts based on how many times each person has attended and how many times they've paid.

## Features

- 📊 **Fair Balance System**: Tracks attendance and payments to ensure everyone pays fairly
- 👥 **Participant Management**: Easily add and remove participants from the group
- 📈 **Visual Analytics**: View attendance and payment statistics through interactive charts
- 📱 **Real-time History**: Automatically saves all events to Google Sheets
- 🎯 **Smart Algorithm**: Automatically selects who pays based on lowest balance (owes the most)

## How It Works

The app uses a balance calculation system:

- **Asistencias** (Attendance): How many times a person attended a tortilla event
- **Créditos** (Credits): How many people they paid for/invited
- **Deuda** (Debt): Attendance - Credits = how much they "owe" in terms of paying

The person with the highest debt is chosen to pay, ensuring everyone contributes fairly.

## Installation

### Requirements

- Python 3.8+
- Google Sheets API credentials (for data persistence)
- Streamlit

### Setup

1. Clone the repository:

```bash
git clone https://github.com/japflorencia/tortilla.git
cd tortilla
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Set up Google Sheets authentication:

   - Create a Google Cloud project and enable the Google Sheets API
   - Generate a service account key and add it to your Streamlit secrets as `GOOGLE_SERVICE_ACCOUNT`
   - Create a Google Sheet named "TortillaPagos" with sheets: "personas" and "historial"

4. Run the app:

```bash
streamlit run tortilla_app.py
```

## Usage

### Participant Management

- **Add Participant**: Enter a name in the sidebar and click "Añadir" to add them to the group
- **Remove Participant**: Select a name from the dropdown and click "Eliminar" to remove them

### Record an Event

1. Select all participants who attended today from the multiselect
2. Click "Calcular quién paga" (Calculate who pays)
3. The app displays who should pay and shows the current balance sheet

### View Statistics

- The dashboard automatically displays charts showing:
  - Attendance count per person
  - Number of people each person has paid for
  - Current debt balance for each participant

## Technology Stack

- **Streamlit**: Web app framework
- **Pandas**: Data manipulation and analysis
- **Altair**: Interactive data visualization
- **gspread**: Google Sheets API client
- **oauth2client**: OAuth 2.0 authentication

## Data Structure

### Google Sheets Setup

- **personas sheet**: List of all participants
- **historial sheet**: Columns for pagador (payer), fecha (date), cantidad (count), asistentes (attendees)

## License

See LICENSE file for details.
