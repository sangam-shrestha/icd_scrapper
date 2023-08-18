#ICD-10 scrapper written by Sangam Shrestha
#Version history
#v1 - 8-18-2023 - initial version

import requests
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np

url = 'http://icd.who.int/browse10/2019/en'
reqs = requests.get(url)
soup = BeautifulSoup(reqs.text, 'html.parser')
 
urls = []
for link in soup.find_all('a'):
    print(link.get('href'))

tmp_ch = pd.DataFrame()    

#get the chapters data
chapter_url = 'https://icd.who.int/browse10/2019/en/JsonGetRootConcepts?useHtml=false'
chapters = requests.get(chapter_url).json()
chapter_IDS = [chapter['ID'] for chapter in chapters]
chapter_LABEL = [chapter['label'] for chapter in chapters]
key = []
label = []
for x in chapter_LABEL:
  k, l = x.split(' ', maxsplit = 1)
  key.append(k)
  label.append(l)
      
chapter_DICT = dict(zip(key, label))
#print(chapter_IDS)


section_url = 'https://icd.who.int/browse10/2019/en/JsonGetChildrenConcepts?ConceptId={}&useHtml=false'

for ch_ID in chapter_IDS:
  ch_label = chapter_DICT[ch_ID]
  print(ch_ID, ch_label)
  
  #get the sections data
  try:
    sections = requests.get(section_url.format(ch_ID)).json()
  except:
    time.sleep(5)
    sections = requests.get(section_url.format(ch_ID)).json()
  
  section_IDS = [section['ID'] for section in sections]
  section_LABEL = [section['label'] for section in sections]
  key = []
  label = []
  for x in section_LABEL:
    k, l = x.split(' ', maxsplit = 1)
    key.append(k)
    label.append(l)
      
  section_DICT = dict(zip(key, label))
  
  #print(section_IDS)
  
  tmp_sec = pd.DataFrame()
  for sec_ID in section_IDS:
    sec_label = section_DICT[sec_ID]
    
    print(sec_ID, sec_label)
    
    #get the category data
    try:
      inner_sections = requests.get(section_url.format(sec_ID)).json()
    except:
      time.sleep(5)
      inner_sections = requests.get(section_url.format(sec_ID)).json()
    
    inner_section_IDS = [section['ID'] for section in inner_sections]
    inner_section_LABEL = [section['label'] for section in inner_sections]
    key = []
    label = []
    for x in inner_section_LABEL:
      k, l = x.split(' ', maxsplit = 1)
      key.append(k)
      label.append(l)
      
    inner_section_DICT = dict(zip(key, label))
    #print(inner_section_IDS)
    
    tmp_inner = pd.DataFrame()
    for innersec_ID in inner_section_IDS:
      # get the subcategory data
      try:
        inner_sections_core = requests.get(section_url.format(innersec_ID)).json()
      except:
        time.sleep(5)
        inner_sections_core = requests.get(section_url.format(innersec_ID)).json()
      
      # stack the data
      sub_LABEL = [section['label'] for section in inner_sections_core]
      tmp1 = []
      tmp2 = []
      for x in sub_LABEL:
        k, l = x.split(' ', maxsplit = 1)
        tmp1.append(k)
        tmp2.append(l)
        
      tmp1.extend([innersec_ID])
      tmp2.extend([inner_section_DICT[innersec_ID]])
      tmp1 = np.vstack(tmp1)
      tmp2 = np.vstack(tmp2)
      inner_section_core_vals = np.hstack((tmp1, tmp2))
      #print(str(inner_section_core_vals))
      #tmp = pd.DataFrame(inner_section_core_vals)
      tmp_inner = pd.concat([tmp_inner, pd.DataFrame(inner_section_core_vals)])
    
    #print(tmp_inner)
    #merge the data together
    tmp_inner['section_ID'] = sec_ID
    tmp_inner['section_LABEL'] = sec_label
    tmp_sec = pd.concat([tmp_sec, tmp_inner])
    
  tmp_sec['chapter_ID'] = ch_ID
  tmp_sec['chapter_LABEL'] = ch_label
  tmp_ch = pd.concat([tmp_ch, tmp_sec])

file_final = tmp_ch.rename(columns={0:"icd10", 1:"icd10label"})
file_final.to_csv("B:\ICD\ICD-10\icd-10-who.csv", index = False)
