import streamlit as st
import tomli_w
import PIL

col1, col2, col3, col4 = st.columns(4)
with col2:
    with open("./.streamlit/defaultTheme.txt", "r", encoding="utf-8") as f:
        if f.read().strip() == "Dark":
            st.image(PIL.Image.open("./.streamlit/pic/dark.png"), width=50)
        else:
            st.image(PIL.Image.open("./.streamlit/pic/light.png"), width=50)
        f.close()
with col1:
    st.title("Fidana")


st.markdown("""
[Fidilio](https://fidilio.com/) (فیدیلیو) is one of the best sites in Iran that allows you to find the best restaurant, confectionerie or coffee-shop.

Here in this project, we analysis data from this site and also you can personalization it and get best analysis.

Good Luck & Be Happy ! 🙂
""")

col_1, col_2, col_3 = st.columns(3)
with col_2:
    st.markdown("""
    ### Group members
    - Soroush Asgari
    - Amir Reza Moeini
    - Amir Mohammad Anvari
    ### Mentors
    - Mr. Sajjad
    - Mr. Ehsan
    - Mr. Poorya
    """)
with col_1:
    st.image(PIL.Image.open("./.streamlit/pic/restaurant.png"))
st.markdown("""Made with ❤️ by `Group 1` in `Quera Data Analysis Bootcamp`""")

with open("./.streamlit/defaultTheme.txt", "r", encoding="utf-8") as f:
    if f.read().strip() == "Dark":
        themeCode = 0
    else:
        themeCode = 1
    f.close()

if i := st.selectbox("Choose Theme", ["Dark", "Light"], index=themeCode):
    if i == "Dark":
        settings = {
            "theme": {
                "primaryColor": "#ff4b4b",
                "backgroundColor": "#0e1117",
                "secondaryBackgroundColor": "#262730",
                "textColor": "#fafafa",
                "font": "sans serif"
            }
        }
        with open("./.streamlit/defaultTheme.txt", "w", encoding="utf-8") as f:
            f.write("Dark")
            f.close()
    elif i == "Light":
        settings = {
            "theme": {
                "primaryColor": "#ff4b4b",
                "backgroundColor": "#ffffff",
                "secondaryBackgroundColor": "#f0f2f6",
                "textColor": "#31333f",
                "font": "sans serif"
            }
        }
        with open("./.streamlit/defaultTheme.txt", "w", encoding="utf-8") as f:
            f.write("Light")
            f.close()
    with open("./.streamlit/config.toml", "wb") as f:
        tomli_w.dump(settings, f)
        f.close()
