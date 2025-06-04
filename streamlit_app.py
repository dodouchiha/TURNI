import streamlit as st
import pandas as pd
import calendar
from datetime import datetime
import holidays
from io import BytesIO

# Titolo
st.title("🗓️ Pianificazione Turni Mensili con Assenze per Medico")

# Selezione medici
st.sidebar.header("👨‍⚕️ Selezione Medici")
medici = st.sidebar.multiselect("Scegli i medici da includere:", ["Dr. Rossi", "Dr. Bianchi", "Dr. Verdi"], default=["Dr. Rossi", "Dr. Bianchi"])

# Selezione del mese e anno
oggi = datetime.today()
mese = st.selectbox("Seleziona il mese", options=list(range(1, 13)), index=oggi.month - 1, format_func=lambda x: calendar.month_name[x])
anno = st.selectbox("Seleziona l'anno", options=list(range(oggi.year - 1, oggi.year + 3)), index=1)
nome_mese = calendar.month_name[mese]

# Crea le date del mese
_, ultimo_giorno = calendar.monthrange(anno, mese)
giorni_mese = pd.date_range(start=f"{anno}-{mese:02d}-01", end=f"{anno}-{mese:02d}-{ultimo_giorno}")
festivi_it = holidays.country_holidays('IT', years=anno)

# Funzione per ambulatorio
def is_ambulatorio(data):
    return data.weekday() in [0, 2, 4] and data.date() not in festivi_it

# DataFrame base
giorni_series = pd.Series(giorni_mese)

df = pd.DataFrame({
    "Data": giorni_mese,
    "Giorno": giorni_mese.strftime("%A"),
    "Festivo": giorni_series.dt.date.isin(festivi_it),
    "Nome Festivo": [festivi_it.get(d.date(), "") for d in giorni_mese],
    "Mattina": "",
    "Pomeriggio": "",
    "Notte": "",
    "Riposo": "",
    "Ambulatorio": ["Ambulatorio" if is_ambulatorio(d) else "" for d in giorni_mese]
})

# Tipi di assenza disponibili
tipi_assenza = ["Nessuna", "Ferie", "Congresso", "Lezione"]

# Inserimento assenze per medico
for medico in medici:
    df[medico] = "Nessuna"
    st.markdown(f"### Assenze per {medico}")
    for i in range(len(df)):
        opzioni = tipi_assenza
        selezione = st.selectbox(
            f"{df.at[i, 'Data'].strftime('%d %B %Y')} - {medico}",
            opzioni,
            index=0,
            key=f"{medico}_{i}"
        )
        df.at[i, medico] = selezione

# Funzione di stile
def evidenzia_riga(row):
    style = []
    weekday = row["Data"].weekday()
    festivo = row["Festivo"]
    ambulatorio = row["Ambulatorio"] == "Ambulatorio"

    for col in row.index:
        if col == "Ambulatorio" and not ambulatorio:
            style.append("background-color: black; color: white; border: 1px solid black")
        elif col in medici and row[col] != "Nessuna":
            style.append("background-color: lightblue; border: 1px solid black")
        elif festivo or weekday in [5, 6]:
            style.append("background-color: lightgray; border: 1px solid black")
        else:
            style.append("background-color: white; border: 1px solid black")
    return style

# Visualizzazione tabella
st.subheader(f"Calendario per {nome_mese} {anno}")
st.dataframe(df.style.apply(evidenzia_riga, axis=1), use_container_width=True)

# Esportazione Excel
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
