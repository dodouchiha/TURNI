import streamlit as st
import pandas as pd
import calendar
from datetime import datetime
import holidays
from io import BytesIO

# Titolo
st.title("🗓️ Pianificazione Turni Mensili")

# Selezione della data
data_selezionata = st.date_input("Seleziona una data nel mese da pianificare", datetime.today())

# Estrai mese e anno
mese = data_selezionata.month
anno = data_selezionata.year
nome_mese = data_selezionata.strftime('%B')

# Genera tutte le date del mese
_, ultimo_giorno = calendar.monthrange(anno, mese)
giorni_mese = pd.date_range(start=f"{anno}-{mese:02d}-01", end=f"{anno}-{mese:02d}-{ultimo_giorno}")

# Festività italiane
festivi_it = holidays.country_holidays('IT', years=anno)

# Funzione per determinare se è un giorno ambulatoriale
def is_ambulatorio(data):
    weekday = data.weekday()  # 0=Mon, 2=Wed, 4=Fri
    is_weekday = weekday in [0, 2, 4]
    is_holiday = data in festivi_it
    return is_weekday and not is_holiday

# Costruzione DataFrame
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

# Funzione di stile
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
st.subheader(f"Calendario per il mese di {nome_mese} {anno}")
st.dataframe(df.style.apply(evidenzia_speciali, axis=1), use_container_width=True)

# Esporta in Excel
def to_excel(dataframe):
    output = BytesIO()
    writer = pd.ExcelWriter(output, engine='openpyxl')
    dataframe.to_excel(writer, index=False, sheet_name='Turni')
    writer.close()
    output.seek(0)
    return output

# Pulsante download
excel_bytes = to_excel(df)
st.download_button(
    label="📥 Scarica il calendario in Excel",
    data=excel_bytes,
    file_name=f"calendario_turni_{anno}_{mese:02d}.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)
