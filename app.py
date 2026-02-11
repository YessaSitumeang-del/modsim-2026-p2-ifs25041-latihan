import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Dashboard Kuesioner", layout="wide")
st.title("📊 Dashboard Analisis Kuesioner")

uploaded_file = st.file_uploader("Upload file data_kuesioner.xlsx", type=["xlsx"])

if uploaded_file is not None:
    # Baca data
    df = pd.read_excel(uploaded_file)

    st.subheader("Preview Data")
    st.dataframe(df.head())

    # Kolom pertanyaan (mulai kolom ke-2)
    question_cols = df.columns[1:]

    # Mapping skala Likert ke angka (versi baru)
    likert_map = {
        "SS": 6,   # Sangat Setuju
        "S": 5,    # Setuju
        "CS": 4,   # Cukup Setuju
        "CTS": 3,  # Cukup Tidak Setuju
        "TS": 2,   # Tidak Setuju
        "STS": 1   # Sangat Tidak Setuju
    }

    df_num = df.copy()
    for col in question_cols:
        df_num[col] = df_num[col].map(likert_map)

    # =========================
    # 1. Bar Chart Distribusi Jawaban Keseluruhan
    # =========================
    all_answers = df_num[question_cols].values.flatten()
    dist_all = pd.Series(all_answers).value_counts().sort_index().reset_index()
    dist_all.columns = ["Skor", "Frekuensi"]

    fig1 = px.bar(dist_all, x="Skor", y="Frekuensi",
                  title="Distribusi Jawaban Keseluruhan")
    st.plotly_chart(fig1, use_container_width=True)

    # =========================
    # 2. Pie Chart Proporsi Jawaban Keseluruhan
    # =========================
    fig2 = px.pie(dist_all, names="Skor", values="Frekuensi",
                  title="Proporsi Jawaban Keseluruhan")
    st.plotly_chart(fig2, use_container_width=True)

    # =========================
    # 3. Stacked Bar Distribusi Jawaban per Pertanyaan
    # =========================
    dist_per_question = df_num[question_cols].apply(lambda x: x.value_counts()).fillna(0).sort_index()
    dist_per_question = dist_per_question.T.reset_index().rename(columns={"index": "Pertanyaan"})
    dist_melt = dist_per_question.melt(
        id_vars="Pertanyaan",
        var_name="Skor",
        value_name="Frekuensi"
    )

    fig3 = px.bar(
        dist_melt,
        x="Pertanyaan",
        y="Frekuensi",
        color="Skor",
        title="Distribusi Jawaban per Pertanyaan (Stacked Bar)",
        barmode="stack"
    )
    st.plotly_chart(fig3, use_container_width=True)

    # =========================
    # 4. Bar Chart Rata-rata Skor per Pertanyaan
    # =========================
    avg_scores = df_num[question_cols].mean().reset_index()
    avg_scores.columns = ["Pertanyaan", "Rata-rata Skor"]

    fig4 = px.bar(avg_scores, x="Pertanyaan", y="Rata-rata Skor",
                  title="Rata-rata Skor per Pertanyaan")
    st.plotly_chart(fig4, use_container_width=True)

    # =========================
    # 5. Bar Chart Kategori Positif, Netral, Negatif
    # =========================
    def categorize(x):
        if x >= 5:        # SS (6) dan S (5)
            return "Positif"
        elif x == 4:     # CS
            return "Netral"
        else:            # CTS (3), TS (2), STS (1)
            return "Negatif"

    categories = df_num[question_cols].applymap(categorize).values.flatten()
    cat_dist = pd.Series(categories).value_counts().reset_index()
    cat_dist.columns = ["Kategori", "Frekuensi"]

    fig5 = px.bar(cat_dist, x="Kategori", y="Frekuensi",
                  title="Distribusi Kategori Jawaban (Positif, Netral, Negatif)")
    st.plotly_chart(fig5, use_container_width=True)

else:
    st.info("Silakan upload file data_kuesioner.xlsx terlebih dahulu.")