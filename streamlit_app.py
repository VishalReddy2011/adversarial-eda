import streamlit as st
import pandas as pd
from app.pipeline import run_analysis

st.set_page_config(page_title="Adversarial EDA POC", layout="centered")

st.title("Adversarial EDA POC")
st.write("Upload a CSV dataset to run an automated exploratory data analysis (EDA) pipeline powered by AI agents.")

uploaded_file = st.file_uploader("Upload CSV", type=["csv"])
show_execution_order = st.checkbox("Show execution order in report", value=False)

if uploaded_file is not None:
    # Preview the dataframe
    df = pd.read_csv(uploaded_file)
    st.write("### Data Preview")
    st.dataframe(df.head())

    if st.button("Run Analysis"):
        with st.spinner("Agents are analyzing your data. This may take a few minutes..."):
            try:
                pdf_bytes = run_analysis(
                    dataframe=df,
                    dataset_name=uploaded_file.name,
                    show_execution_order=show_execution_order
                )
                
                st.success("Analysis complete!")
                
                st.download_button(
                    label="Download PDF Report",
                    data=pdf_bytes,
                    file_name=f"{uploaded_file.name}.report.pdf",
                    mime="application/pdf"
                )
            except Exception as e:
                st.error(f"An error occurred during analysis: {e}")
