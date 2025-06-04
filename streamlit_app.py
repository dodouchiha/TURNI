import streamlit as st
import pandas as pd
import calendar
from datetime import datetime
import holidays
from io import BytesIO

# Titolo
st.title("🗓️ Pianificazione Turni Mensili")

# Menu a tendina: selezione mese e anno
oggi = datetime.today()
mese = st.selectbox("Seleziona il mese", options=list(range(1, 13)), index=oggi.month - 1, format_func=lambda x: calendar.month_name[x])
anno = st.selectbox("Seleziona l'anno", options=list(range(oggi.year - 1, oggi.year + 3)), index=1)

nome_mese = calendar.month_name[mese]

# Crea le date del mese
_, ultimo_giorno = calendar.monthrange(anno, mese)
giorni_mese = pd.date_range(start=f"{anno}-{mese:02d}-01", end=f"{anno}-{mese:02d}-{ultimo_giorno}")

# Festività italiane
festivi_it = holidays.country_holidays('IT', years=anno)

# Funzione per determinare se è un giorno ambulatoriale
def is_ambulatorio(data):
    weekday = data.weekday()
    return weekday in [0, 2, 4] and data not in festivi_it

# Crea il DataFrame
df = pd.DataFrame({
    "Data": giorni_mese,
    "Giorno": giorni_mese.strftime("%A"),
    "Festivo": giorni_mese.isin(festivi_it),
    "Nome Festivo": [festivi_it.get(data.date(), "") for data in giorni_mese],
    "Mattina": "",
    "Pomeriggio": "",
    "Notte": "",
    "Riposo": "",
    "Ambulatorio": [ "Ambulatorio" if is_ambulatorio(d) else "" for d in giorni_mese ]
})

# Stile celle
def evidenzia_speciali(row):
    giorno_sett = row["Data"].weekday()
    is_festivo = row["Festivo"]
    is_ambulatorio = row["Ambulatorio"] == "Ambulatorio"

    style = []
    for col in row.index:
        if col == "Ambulatorio" and not is_ambulatorio:
            style.append("background-color: black; color: white; border: 1px solid black")
        elif giorno_sett in [5, 6] or is_festivo:
            style.append("background-color: lightgray; border: 1px solid black")
        else:
            style.append("background-color: white; border: 1px solid black")
    return style

# Mostra tabella
st.subheader(f"Calendario per {nome_mese} {anno}")
st.dataframe(df.style.apply(evidenzia_speciali, axis=1), use_container_width=True)

# Download Excel
def to_excel(dataframe):
    output = BytesIO()
    writer = pd.ExcelWriter(output, engine='openpyxl')
    dataframe.to_excel(writer, index=False, sheet_name='Turni')
    writer.close()
    output.seek(0)
    return output

excel_bytes = to_excel(df)
st.download_button(
    label="📥 Scarica il calendario in Excel",
    data=excel_bytes,
    file_name=f"calendario_turni_{anno}_{mese:02d}.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)
