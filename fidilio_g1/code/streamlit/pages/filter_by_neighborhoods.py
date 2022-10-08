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
result = pd.merge(df_cafe, df_cafe_rating, on="cafe_id")


st.markdown("""# City & Neighborhoods
- In this page, you can choose city and number of cafes in a neighborhoods""")

df = result
minval=df['start datetime'].min().time()
maxval=df['end datetime'].max().time()



fav_num = st.selectbox(
    "Choose city", 
    list(df['city'].unique()),
)



appointment_time = st.slider(
    "Set minimun number of cafe in a neighborhood:",min_value=0, max_value=30,
    value=15
)


temp=df[df['city']==fav_num]['province'].value_counts()
neighborhood_list=list(temp[temp>appointment_time].index)




grouped=df[df['province'].isin(neighborhood_list)].groupby('province')
df1=grouped[['food_quality','service_quality','cost_y','cost_value','environment']].agg('mean')
try: 
    df1.drop(index=['Error'],inplace=True)
except:
    pass
df1 = df1.rename(columns={"environment": "Environment", "cost_value": "Cost Value", "cost_y": "Cost", "food_quality": "Food Quality", "service_quality": "Service Quality"})
st.dataframe(df1)
st.bar_chart(df1)