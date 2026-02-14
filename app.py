import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Dashboard Kuesioner", layout="wide")

st.title("📊 Dashboard Analisis Kuesioner")

# ===============================
# 1. Load Data (Langsung dari file)
# ===============================
@st.cache_data
def load_data():
    return pd.read_excel("data_kuesioner.xlsx")


try:
    df = load_data()
except FileNotFoundError:
    st.error(
        "File data_kuesioner.xlsx tidak ditemukan. "
        "Pastikan file ada di folder yang sama dengan app.py"
    )
    st.stop()

st.subheader("Preview Data")
st.dataframe(df.head())

# ===============================
# 2. Transform ke format long
# ===============================
df_long = df.drop(columns=["Partisipan"]).melt(
    var_name="Pertanyaan",
    value_name="Jawaban"
)

# Bersihkan jawaban
df_long["Jawaban"] = (
    df_long["Jawaban"]
    .astype(str)
    .str.strip()
    .str.upper()
)

valid_jawaban = ["SS", "S", "CS", "CTS", "TS", "STS"]
df_long = df_long[df_long["Jawaban"].isin(valid_jawaban)]

# ===============================
# 3. Mapping Skor
# ===============================
skor_map = {
    "SS": 6,
    "S": 5,
    "CS": 4,
    "CTS": 3,
    "TS": 2,
    "STS": 1
}

df_long["Skor"] = df_long["Jawaban"].map(skor_map)

# ===============================
# 4. Kategori Sentimen
# ===============================
def kategori(jawaban):
    if jawaban in ["SS", "S"]:
        return "Positif"
    elif jawaban == "CS":
        return "Netral"
    else:
        return "Negatif"


df_long["Kategori"] = df_long["Jawaban"].apply(kategori)

# Urutan pertanyaan
urutan_pertanyaan = [f"Q{i}" for i in range(1, 18)]

df_long["Pertanyaan"] = pd.Categorical(
    df_long["Pertanyaan"],
    categories=urutan_pertanyaan,
    ordered=True
)

st.divider()

# ===============================
# 5. Grafik 1 - Distribusi Jawaban
# ===============================
st.subheader("1️⃣ Distribusi Jawaban (Keseluruhan)")

distribusi = (
    df_long["Jawaban"]
    .value_counts()
    .reset_index()
)
distribusi.columns = ["Jawaban", "Jumlah"]

fig1 = px.bar(
    distribusi,
    x="Jawaban",
    y="Jumlah",
    title="Distribusi Jawaban Kuesioner"
)

st.plotly_chart(fig1, use_container_width=True)

# ===============================
# 6. Grafik 2 - Pie Chart
# ===============================
st.subheader("2️⃣ Proporsi Jawaban")

fig2 = px.pie(
    distribusi,
    names="Jawaban",
    values="Jumlah",
    title="Proporsi Jawaban"
)

st.plotly_chart(fig2, use_container_width=True)

# ===============================
# 7. Grafik 3 - Stacked per Pertanyaan
# ===============================
st.subheader("3️⃣ Distribusi Jawaban per Pertanyaan")

stacked = (
    df_long
    .groupby(["Pertanyaan", "Jawaban"], observed=True)
    .size()
    .reset_index(name="Jumlah")
)

fig3 = px.bar(
    stacked,
    x="Pertanyaan",
    y="Jumlah",
    color="Jawaban",
    barmode="stack",
    category_orders={
        "Pertanyaan": urutan_pertanyaan,
        "Jawaban": ["SS", "S", "CS", "CTS", "TS", "STS"]
    },
    title="Distribusi Jawaban per Pertanyaan (Q1–Q17)"
)

st.plotly_chart(fig3, use_container_width=True)

# ===============================
# 8. Grafik 4 - Rata-rata Skor
# ===============================
st.subheader("4️⃣ Rata-rata Skor per Pertanyaan")

mean_score = (
    df_long
    .groupby("Pertanyaan", observed=True)["Skor"]
    .mean()
    .reset_index()
)

fig4 = px.bar(
    mean_score,
    x="Pertanyaan",
    y="Skor",
    category_orders={"Pertanyaan": urutan_pertanyaan},
    title="Rata-rata Skor per Pertanyaan (Skala 1–6)"
)

st.plotly_chart(fig4, use_container_width=True)

# ===============================
# 9. Grafik 5 - Kategori Sentimen
# ===============================
st.subheader("5️⃣ Distribusi Kategori Jawaban")

kategori_count = (
    df_long["Kategori"]
    .value_counts()
    .reset_index()
)
kategori_count.columns = ["Kategori", "Jumlah"]

fig5 = px.bar(
    kategori_count,
    x="Kategori",
    y="Jumlah",
    title="Distribusi Kategori (Positif, Netral, Negatif)"
)

st.plotly_chart(fig5, use_container_width=True)