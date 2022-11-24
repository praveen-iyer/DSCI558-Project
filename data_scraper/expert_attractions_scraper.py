from bs4 import BeautifulSoup
import requests
import pandas as pd
import os

def get_about_dictionary(url):
    content = requests.get(url)
    soup = BeautifulSoup(content.content, 'html.parser')
    div = soup.find('div', attrs = {'class' : 'entry-content single-content'})
    content_list = []
    for p_tag in div:
        if p_tag.name == 'p':
            content_list.append(p_tag.get_text())
    heading = content_list[1:-1:2]
    about = content_list[2:-1:2]
    d = dict(zip(heading,about))
    return d

url1 = 'https://californiathroughmylens.com/strange-fun-attractions-list/'
url2 = 'https://californiathroughmylens.com/strange-unique-northern-california/'

d1 = get_about_dictionary(url1)
d2 = get_about_dictionary(url2)

d = d1 | d2
attraction_names, about_sections = list(d.keys()), list(d.values())
df = pd.DataFrame({'attraction_name': attraction_names, 'about': about_sections})

fname = os.path.join(os.path.dirname(__file__),"expert_attraction.csv")
df['ID'] = df.reset_index().index
df.to_csv(fname, index=False)