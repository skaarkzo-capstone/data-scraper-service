# Testing all the scraping tools
import requests
from bs4 import BeautifulSoup
import undetected_chromedriver as uc
import pandas as pd

# requests
response = requests.get("https://www.google.com")
if response.status_code == 200:
    print("Requests Works!")
    print(response)
else:
    print("Requests failed")

# bs4
html = "<html><head><title>Test</title></head><body><p>Hello, World!</p></body></html>"
soup = BeautifulSoup(html, "lxml")
print("BeautifulSoup is working properly!" if soup.title.string == "Test" else "BeautifulSoup test failed.")

# undetected-chromedriver
driver = uc.Chrome()
driver.get("https://www.google.com")
print("Undetected Chromedriver is working properly!")
driver.quit()

# pandas
data = {"Name": ["Alice", "Bob"], "Age": [25, 30]}
df = pd.DataFrame(data)
print("Pandas is working properly!\n", df)