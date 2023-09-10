import requests
from bs4 import BeautifulSoup
import datetime

todays = datetime.date.today()
today = todays.strftime("%y.%m.%d")

webpage = requests.get("https://weather.naver.com/")
soup = BeautifulSoup(webpage.content, "html.parser")

temp = soup.select_one('.current').text
temp_ = temp.replace('\n', '')
location_name = soup.select_one('.location_name').text

sum = soup.select('.summary')
sums = []
for i in sum:
    sums.append(i.text)
sums_ = sums[0].replace('\n', ' ')



print(f"{today} {location_name}위치의 날씨를 전달하겠습니다.")
print(f"{temp_}이며, {sums_}!\n\n")


webpage = requests.get("https://news.daum.net/")
soup = BeautifulSoup(webpage.content, "html.parser")

links = soup.select('a.link_txt')

count = 0

print(f"오늘 {today}의 HEADLINE은")

for link in links:
    count += 1
    if count <= 5:
        headline = link.text.strip() 
        href = link.get('href') 

        print(f"{count}. {headline}")
        print(f"   {href}")

