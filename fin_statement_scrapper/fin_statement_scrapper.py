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
    df = df.transpose()
    df = df.loc[:,~df.columns.duplicated()]
    
    return df

df.columns = df.iloc[0,:]
df.drop('Date', axis = 0, inplace = True)


df.iloc[0,:]

def fin_ratios(df):
    
    #Net Profit margin
    df['Profit_Margin'] = df['Net Income']/df['Total Revenue']
    
    #ROE
    df['SE_lag'] = df['Total Stockholder Equity'].shift(-1).fillna(df['Total Stockholder Equity'])
    df['ROE'] = df['Net Income']/((df['Total Stockholder Equity'] + df['SE_lag'])/2)
    df.drop('SE_lag', axis = 1, inplace = True)
    
    #ROA
    df['TA_lag'] = df['Total Assets'].shift(-1).fillna(df['Total Assets'])
    df['ROA'] = df['Net Income']/((df['Total Assets'] + df['TA_lag'])/2)
    df.drop('TA_lag',axis = 1, inplace = True)
    
    #Financial Leverage
    df['Financial Leverage'] = df['ROE'] - df['ROA']
    
    #Earning Quality
    df['Earning Quality'] = df['Total Cash Flow From Operating Activities']/ df['Net Income']
    
    return df
 
    

#%%
from selenium.webdriver.common.action_chains import ActionChains
import time

browser = webdriver.Firefox(executable_path=r'/Users/fr3d/Downloads/geckodriver')
browser.get(url)
source_data = browser.page_source
page_soup = BeautifulSoup(source_data)

url = 'https://www.macrotrends.net/stocks/charts/AMZN/amazon/financial-ratios'

#%%

def fin_ratios_scrapper(url, current_year):
    
    latest_year = int(current_year)
    ending_year = latest_year - 14
    
    # Initiate browser
    browser = webdriver.Firefox(executable_path=r'/Users/fr3d/Downloads/geckodriver')
    
    # Go to url
    browser.get(url)
    
    time.sleep(3)
    
    # click anyhere to hide ads
    scroll_tab = browser.find_element_by_xpath('.//*[@id="jqxScrollThumbhorizontalScrollBarjqxgrid"]')
    action = ActionChains(browser)
    action.click()
    action.perform()
    
    # Scrap the initial visible pages
    source_data = browser.page_source
    page_soup = BeautifulSoup(source_data)
    
    # Get ratio names
    ratio_titles = []
    for tag in page_soup.find_all('div', class_='jqx-grid-cell jqx-item jqx-grid-cell-pinned'):
        ratio_titles.append(tag.text)
    ratio_titles = list(filter(None, ratio_titles))
    
    # Iterate over row tags and get all data
    ratios = []
    for number in range(0,20):
        temp_ratios = []
        for tag in page_soup.find('div',{'id':'row{}jqxgrid'.format(number)}).find_all('div',class_='jqx-grid-cell jqx-item'):
            temp_ratios.append(tag.text)
        # drop the last two elements in the list. This will prevent duplicates when page is horizontally    
        #scrolled
        
        ratios.append(temp_ratios[:-2])
    
    time.sleep(3)
    
    # Click page to remove pop-up ads    
    action.click()
    action.perform()
    
    # Scroll table to the right to expose data
    action.drag_and_drop_by_offset(scroll_tab,500,0).perform()
    
    # Get new bs results
    source_data = browser.page_source
    page_soup = BeautifulSoup(source_data)
    
    ratios2 = []
    for number in range(0,20):
        temp_ratios = []
        for tag in page_soup.find('div',{'id':'row{}jqxgrid'.format(number)}).find_all('div',class_='jqx-grid-cell jqx-item'):
            temp_ratios.append(tag.text)
        ratios2.append(temp_ratios)
        
    all_ratios = [a + b for a,b in zip(ratios,ratios2)]
    column_name = list(reversed(range(ending_year, latest_year)))
    
    df = pd.DataFrame(all_ratios, columns = column_name, index = ratio_titles)
    return df


#%%
start = time.time()
df = fin_ratios_scrapper(url, current_year = 2019)
end = time.time()

print(end-start)

df.to_excel('amazon_data.xls', index = False)

#%%

import matplotlib.pyplot as plt
plt.plot(df.loc['ROE - Return On Equity',:])
