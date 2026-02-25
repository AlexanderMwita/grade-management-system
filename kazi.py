import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Muonekano wa Website
st.set_page_config(page_title="Test 2 Grade Analyzer", layout="wide")

st.title("📊 Test 2 Grade Visualizer")
st.markdown("Huu ni mfumo wa kuchakata alama za wanafunzi na kutengeneza ripoti ya PDF.")

# 1. Sehemu ya Upload Faili
uploaded_file = st.file_sidebar.file_uploader("Pakia faili la Excel hapa", type=["xlsx", "xls"])

if uploaded_file is not None:
    try:
        df = pd.read_excel(uploaded_file)
        
        # Onyesha data kidogo kwenye website
        st.subheader("Hakiki Data Yako")
        st.dataframe(df.head())

        # Chagua Column ya Alama (Auto-detect)
        column_names = df.columns.tolist()
        selected_col = st.selectbox("Chagua Column yenye Alama za Wanafunzi:", column_names)

        # 2. Tengeneza Grafu
        st.subheader("Visual Representation")
        col1, col2 = st.columns(2)

        fig, ax = plt.subplots(figsize=(8, 5))
        
        with col1:
            st.write("### Histogram ya Alama")
            plt.hist(df[selected_col], bins=10, color='royalblue', edgecolor='white')
            plt.xlabel("Alama")
            plt.ylabel("Idadi ya Wanafunzi")
            st.pyplot(fig)

        with col2:
            st.write("### Takwimu Muhimu")
            st.write(f"**Wastani wa Darasa:** {df[selected_col].mean():.2f}")
            st.write(f"**Alama ya Juu:** {df[selected_col].max()}")
            st.write(f"**Alama ya Chini:** {df[selected_col].min()}")
            
        # 3. Kitufe cha Kudownload PDF
        # Kwa Streamlit, unaweza kusave picha moja kwa moja
        fn = 'Test2_Report.pdf'
        plt.savefig(fn)
        with open(fn, "rb") as img:
            btn = st.download_button(
                label="Download Visual Representation as PDF",
                data=img,
                file_name=fn,
                mime="application/pdf"
            )

    except Exception as e:
        st.error(f"Kuna tatizo: {e}")
else:
    st.info("Tafadhali pakia faili la Excel upande wa kushoto (Sidebar) ili kuanza.")