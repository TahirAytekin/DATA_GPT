import streamlit as st
import pandas as pd
import openai

# Streamlit sayfa ayarı
st.set_page_config(page_title="Sales Analysis with Chatbot", layout="wide")
st.title("📊 Sales Data Analyzer + Chatbot")

# OpenAI API anahtarını gizli dosyadan alır
openai.api_key = st.secrets["openai_api_key"]

# Dosya yükleme
uploaded_file = st.file_uploader("Lütfen 'sales_data_sample.csv' dosyasını yükleyin:", type="csv")

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file, encoding='ISO-8859-1')

    st.subheader("Veri Önizleme")
    st.dataframe(df.head())

    # Tarih sütununu dönüştür
    if "ORDERDATE" in df.columns:
        df["ORDERDATE"] = pd.to_datetime(df["ORDERDATE"], errors='coerce')

    # Temel metrikler
    st.subheader("Temel İstatistikler")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Toplam Satış", f"${df['SALES'].sum():,.2f}")
    with col2:
        st.metric("Sipariş Sayısı", df["ORDERNUMBER"].nunique())
    with col3:
        st.metric("Ürün Sayısı", df["PRODUCTCODE"].nunique())

    # Ülkeye göre satış
    st.subheader("Ülkeye Göre Toplam Satışlar")
    COUNTRY_SALES = df.groupby("COUNTRY")["SALES"].sum().sort_values(ascending=False)
    st.bar_chart(COUNTRY_SALES)

    # Ürün kategorisine göre satış
    st.subheader("Ürün Kategorisine Göre Satışlar")
    PRODUCT_SALES = df.groupby("PRODUCTLINE")["SALES"].sum()
    st.bar_chart(PRODUCT_SALES)

    # Zaman serisi grafiği
    if "ORDERDATE" in df.columns:
        st.subheader("Aylık Satış Grafiği")
        df_monthly = df.dropna(subset=["ORDERDATE"]).copy()
        df_monthly["Month"] = df_monthly["ORDERDATE"].dt.to_period("M").astype(str)
        monthly_sales = df_monthly.groupby("Month")["SALES"].sum()
        st.line_chart(monthly_sales)

    # Chatbot bölümü
    st.subheader("🤖 Chatbot ile Veri Analizi")
    user_question = st.text_input("Veri hakkında bir soru sorun:")

    if user_question:
        data_info = f"Sütunlar: {', '.join(df.columns)}"
        sample_rows = df.head(3).to_dict(orient="records")

        prompt = (
            f"Elinde şu yapıya sahip bir satış verisi var:\n{data_info}\n"
            f"Örnek veriler:\n{sample_rows}\n\n"
            f"Kullanıcının sorusu: {user_question}\n"
            f"Lütfen veriye dayalı şekilde cevapla. Kısa, öz ve anlaşılır ol."
        )

        response = openai.chat.completions.create(
            model="gpt-4",
            messages=[
                {
                    "role": "system",
                    "content": "Sen veriye dayalı analiz yapan bir asistan botsun."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.2,
        )

        st.markdown("**Yanıt:**")
        st.success(response.choices[0].message.content)




