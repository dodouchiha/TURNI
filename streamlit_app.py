import streamlit as st
import pandas as pd
import calendar
from datetime import datetime
import holidays
from io import BytesIO

# Titolo principale
st.title("🗓️ Pianificazione Turni Mensili")

# Selezione della data di riferimento
data_selezionata = st.date_input("Seleziona una data nel mese da pianificare", datetime.today())

# Estrazione mese e anno
mese = data_selezionata.month
anno = data_selezionata.year
nome_mese = data_selezionata.strftime('%B')

# Costruzione delle date del mese
_, ultimo_giorno = calendar.monthrange(anno, mese)
giorni_mese = pd.date_range(start=f"{anno}-{mese:02d}-01", end=f"{anno}-{mese:02d}-{ultimo_giorno}")

# Festivi italiani
festivi_it = holidays.country_holidays('IT', years=anno)

# Creazione DataFrame con colonne
df = pd.DataFrame({
    "Data": giorni_mese,
    "Giorno": giorni_mese.strftime("%A"),
    "Festivo": giorni_mese.isin(festivi_it),
    "Nome Festivo": [festivi_it.get(data.date(), "") for data in giorni_mese]
})

# Funzione per evidenziare weekend e festivi
def evidenzia_speciali(row):
    giorno_sett = row["Data"].weekday()  # 5 = sabato, 6 = domenica
    if giorno_sett in [5, 6] or row["Festivo"]:
        return ['background-color: lightgray; border: 1px solid black'] * len(row)
    else:
        return ['background-color: white; border: 1px solid black'] * len(row)

# Mostra tabella
st.subheader(f"Calendario per il mese di {nome_mese} {anno}")
st.dataframe(df.style.apply(evidenzia_speciali, axis=1), use_container_width=True)

# Funzione per esportare in Excel
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
