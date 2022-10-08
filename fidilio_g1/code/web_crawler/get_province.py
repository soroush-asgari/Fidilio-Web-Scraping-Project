# %%
import json
import re
import requests
from bs4 import BeautifulSoup
# %%
class wikipediaProvinceScraper():
    def __init__(self, link: str) -> None:
        self.rsp = requests.get(link)
        if self.rsp.status_code == 200:
            self.soup = BeautifulSoup(self.rsp.text, "html.parser")
        else:
            raise ValueError("Error !")
    def proces(self):
        self.mainLink = "https://fa.wikipedia.org/"
        self.pagesLink = []
        self.tags = self.soup.findAll("div", {"class": "CategoryTreeItem"})
        for i in self.tags:
            self.pagesLink.append(i.findNext("a")["href"])

        self.provinces = []
        for i in self.pagesLink:
            self.tempRsp = requests.get(self.mainLink + i)
            if self.tempRsp.status_code == 200:
                self.tempSoup = BeautifulSoup(self.tempRsp.text, "html.parser")
                self.tempTags = self.tempSoup.find("div", {"class": "mw-category-generated"}).findAll("div", {"class": "mw-category-group"})
                for category in self.tempTags:
                    self.liTags = category.findAll("li")
                    for li in self.liTags:
                        self.provinces.append(li.find("a")["title"])
            else:
                raise ValueError("Error !")

        return self.provinces
# %%
m = wikipediaProvinceScraper("https://fa.wikipedia.org/wiki/%D8%B1%D8%AF%D9%87:%D9%85%D8%AD%D9%84%D9%87%E2%80%8C%D9%87%D8%A7%DB%8C_%D8%AA%D9%87%D8%B1%D8%A7%D9%86_%D8%A8%D8%B1_%D9%BE%D8%A7%DB%8C%D9%87_%D9%85%D9%86%D8%B7%D9%82%D9%87")
mahaleh = (m.proces())
with open("./mahaleh.txt", "w", encoding="utf-8") as f:
    for i in mahaleh:
        f.writelines(i)
        f.writelines("\n")
    f.close()
# %%
with open("./data.json", "r", encoding="utf-8") as f:
    data = json.load(f)
# %%
class province():
    def __init__(self) -> None:
        with open("./stopWords.txt", "r", encoding="utf-8") as f:
            self.stopWords = f.read().splitlines()
            f.close()
        with open("./mahaleh.txt", "r", encoding="utf-8") as f:
            self.mahaleh = f.read().splitlines()
            f.close()
        with open("./reqCount.txt", "r+", encoding="utf-8") as f:
            self.reqCount = int(f.read())
            f.close()
        if self.reqCount >= 5000:
            raise ValueError(f"number of requests to api.neshan.org is more than 5000 !")

    def __del__(self):
        with open("./reqCount.txt", "w", encoding="utf-8") as f:
            f.write(str(self.reqCount))
            f.close()

    def getLngLat(self, url: str):
        rsp = requests.get(url)
        if rsp.status_code == 200:
            try:
                soup = BeautifulSoup(rsp.text, "html.parser")
                lat, long = soup.find("div", {"class": "map-container"}).find("a")["href"].split("/")[-1].split(",")
                return lat.strip(), long.strip()
            except:
                raise ValueError(f"Error in '{url}' for give lat, long !")
        else:
            raise ValueError(f"request to '{url}' || status code: {rsp.status_code}")

    
    def proces(self, address: str, name: str, link: str):
        apiCode = ""
        if len(address.strip()) == 0 or len(name.strip()) == 0 or len(link.strip()) == 0:
            raise ValueError(f"address: '{address}' is empty OR name: '{name}' is empty OR link: '{link}' is empty")
        else:
            if re.findall(r"\(\w+\)", name):
                return re.findall(r"\(\w+\)", name)[0].strip("(").strip(")")
            
            for word in self.stopWords:
                rePattern = re.compile(fr"{word.strip()}")
                address = rePattern.sub(" ", address)

            if "،" in address:
                address = address.split("،")
                if len(address[0].strip().split()) > 2:
                    if " ".join(address[0].split()[0:2]) not in self.mahaleh:
                        try:
                            lat, lng = self.getLngLat(link)
                            rsp = requests.get(f"https://api.neshan.org/v5/reverse?lat={lat}&lng={lng}", headers={"Api-Key": f"{apiCode}"})
                            self.reqCount += 1
                            if rsp.status_code == 200:
                                try:
                                    return rsp.json()["neighbourhood"]
                                except:
                                    return -1
                            else:
                                return f"status code: {rsp.status_code} from .neshan.org"
                        
                        except Exception as e:
                            return e

                    else:
                        return " ".join(address[0].split()[0:2])
                else:
                    if len(address[0].strip().split()) == 2:
                        if address[0].strip().split()[0] in self.mahaleh:
                            return address[0].strip().split()[0]
                        elif address[0].strip().split()[1] in self.mahaleh:
                            return address[0].strip().split()[1]
                        else:
                            try:
                                lat, lng = self.getLngLat(link)
                                rsp = requests.get(f"https://api.neshan.org/v5/reverse?lat={lat}&lng={lng}", headers={"Api-Key": f"{apiCode}"})
                                self.reqCount += 1
                                if rsp.status_code == 200:
                                    try:
                                        return rsp.json()["neighbourhood"]
                                    except:
                                        return -1
                                else:
                                    return f"status code: {rsp.status_code} from api.neshan.org"
                            
                            except Exception as e:
                                return e
                    else:
                        if address[0].strip() in self.mahaleh:
                            return address[0].strip()
                        else:
                            try:
                                lat, lng = self.getLngLat(link)
                                rsp = requests.get(f"https://api.neshan.org/v5/reverse?lat={lat}&lng={lng}", headers={"Api-Key": f"{apiCode}"})
                                self.reqCount += 1
                                if rsp.status_code == 200:
                                    try:
                                        return rsp.json()["neighbourhood"]
                                    except:
                                        return -1
                                else:
                                    return f"status code: {rsp.status_code} from api.neshan.org"
                            
                            except Exception as e:
                                return e
            else:
                return " ".join(address.split()[0:2])
# %%
p = province()
prov = []
for city in data:
    for coffee in data[city]:
        ans =  p.proces(data[city][coffee]["address"], coffee, data[city][coffee]["link"])
        prov.append(ans)
        data[city][coffee]["province"] = ans
        
del p # important!
# %%
def exportTojson(data):
    try:
        with open("./data.json", "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
    except:
        raise ValueError("Can Not Save !")
# %%
exportTojson(data)