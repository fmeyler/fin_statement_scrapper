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

x = [1,2,3,4,5,6]
pd.Series(x).hist()

from selenium import webdriver
from selenium.webdriver.common.keys import Keys

url = 'https://www.macrotrends.net/stocks/charts/ACB/aurora-cannabis/financial-ratios'

url = 'https://finance.yahoo.com/quote/AMZN/history?period1=1270357200&period2=1554354000&interval=1d&filter=history&frequency=1d'


def fin_scrapper(url):
    
    #set browser
    browser = webdriver.Firefox(executable_path=r'/Users/fr3d/Downloads/geckodriver')
    browser =  webdriver.Firefox()
    
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
browser = webdriver.Chrome()
browser.get(url)
source_data = browser.page_source
page_soup = BeautifulSoup(source_data)

url = 'https://www.macrotrends.net/stocks/charts/AMZN/amazon/financial-ratios'

#%%

def fin_ratios_scrapper(ticker):
    # Initiate browser
    browser = webdriver.Chrome()
    
    # Base url
    base_url = 'https://www.macrotrends.net/stocks/charts/AMZN/amazon/financial-ratios'
    
    # Go to url
    browser.get(base_url)
    
    action = ActionChains(browser)
    action.click()
    action.perform()
    
    # Enter symbol in search box
    search_field = browser.find_element_by_css_selector('#jqxInput')
    search_field.send_keys(ticker+ ' ')
    time.sleep(.5)
    search_field.send_keys(Keys.DOWN)
    search_field.send_keys(Keys.ENTER)
    
    time.sleep(1)
    action.click()
    action.perform()
    
    # Find the lenght of years of financial ratios
    source_data = browser.page_source
    page_soup = BeautifulSoup(source_data)
    
    year_range = [x for x in str(page_soup.find('h2').text).replace('-',' ').split() if x.isdigit()]
    beginning_year = int(year_range[0])
    end_year = int(year_range[1])
    
    number_of_years = len(range(beginning_year, end_year))
    print(number_of_years)
        
    # click anyhere to hide ads
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
    
    time.sleep(2)
    
    # Click page to remove pop-up ads    
    action.click()
    action.perform()
    
    scroll_tab = browser.find_elements_by_css_selector('#jqxScrollThumbhorizontalScrollBarjqxgrid')

    
    if number_of_years > 6:
        
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
    else:
        ratio2 = []
        
    all_ratios = [a + b for a,b in zip(ratios,ratios2)]
    column_name = list(reversed(range(beginning_year, end_year)))
    
    df = pd.DataFrame(all_ratios, columns = column_name, index = ratio_titles)
    return df

#%%
start = time.time()
df = fin_ratios_scrapper(ticker = 'BAC')
end = time.time()

print(end-start)

df.to_excel('amazon_data.xls', index = False)


text = [x for x in str(page_soup.find('h2').text).replace('-',' ').split() if x.isdigit()]

#%%

def get_tickers(exchange):
    
    exchange_name = exchange.upper()
    
    # Get a list of all alphabets
    alphabets = [chr(i).upper() for i in range(ord('a'),ord('z')+1)]
    
    ticker_df = pd.DataFrame()
    
    # Loop over each page to extract ticker and company name
    for letter in alphabets:
        url = 'http://eoddata.com/symbols/{}/{}.htm'.format(exchange_name, letter)
    
        response = get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        ticker_and_names = []
        headers = []
        
        # Get a list of headers
        for title in soup.find('div', class_='cb').find('table', class_='quotes').find('tr').find_all('th'): 
            headers.append(title.text)
        
        # Get all tickers and company names from page  
        for interim_soup in soup.find('div', class_= 'cb').find_all('tr'):
            temp_container = []
            for tag in interim_soup.find_all('td'):
                temp_container.append(tag.text)
            ticker_and_names.append(temp_container[:2])
        
        temp_ticker_df = pd.DataFrame(ticker_and_names, columns = headers[:2]) 
        ticker_df = ticker_df.append(temp_ticker_df)
    ticker_df.dropna(inplace = True)
    
    return ticker_df
    
#%%
    
def all_companies(list_of_tickers):
    
    browser = webdriver.Firefox(executable_path=r'/Users/fr3d/Downloads/geckodriver')
    
    for ticker in list_of_tickers[:2]:
        ticker_df = fin_ratios_scrapper()
        






browser.get(url)

time.sleep(3)

# click anyhere to hide ads
search_field = browser.find_element_by_xpath('//*[@id="jqxInput"]')
search_field.send_keys('AMZN ')
search_field.send_keys(Keys.ENTER)

action = ActionChains(browser)
action.click()
action.perform()

# Scrap the initial visible pages
source_data = browser.page_source
page_soup = BeautifulSoup(source_data)


//*[@id="jqxInput"]







tag = soup.find('div').find('a')
tag['href']
