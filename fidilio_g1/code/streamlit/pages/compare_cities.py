from datetime import time, datetime
from cProfile import label
import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sqlalchemy import create_engine
from sqlalchemy import select
import datetime
import pymysql
import os
import json
import re

user='user_group1'
password ='AWsWrGBjjyrA_group1'
db ='group1'    
host='45.139.10.138:80'
@st.experimental_memo
def cafedf(table):
    engine=create_engine(f"mysql+pymysql://{user}:{password}@{host}/{db}")
    connection=engine.connect()
    if table=='cafe':
        df_cafe=pd.read_sql("select * from "+table, connection)

        df_cafe['start']=(pd.Timestamp('now').normalize() + df_cafe['work_start']).dt.time
        df_cafe['start datetime']=pd.to_datetime(df_cafe['start'],format="%H:%M:%S")
        df_cafe['end']=(pd.Timestamp('now').normalize() + df_cafe['work_end']).dt.time
        df_cafe['end datetime']=pd.to_datetime(df_cafe['end'],format="%H:%M:%S")
        df_cafe.drop(columns=['work_start','work_end'],inplace=True)
        return df_cafe
    else:
        df=pd.read_sql("select * from "+table, connection)
        return df

df_cafe=cafedf('cafe')
df_cafe_rating=cafedf('cafe_rating')
df = pd.merge(df_cafe, df_cafe_rating, on="cafe_id")



pathOfProject = (__file__.split("\\"))
del pathOfProject[-4:]
pathOfProject = "\\\\".join(pathOfProject)


with open(os.path.abspath(pathOfProject + "\\\\code\\\\streamlit\\\\.streamlit\\\\defaultTheme.txt"), "r", encoding="utf-8") as f:
    themeColor = f.read()
    f.close()


with open(os.path.abspath(pathOfProject + "\\\\code\\\\streamlit\\\\.streamlit\\\\plotColors.json"), "r", encoding="utf-8") as f:
    colors = json.load(f)
    colors = colors[themeColor]
    f.close()


st.markdown("""# Compare Cities
- In this page, you can compare cities based on scores in 5 main parameters.""")

col1, col2 = st.columns(2)


firstcity = col1.selectbox(
    "choose city?", 
    list(df['city'].unique()),key="10"
)

secondcity = col2.selectbox(
    "choose city?", 
    list(df['city'].unique()),key="100"
)


grouped=df[df['city'].isin([firstcity,secondcity])].groupby('city')
df1=grouped[['food_quality','service_quality','cost_y','cost_value','environment']].agg('mean')
df2=df1.T
df2[secondcity]=df2[secondcity]*-1
st.dataframe(df2.rename(index={i: (str(i).replace("_", " ").capitalize() if str(i).replace("_", " ").capitalize() != "Cost y" else "Cost") for i in df2.index}, columns={i: str(i).capitalize() for i in df1.index}))


plt.rcdefaults()
fig, ax = plt.subplots()
ax.barh([(str(i).replace("_", " ").capitalize() if str(i).replace("_", " ").capitalize() != "Cost y" else "Cost") for i in df2.index], df2[firstcity], align='center',label=str(firstcity).capitalize(),color='#FF6C00',alpha=0.8)
ax.barh([(str(i).replace("_", " ").capitalize() if str(i).replace("_", " ").capitalize() != "Cost y" else "Cost")  for i in df2.index], df2[secondcity], align='center',color='#FF6C00',label=str(secondcity).capitalize(),alpha=.4)
ax.legend()
ax.set_facecolor(colors["bg_plot"])
fig.set_facecolor(colors["bg_plot"])
ax.spines['top'].set_color('#BFBC00')
ax.spines['right'].set_color('#BFBC00')
ax.spines['left'].set_color('#BFBC00')
ax.spines['bottom'].set_color('#BFBC00')
ax.tick_params(axis="both", colors="#E0A301")
ax.set_xlabel("Rate", color="#E0A301")
plt.draw()
ax.set_xticklabels([(str(i.get_text()) if re.match(r"(^\d+)|(^\d+.\d+)", i.get_text()) else str(i.get_text())[1:]) for i in ax.get_xticklabels()], color="#E0A301")
st.pyplot(fig)