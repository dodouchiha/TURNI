import streamlit as st
import pandas as pd
import calendar
from datetime import datetime
import holidays
from io import BytesIO

# Titolo app
st.title("Pianificazione Turni Mensili")

# Input dell'utente
data_selezionata = st.date_input("Scegli una data del mese", datetime.today())

# Estrai mese e anno
mese = data_selezionata.month
anno = data_selezionata.year
nome_mese = data_selezionata.strftime('%B')

# Calcola giorni del mese
_, ultimo_giorno = calendar.monthrange(anno, mese)
giorni_mese = pd.date_range(start=f"{anno}-{mese}-01", end=f"{anno}-{mese}-{ultimo_giorno}")

# Crea calendario festivi italiani
festivi = holidays.IT(years=anno)

# Crea DataFrame
df = pd.DataFrame({
    "Data": giorni_mese,
    "Giorno": giorni_mese.strftime("%A"),
    "Festivo": giorni_mese.isin(festivi)
})

# Funzione stile: weekend o festivi = grigio chiaro
def evidenzia_speciali(row):
    weekday = row["Data"].weekday()
    is_festivo = row["Festivo"]
    if weekday in [5, 6] or is_festivo:
        return ['background-color: lightgray; border: 1px solid black'] * len(row)
    else:
        return ['background-color: white; border: 1px solid black'] * len(row)

# Visualizzazione
st.subheader(f"Calendario Turni - {nome_mese} {anno}")
st.dataframe(df[["Data", "Giorno", "Festivo"]].style.apply(evidenzia_speciali, axis=1), use_container_width=True)

# Pulsante di esportazione in Excel
def to_excel(df):
    output = BytesIO()
    writer = pd.ExcelWriter(output, engine='openpyxl')
    df.to_excel(writer, index=False, sheet_name='Turni')
    writer.save()
    output.seek(0)
    return output

excel_data = to_excel(df)

st.download_button(
    label="📥 Scarica Excel",
    data=excel_data,
    file_name=f"turni_{anno}_{mese:02}.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)
