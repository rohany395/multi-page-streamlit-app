import streamlit as st

lab1=st.Page("./lab/lab1.py",title="Lab1")
lab2=st.Page("./lab/lab2.py",title="Lab2")
lab3=st.Page("./lab/lab3.py",title="Lab3")
lab4=st.Page("./lab/lab4.py",title="Lab4")
lab5=st.Page("./lab/lab5.py",title="Lab5")
lab6=st.Page("./lab/lab6.py",title="Lab6")
pg=st.navigation([lab6,lab5,lab4,lab3,lab2,lab1])
st.set_page_config(page_title="Multi page app",)
pg.run()