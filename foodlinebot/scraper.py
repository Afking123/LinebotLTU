from bs4 import BeautifulSoup
from abc import ABC, abstractmethod
import json
import requests
class rent(ABC):
 
    def __init__(self, area):
        self.area = area  # 地區
 
    @abstractmethod
    def scrape(self):
        pass
 
 

class rent591(rent):
 
    def scrape(self):
        headers = {'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36'}
        response = requests.get("https://buy.housefun.com.tw/region/"+self.area+"_c/?od=SeqUp",headers=headers)
        soup = BeautifulSoup(response.text, "html.parser")
        result = soup.find_all("h1",class_="casename",limit=5)
        ans=""
        for i in result:
            ans += i.text
        return str(ans)
