# X-Files Transcript Web Scraper

import requests
from bs4 import BeautifulSoup

URL = 'http://www.insidethex.co.uk/'

req = requests.get(URL)
html = req.content
soup = BeautifulSoup(html, 'lxml')

xfiles_eps = []

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
            xfiles_eps.append(ep_data)

# Loop through transcripts

xfiles_lines = []
xfiles_scenes = []

xfiles_eps = xfiles_eps[5:7]

for ep in xfiles_eps:

    ep_url = URL + ep[0]
    ep_id = ep[2]
    print("Loading Episode: " + ep[1])

    tr_html = requests.get(ep_url).content
    tr_soup = BeautifulSoup(tr_html, 'lxml')

    body = tr_soup.find('body')
    body = str(body)
    body_split = body.rsplit("[THE END]")[0]
    scenes = body_split.split("SCENE ")[1:]

    for scene in scenes:

        scene_details = scene.split("<p>")[0].rsplit("<br/>")
        scene_num = "Scene " + scene_details[0].strip()
        scene_desc = ''.join(scene_details[1:]).replace('\n', ' ').strip()

        if '(' in scene_desc:
            context = scene_desc.split('(')[1].split(')')[0]
            context = '(' + context + ')'

            caught_data = [ep_id, scene_num, "Context", "", context]
            xfiles_lines.append(caught_data)
            
            scene_desc = scene_desc.split('(')[0] + scene_desc.split(')')[1]
        
        if '<b>' in scene_desc:
            s_text = scene_desc.split('<b>')[1].split(':</b>')
            s_char = s_text[0]
            s_line = s_text[1].strip()

            caught_data = [ep_id, scene_num, "Line", s_char, s_line]
            xfiles_lines.append(caught_data)

            scene_desc = scene_desc.split('<b>')[0]
        
        scene_desc = scene_desc.strip()

        scene_data = [ep_id, scene_num, scene_desc]

        xfiles_scenes.append(scene_data)

        scene_soup = BeautifulSoup(scene, 'lxml')
        paras = scene_soup.find_all('p')[1:]

        for para in paras:

            try:
                char_name = para.find('b').text
                char_name = char_name.split(':')[0] # Some bad data will be picked up here - consider filtering for names that appear more than once
                line_text = str(para).split('</b>')[1:]
                line_text = ''.join(line_text)
                line = line_text.replace('\n', ' ').split('</p>')[0].strip()
                line_type = "Line"

                line_data = [ep_id, scene_num, line_type, char_name, line]

                xfiles_lines.append(line_data)

            except:
                line_text = para.get_text()
                line = line_text.replace('\n', ' ').strip()
                line_type = "Context"

                line_data = [ep_id, scene_num, line_type, '', line]

                if line != '':
                    xfiles_lines.append(line_data)


print("\nLines Sample:")        
for i in range(15):
    print(xfiles_lines[i])


print("\nScenes Sample:")
for i in range(12):
    print(xfiles_scenes[i])
