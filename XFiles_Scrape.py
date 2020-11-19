# X-Files Transcript Web Scraper

import requests
from bs4 import BeautifulSoup
import pandas as pd

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
            ep_name = cols[0].contents[0].string.strip()
            ep_num = cols[1].string
            ep_aired = cols[2].string
            # Episodes are classified as 'Mythos' or 'MOTW' (Monster of the Week)
            if ep_name[-1] == '*':
                ep_type = 'Mythos'
            else:
                ep_type = 'MOTW'
            ep_name = ep_name.strip('*').strip()

            ep_data = [ep_name, ep_num, ep_type, ep_aired, ep_trans]
            xfiles_eps.append(ep_data)

# Loop through transcripts

xfiles_lines = []
xfiles_scenes = []

# Test fewer episodes:
# xfiles_eps = xfiles_eps[5:7]

# For each episode
for ep in xfiles_eps:

    ep_url = URL + ep[4]
    ep_id = ep[1]
    print("Loading Episode: " + ep[0] + " " + ep_id)

    tr_html = requests.get(ep_url).content
    tr_soup = BeautifulSoup(tr_html, 'lxml')

    body = tr_soup.find('body')
    body = str(body)
    body_split = body.rsplit("[THE END]")[0]
    scenes = body_split.split("SCENE ")[1:]

    # For each scene
    for scene in scenes:

        scene_details = scene.split("<p>")[0].rsplit("<br/>")
        scene_num = "Scene " + scene_details[0].strip()
        scene_desc = ''.join(scene_details[1:]).replace('\n', ' ').strip()

        # Transcript not always structured uniformly
        # Below if statements help to capture leaks
        if '(' in scene_desc:
            try:
                context = scene_desc.split('(')[1].split(')')[0]
                scene_desc = scene_desc.split('(')[0] + scene_desc.split(')')[1]
            except:
                context = scene_desc.split('(')[1]
                scene_desc = scene_desc.split('(')[0]
            context = '(' + context + ')'

            caught_data = [ep_id, scene_num, "Context", "", context]
            xfiles_lines.append(caught_data)
        
        if '<b>' in scene_desc:
            s_text = scene_desc.split('<b>')[1].split(':</b>')
            if len(s_text) > 1:
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

        # For each line
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



# Export Data to CSV

eps_df = pd.DataFrame(data=xfiles_eps, columns=['Episode Name', 'Episode Number', 'Episode Type', 'Date Aired', 'Transcript URL'])
scenes_df = pd.DataFrame(data=xfiles_scenes, columns=['Episode Number', 'Scene Number', 'Scene Description'])
lines_df = pd.DataFrame(data=xfiles_lines, columns=['Episode Number', 'Scene Number', 'Line Type', 'Character Name', 'Script'])

eps_df.to_csv('X_Files_Episodes.csv', sep=',', index=False)
print("Episodes CSV created...")
scenes_df.to_csv('X_Files_Scenes.csv', sep=',', index=False)
print("Scenes CSV created...")
lines_df.to_csv('X_Files_Lines.csv', sep=',', index=False)
print("Lines CSV created...")