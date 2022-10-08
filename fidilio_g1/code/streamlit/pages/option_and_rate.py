import json
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import sys
import os

st.markdown("""# Feature & Rate
- In this page, you can choose an option and them see rate of cafes in 3 caharts (Histogeram - Line - Pie).""")

col1, col2 = st.columns(2)
with col1:
    chooseOption = st.selectbox("Choose Option",[
    'hookah',
    'internet',
    'delivery',
    'smoking',
    'open_space',
    'live_music',
    'parking',
    'pos'])

with col2:
    choosePlot = st.multiselect("Choose Plot", [
        "Line-Chart", 
        "Histogeram", 
        "Pie"])



pathOfProject = (__file__.split("\\"))
del pathOfProject[-4:]
pathOfProject = "\\\\".join(pathOfProject)

sys.path.append(pathOfProject + "\\\\code\\\\db_orm")
from db_interface import *

connection = DBManager("user_group1", "AWsWrGBjjyrA_group1", "45.139.10.138:80", "group1")
res = connection.session.query(Cafe.rate, Cafe.cafe_id, Cafe.city, getattr(CafeFeatures, chooseOption)).select_from(Cafe).join(CafeFeatures, Cafe.cafe_id == CafeFeatures.cafe_id).filter((Cafe.rate != -1)).all()
li = []
for i, val in  enumerate(res):
    li.append(list(val))

df = pd.DataFrame(li)

sys.path.remove(pathOfProject + "\\\\code\\\\db_orm")
connection.session.close()

with open(os.path.abspath(pathOfProject + "\\\\code\\\\streamlit\\\\.streamlit\\\\defaultTheme.txt"), "r", encoding="utf-8") as f:
    themeColor = f.read()
    f.close()



with open(os.path.abspath(pathOfProject + "\\\\code\\\\streamlit\\\\.streamlit\\\\plotColors.json"), "r", encoding="utf-8") as f:
    colors = json.load(f)
    colors = colors[themeColor]
    f.close()


def ploting(theme: str, nameOfPlot: list):
    # data_1 = df[(df[nameOfOption] == 1) & (df["rate"] != -1)].loc[:, "rate"]
    data_1 = df[df[3] == 1][0]
    for i in nameOfPlot:
        st.write(i)
        if i == "Line-Chart":
            fig1, ax1 = plt.subplots()
            ax1.plot(data_1.index, data_1)
            fig1.set_facecolor(theme["bg_plot"])
            ax1.set_facecolor(theme["bg_plot"])
            ax1.set_xlim(xmin=0, xmax=data_1.shape[0])
            ax1.set_ylim(ymin=0, ymax=5)
            ax1.spines['top'].set_color('#BFBC00')
            ax1.spines['right'].set_color('#BFBC00')
            ax1.spines['left'].set_color('#BFBC00')
            ax1.spines['bottom'].set_color('#BFBC00')
            ax1.tick_params(axis="both", colors="#E0A301")
            ax1.grid()
            ax1.xaxis.grid(True, linestyle=":", color=theme["grid_plot"])
            ax1.yaxis.grid(True, linestyle=":", color=theme["grid_plot"])
            ax1.set_ylabel("Rate", color="#E0A301")
            st.pyplot(fig1)

        elif i == "Histogeram":
            fig, ax = plt.subplots()
            # Freedman–Diaconis rule
            bin = ((data_1.max() - data_1.min()) / (2 * (data_1.quantile(0.75) - data_1.quantile(0.25)) * np.power(data_1.shape[0], -1/3)))

            cm = plt.cm.get_cmap('Oranges')

            n, bins, patches = ax.hist(data_1, int(bin), density=False)
            bin_centers = 0.5 * (bins[:-1] + bins[1:])

            col = bin_centers - min(bin_centers)
            col /= max(col)

            for c, p in zip(col, patches):
                plt.setp(p, 'facecolor', cm(c))

            fig.set_facecolor(theme["bg_plot"])
            ax.set_facecolor(theme["bg_plot"])
            ax.set_xlim(xmin=0, xmax=5)
            ax.set_xticks([0, 0.5, 1, 1.5, 2, 2.5, 3, 3.5, 4, 4.5, 5])
            ax.spines['top'].set_color('#BFBC00')
            ax.spines['right'].set_color('#BFBC00')
            ax.spines['left'].set_color('#BFBC00')
            ax.spines['bottom'].set_color('#BFBC00')
            ax.tick_params(axis="both", colors="#E0A301")
            ax.grid()
            ax.xaxis.grid(True, linestyle=":", color=theme["grid_plot"])
            ax.yaxis.grid(True, linestyle=":", color=theme["grid_plot"])
            ax.set_xlabel("Rate", color="#E0A301")
            ax.set_ylabel("Count", color="#E0A301")
            st.pyplot(fig)
        
        elif i == "Pie":
            colorlist = ["red", "blue", "green"]
            tempData_1 = df[df[3] == 1].loc[:, [0, 2]]
            # st.write(df[df[3] == 1].loc[:, [0, 2]])
            # tempData_1 = df[(df[nameOfOption] == 1) & (df["rate"] != -1)].loc[:, ["rate", "city"]]
            tempData_0 = df[df[3] == 0].loc[:, [0, 2]]
            # tempData_0 = df[(df[nameOfOption] == 0) & (df["rate"] != -1)].loc[:, ["rate", "city"]]
            fig, (ax1, ax2) = plt.subplots(1, 2)
            fig.subplots_adjust(wspace=0.2)
            overall_ratios = [len(tempData_0) / (len(tempData_0) + len(tempData_1)) * 100, len(tempData_1) / (len(tempData_0) + len(tempData_1)) * 100]
            labels = ['Not\nHave', f'{str(chooseOption).capitalize()}']
            explode = [0.1, 0]
            angle = 120 * overall_ratios[0]
            patches, texts, autotexts = ax1.pie(overall_ratios, autopct='%1.1f%%', startangle=angle,
                                labels=labels, explode=explode, colors=plt.get_cmap("Oranges")(np.arange(100)*100))

            for text, color in zip(texts, colorlist):
                text.set_color(color)
            city_ratio = tempData_1[2].value_counts()
            city_ratio = (city_ratio / city_ratio.sum())
            age_ratios = city_ratio
            age_labels = city_ratio.index
            bottom = 1
            width = 0.5
            for j, (height, label) in enumerate(reversed([*zip(age_ratios, age_labels)])):
                bottom -= height
                bc = ax2.bar(0, height, width, bottom=bottom, color='#BFBC00', label=(str(label).capitalize()),
                            alpha= j / len(city_ratio))
                # ax2.bar_label(bc, labels=[f"{height:.0%}"], label_type='center', padding=2.5, fmt="%d", fontsize=6)

            threshold = 0.025
            for c in ax2.containers:
                labels = [str(round(v * 100, 2)) + "%" if v > threshold else "" for v in c.datavalues]    
                ax2.bar_label(c, labels=labels, label_type="center", color="#000000")
            ax2.set_title('Cities', color="white")
            ax2.legend(prop={'size': 8})
            ax2.axis('off')
            ax2.set_xlim(-3 * width, width)

            fig.set_facecolor(theme["bg_plot"])
            ax1.set_facecolor(theme["bg_plot"])
            fig.set_facecolor(theme["bg_plot"])
            ax2.set_facecolor(theme["bg_plot"])
            st.pyplot(fig)

ploting(colors, choosePlot)
