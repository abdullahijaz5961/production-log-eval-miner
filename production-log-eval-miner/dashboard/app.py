import streamlit as st
from eval_miner.core import EvalMiner
st.title('Eval Dataset Curation');m=EvalMiner();status=st.selectbox('Status',[None,'approved','review']);st.dataframe(m.cases(status))
