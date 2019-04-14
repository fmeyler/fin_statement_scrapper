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
def data_scrapper(symbol):
    income_statement_url = 'https://finance.yahoo.com/quote/{}/financials?p={}'.format(symbol, symbol)
    balance_sheet_url = 'https://finance.yahoo.com/quote/{}/balance-sheet?p={}'.format(symbol,symbol)
    cash_flow_url = 'https://finance.yahoo.com/quote/{}/cash-flow?p={}'.format(symbol, symbol)

    def url_scrapper(url):
        url = url
        
        response = get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        dummy = pd.DataFrame()
        
        for container in soup.find('tbody').find_all('tr'):
            data = []
            for item in container.find_all('td'):
                data.append(str(item.text).replace(',',""))
                temp_df = pd.DataFrame(data)
            dummy = pd.concat([dummy,temp_df], axis = 1)
        
        dummy.columns = dummy.iloc[0]
        dummy = dummy.drop(0, axis = 0)
        dummy.replace('-',np.nan, inplace = True)
        dummy = dummy.dropna(axis = 1)
        
        columns = list(dummy.columns)
        cols_to_change = columns[1:]
        first_col = columns[0]
        dummy[cols_to_change] = dummy[cols_to_change].astype(int)
        dummy = dummy.rename(columns = {first_col:'Date'})
        
        return dummy
    
    fin_statement = url_scrapper(income_statement_url)
    balance_sheet = url_scrapper(balance_sheet_url)
    cash_flow = url_scrapper(cash_flow_url)
    
    df = pd.concat([fin_statement,balance_sheet,cash_flow],axis = 1)
    df = df.loc[:,~df.columns.duplicated()]
    
    return df

trail_df = data_scrapper(symbol= 'AMZN')

trail_df2 = trail_df.transpose().reset_index()
trail_df2.columns = trail_df2.iloc[0]
trail_df2.drop(0,axis = 0, inplace = True)
trail_df2.columns = [str(x)[-4:] for x in trail_df2.columns]
trail_df2[trail_df2.columns[1:]] = trail_df2[trail_df2.columns[1:]].astype(int)

df = data_scrapper('https://finance.yahoo.com/quote/AMZN/financials?p=AMZN')
df2 = data_scrapper('https://finance.yahoo.com/quote/AMZN/balance-sheet?p=AMZN')


dummy.dtypes
dummy['Profit_Margin'] = dummy['Net Income']/dummy['Total Revenue']


url2 = 'https://finance.yahoo.com/quote/AMZN/balance-sheet?p=AMZN'

columns = list(df.columns)
columns[1:]
df = df.rename(columns = {'Revenue':'Date'})
df2 = df2.rename(columns = {'Period Ending':'Date'})

df3 = pd.concat([df,df2],axis = 1)
df3 = df3.loc[:,~df3.columns.duplicated()]
