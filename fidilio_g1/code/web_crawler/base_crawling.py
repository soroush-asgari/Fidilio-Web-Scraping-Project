# %%
import requests
from bs4 import BeautifulSoup
import re
import json
from sqlalchemy import create_engine
import numpy as np
import pandas as pd
import datetime
import pymysql
#%%
user='user_group1'
password ='AWsWrGBjjyrA_group1'
db ='group1'    
host='45.139.10.138:80'
#%%
engine=create_engine(f"mysql+pymysql://{user}:{password}@{host}/{db}")
connection=engine.connect()
df_cafe=pd.read_sql("select cafe_name,city from cafe", connection)

# %%
def getCities(url: str) -> list:
    tempListOfCities = []
    rsp = requests.get(url)
    if rsp.status_code == 200:
        soup = BeautifulSoup(rsp.text, "html.parser")
        optinTags = soup.find("select", {"name": "filter-city"}).find_all("option")
        cities = []
        for i in optinTags:
            cities.append(i["value"])

        return cities
    else:
        raise ValueError(f"Status Code {[url]} : {rsp.status_code}")
# %%
url = "https://fidilio.com/coffeeshops/in/tehran/"
cities = getCities(url)
# %%
def getPageLinkAndSomeInformationOfEachCoffeeshops(cities: list) -> dict:
    webSiteurl = "https://fidilio.com/"
    coffeeshops = {}
    for city in cities:
        coffeeshops[city] = {}
        rsp = requests.get(f"https://fidilio.com/coffeeshops/in/{city}/")
        if rsp.status_code == 200:
            soup = BeautifulSoup(rsp.text, "html.parser")
            lastPageUrl = soup.find("div", {"class": "pagination"}).find_all("a")[-1]["href"]
            numberOfLastPage = int(re.search(r"\d+", re.search(r"\?p=\d+", lastPageUrl)[0])[0])
            for pageNumber in range(numberOfLastPage + 1):
                rsp = requests.get(f"https://fidilio.com/coffeeshops/in/{city}/?p={pageNumber}")
                if rsp.status_code == 200:
                    soup = BeautifulSoup(rsp.text, "html.parser")
                    listContainer = soup.find("div", {"class": "restaurant-list-container"})
                    if listContainer:
                        listOfCoffeeshops = listContainer.find_all("div", {"class": re.compile(r"restaurant-list-items.+")})
                        for coffeeshop in listOfCoffeeshops:
                            name = coffeeshop.find("div", {"class": "venue-title"})["title"]
                            if ((df_cafe['cafe_name'] == name) & (df_cafe['city'] == city)).any():
                                continue
                            link = coffeeshop.find("a")["href"]
                            imageLink = coffeeshop.find("div", {"class": "image"}).find("img")["src"]
                            try:
                                price_class = len(coffeeshop.find("span", {"class": "price-class"}).findAll("span", {"class": "active"}))
                            except:
                                price_class = -1
                            try:
                                rate = float(coffeeshop.find("span", {"class": "rate"}).find("div")["data-rateit-value"])
                            except:
                                rate = -1
                            try:
                                followers = int(re.findall(r"\d+", coffeeshop.find("span", {"class": "followers"}).text)[0])
                            except:
                                followers = -1
                                
                            coffeeshops[city][name] = {}
                            coffeeshops[city][name]["link"] = webSiteurl + link
                            coffeeshops[city][name]["imageLink"] = imageLink
                            coffeeshops[city][name]["price_class"] = price_class
                            coffeeshops[city][name]["rate"] = rate
                            coffeeshops[city][name]["followers"] = followers

                    else:
                        print("Coffe Shops Not Found !")
                        
                else:
                    print(f"https://fidilio.com/coffeeshops/in/{city}/?p={pageNumber} || Not Found !")

        else:
            print(f"https://fidilio.com/coffeeshops/in/{city}/ || Not Found !")

        
    return coffeeshops
# %%
simpleInformation = getPageLinkAndSomeInformationOfEachCoffeeshops(cities=cities)
# %%
def getAllOfInformation(data: dict) -> dict:
    for city in cities:
        for coffeeshop in data[city]:
            rsp = requests.get(data[city][coffeeshop]["link"])
            if rsp.status_code == 200:
                soup = BeautifulSoup(rsp.text, "html.parser")
                informationTag = soup.find("div", {"class": "informations-body"})
                if informationTag:
                    addressTag = informationTag.find("span", {"class": "note", "property": "address"})
                    if addressTag:
                        address = addressTag.text.strip()
                    else:
                        address = -1

                    try:
                        telephoneTag = informationTag.find("span", {"class": "note", "property": "telephone"}).find("a").text.strip()
                        telephone = telephoneTag
                    except:
                        telephone = -1

                    # Convert to time in sql :: select str_to_date("14:30:59", "%H:%i:%s");
                    try:
                        workHourTag = re.findall(r"(\d+:\d+|\d+)\-(\d+:\d+|\d+)", informationTag.find("i", {"class": "icon fa fa-lg fa-clock-o"}).findNext("span").findNext("span").text.strip())[0]
                        try:
                            workStart = workHourTag[0]
                        except:
                            workStart = -1
                        try:
                            workEnd = workHourTag[1]
                        except:
                            workEnd = -1
                    except:
                        workStart = -1
                        workEnd = -1

                    try:
                        featureList = []
                        describeTag = soup.find("div", {"class": "venue-description-panel"})
                        featureTag = describeTag.find("div", {"class": "venue-features-box"}).findAll("span")
                        for i in featureTag:
                            featureList.append(i.text)
                        
                    except:
                        featureList = []
                    

                    panelContainerTag = soup.find("div", {"class": re.compile(r"panel-container.+"), "id": "review-list"})
                    ratesTag = panelContainerTag.find("ul", {"class": "rates-list"}).findAll("li")
                    ratesList = ["foodQuality", "service", "cost-value", "environment"]
                    for i, rate in enumerate(ratesTag):
                        try:
                            data[city][coffeeshop][ratesList[i]] = round(float(rate.find("span", {"class": re.compile(r"\w+")}).find("div")["data-rateit-value"]))
                        except:
                            data[city][coffeeshop][ratesList[i]] = -1

                    data[city][coffeeshop]["address"] = address
                    data[city][coffeeshop]["telephone"] = telephone
                    data[city][coffeeshop]["workStart"] = workStart
                    data[city][coffeeshop]["workEnd"] = workEnd
                    data[city][coffeeshop]["featureList"] = featureList
                
                else:
                    print(f"{data[city][coffeeshop]['link']} Not Have Information Tag !")

            else:
                print(f"{data[city][coffeeshop]['link']} || Error !")

    return data
# %%
allInformation = getAllOfInformation(simpleInformation)
# %%
def exportTojson(data):
    try:
        with open("./data.json", "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
    except:
        raise ValueError("Can Not Save !")
# %%
exportTojson(allInformation)