import streamlit as st

lab1=st.Page("lab1.py",title="Lab1")
lab2=st.Page("lab2.py",title="Lab2")
pg=st.navigation([lab2,lab1])
st.set_page_config(page_title="Multi page app",)
pg.run()