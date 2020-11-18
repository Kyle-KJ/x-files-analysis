# X-Files Transcript Web Scraper

import requests
from bs4 import BeautifulSoup

URL = 'http://www.insidethex.co.uk/'

req = requests.get(URL)
html = req.content
soup = BeautifulSoup(html, 'lxml')

xfiles_data = []

tables = soup.find_all('table')

# Select Seasons 1-9 and skip the films
tables = tables[2:7] + tables[8:-4]

for table in tables:
    rows = table.find_all('tr')
    for row in rows:
        title_col = row.find_all('th')
        if len(title_col) == 0:
            cols = row.find_all('td')
            ep_trans = cols[0].find_all('a')[0].get('href')
            ep_name = cols[0].contents[0].string
            ep_num = cols[1].string
            ep_aired = cols[2].string

            ep_data = [ep_trans, ep_name, ep_num, ep_aired]
            xfiles_data.append(ep_data)
            print(ep_data)
            
            

