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


minval=df['start datetime'].min().time()
maxval=df['end datetime'].max().time()


st.markdown("""# Work Time & Rate
- in this page, you can choose range of work time and cities and them see rate of parameters.""")


cities = st.multiselect(
    "Choose city",
    list(df['city'].unique()),
    ("tehran")
)


appointment_time = st.slider(
    "set your desirable startand end work time:",min_value=minval, max_value=maxval,
    value=(time(10,0), time(23, 00))
)
minstart=str(appointment_time[0])
minstart=datetime.datetime.strptime(minstart, "%H:%M:%S").time()
maxend=str(appointment_time[1])
maxend=datetime.datetime.strptime(maxend, "%H:%M:%S").time()
grouped=df[(df['start']>=minstart)&(df['end']<=maxend)&(df['city'].isin(cities))].groupby('city')
df1=grouped[['food_quality','service_quality','cost_y','cost_value','environment']].agg('mean')
df1 = df1.rename(columns={"environment": "Environment", "cost_value": "Cost Value", "cost_y": "Cost", "food_quality": "Food Quality", "service_quality": "Service Quality"}, index={i: str(i).capitalize() for i in df1.index})
st.dataframe(df1)
st.bar_chart(df1)
