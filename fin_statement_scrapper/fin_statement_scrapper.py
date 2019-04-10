# -*- coding: utf-8 -*-

"""Main module."""

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Mar 22 19:07:42 2019

@author: FR3D
"""

from requests import get
from bs4 import BeautifulSoup 
import pandas as pd
import numpy as np


from selenium import webdriver
from selenium.webdriver.common.keys import Keys


url = 'https://finance.yahoo.com/quote/AMZN/history?period1=1270357200&period2=1554354000&interval=1d&filter=history&frequency=1d'


def fin_scrapper(url):
    
    #set browser
    browser = webdriver.Firefox(executable_path=r'/Users/fr3d/Downloads/geckodriver')
    
    # Tell Selenium to get the URL you're interested in.
    browser.get(url)
    
    import time
    # Selenium script to scroll to the bottom, wait 30 seconds for the next batch of data to load, then continue             
    #scrolling.  It will continue to do this until the page stops loading new data.
    
    lenOfPage = browser.execute_script("window.scrollTo(0, document.body.scrollHeight);var lenOfPage=document.body.scrollHeight;return lenOfPage;")
    match=False
    while(match==False):          
        lastCount = lenOfPage
        time.sleep(20)
        lenOfPage = browser.execute_script("window.scrollTo(0, document.body.scrollHeight);var lenOfPage=document.body.scrollHeight;return lenOfPage;")
        if lastCount==lenOfPage:
            match=True
    
    # Now that the page is fully scrolled, grab the source code.
    source_data = browser.page_source
    
    # Throw your source into BeautifulSoup and start parsing!
    page_soup = BeautifulSoup(source_data)
    
    #get column headers
    headers = []
    for item in page_soup.find('thead').find('tr').find_all('th'):
        head = item.get_text()
        headers.append(head)
    
    #create a dataframe with appropriate column names
    df = pd.DataFrame(columns = headers)
    
    for table_row in page_soup.find('tbody').find_all('tr'):
        temp_row = []
        for row in table_row.find_all('td'):
            row2 = row.get_text()
            temp_row.append(row2)
            df_temp = pd.DataFrame(temp_row).transpose()
        df_temp.columns = headers
        df = df.append(df_temp)
    
    return df

df = fin_scrapper(url)



#%%

url = 'https://finance.yahoo.com/quote/AMZN/financials?p=AMZN'

response = get(url)
soup = BeautifulSoup(response.text, 'html.parser')

dummy = pd.DataFrame()

headers = []
for container in soup.find('tbody').find_all('tr'):
    data = []
    for item in container.find_all('td'):
        data.append(item.text)
        temp_df = pd.DataFrame(data)
    dummy = pd.concat([dummy,temp_df], axis = 1)

dummy.columns = dummy.iloc[0]
dummy = dummy.drop(0, axis = 0)

trail =pd.DataFrame(headers)
