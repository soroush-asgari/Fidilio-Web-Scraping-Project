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

    elif table=='cafe_address':
        df=pd.read_sql("select * from "+table, connection)
        df['lat'].fillna(-1,inplace=True)
        df['lng'].fillna(-1,inplace=True)
        df['lat']=df['lat'].astype(np.float16)
        df['lng']=df['lng'].astype(np.float16)
        return df    
    else:
        df=pd.read_sql("select * from "+table, connection)
        return df

df_cafe=cafedf('cafe')
df_cafe_rating=cafedf('cafe_rating')
df_cafe_feature=cafedf('cafe_features')
df_cafe_address=cafedf('cafe_address')
df = pd.merge(df_cafe, df_cafe_rating, on="cafe_id")
df = pd.merge(df, df_cafe_feature, on="cafe_id")
df = pd.merge(df, df_cafe_address, on="cafe_id")





lst=['hookah','internet','delivery','smoking','open_space','live_music','parking','pos']


st.markdown("""# Find Your Favourite Cafe
- In this page, you can find your favourite cafe based on features that you love them and you can set range of rate for main parameters and also you can download data of cafes and see location of them on map.""")

col1, col2 = st.columns(2)


features = col1.multiselect(
    "Select your favourite cafe feature(s)",
    lst,
    ("internet")
)

city = col2.selectbox(
    "choose city?", 
    list(df['city'].unique()),key="10000"
)


col1, col2 ,col3 = st.columns(3)
food_quality = col1.slider(
    "set your food quality:",min_value=0, max_value=5,
    value=(0, 5)
)
a0=(df['food_quality']>=food_quality[0])&(df['food_quality']<=food_quality[1])




service_quality = col2.slider(
    "set your service quality:",min_value=0, max_value=5,
    value=(0, 5)
)
a1=(df['service_quality']>=service_quality[0])&(df['service_quality']<=service_quality[1])



cost_y=col3.slider(
    "set your cost_y:",min_value=0, max_value=5,
    value=(0, 5)
)

a2=(df['cost_y']>=cost_y[0])&(df['cost_y']<=cost_y[1])


col1, col2 ,col3 = st.columns(3)
cost_value=col1.slider(
    "set your cost value:",min_value=0, max_value=5,
    value=(0, 5)
)

a3=(df['cost_value']>=cost_value[0])&(df['cost_value']<=cost_value[1])


environment=col2.slider(
    "set your cost value:",min_value=0, max_value=5,
    value=(0, 5),key=500
)

a4=(df['environment']>=environment[0])&(df['environment']<=environment[1])





df['VAL'] = df.loc[:, features].prod(axis=1)
condition=(df['VAL']==1) & (df['city']==city)
desire_data=['cafe_name','city','province','phone_number','cafe_address','cost_x','start','end','food_quality','service_quality','cost_y','cost_value','environment']
df_final=df[a0&a1&a2&a3&a4&condition][desire_data]

col1, col2, col3 = st.columns(3)

download_file = col2.checkbox("If u want to Download data of your desirable cafes, check the box")
col1, col2, col3 = st.columns(3)
if download_file:
    col2.download_button(
        label = "Download data of your desirable cafes",
        data = df_final.to_csv().encode("utf-8-sig"),
        file_name = "random_numbers.csv",
        mime    = "text/csv",
        key="download agreement"
    )

else:
    try:
        st.dataframe(df_final.rename(columns={i: str(i).replace("_", " ").capitalize() for i in df_final.columns}).drop(["Cost x"], axis=1))
    except:
        st.dataframe(df_final)

'\n'
available_cities=(df['lat']!=-1)&(df['lng']!=-1)
df_map=df[a0&a1&a2&a3&a4&condition&available_cities][['lat','lng']]
df_map.columns = ["lat", "lon"]
st.map(df_map)