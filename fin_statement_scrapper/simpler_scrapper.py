
from requests import get
from bs4 import BeautifulSoup 
import pandas as pd
import numpy as np

from selenium import webdriver
from selenium.webdriver.common.keys import Keys

from selenium.webdriver.common.action_chains import ActionChains
import time


browser = webdriver.Chrome()
base_url = 'https://www.macrotrends.net/stocks/charts/AMZN/amazon/financial-ratios'

browser.get(base_url)

search_field = browser.find_element_by_xpath('//*[@id="jqxInput"]')

source_data = browser.page_source
page_soup = BeautifulSoup(source_data)

temp_soup = page_soup.find('div', id = 'contenttablejqxgrid')

for link in temp_soup.find_all('a'):
    print('https://www.macrotrends.net' + link['href'])

browser.get('https://www.macrotrends.net/stocks/charts/AMZN/amazon/free-cash-flow-per-share')

link_soup = browser.page_source
link_soup = BeautifulSoup(link_soup)
link_soup = link_soup.find('table', class_='table')
link_soup


header = []
for item in link_soup.find('tr').find_all('th'):
    header.append(item.text)

    
for item in link_soup.find_all('th'):
    header.append(item.text)
header = header[-len(row_list[-1]):]
    
row_list = []
for row in link_soup.find_all('tr'):
    #print(row)
    item_list = []
    for item in row.find_all('td'):
        item_list.append(item.text)
    row_list.append(item_list)  




def ratios_scrapper(base_url):
    # Start web driver and go to base url
    browser = webdriver.Chrome()
    base_url = 'https://www.macrotrends.net/stocks/charts/AMZN/amazon/financial-ratios'
    browser.get(base_url)
    
    # Get search field element. This will be used to go to other pages
    search_field = browser.find_element_by_xpath('//*[@id="jqxInput"]')

    # Get all Links to financial ratios
    ratios_data = browser.page_source
    temp_soup = BeautifulSoup(ratios_data)
    ratios_soup = temp_soup.find('div', id = 'contenttablejqxgrid')
    
    # Get a list of all links
    links = []
    for link in ratios_soup.find_all('a'):
        new_link = 'https://www.macrotrends.net' + link['href']
        links.append(new_link)
    
    final_df = pd.DataFrame()
    
    # Go to each link and scrape data
    for page_link in links:
        browser.get(page_link)
        link_soup = browser.page_source
        link_soup = BeautifulSoup(link_soup)
        link_soup = link_soup.find('table', class_='table')
            
        if len(link_soup.find_all('tr')) < 10:
            df = pd.DataFrame()
            final_df = pd.concat([final_df, df], axis = 1)
        
        else:
            # Get table header
            header = []
            for item in link_soup.find_all('th'):
                header.append(item.text)
            # Get data from each row of table
            row_list = []

            for row in link_soup.find_all('tr'):
                #print(row)
                item_list = []
                for item in row.find_all('td'):
                    item_list.append(item.text)
                row_list.append(item_list)  

                # Make a dataframe from list
            df = pd.DataFrame(row_list, columns = header[-len(row_list[-1]):])
            df['Ticker'] = 'AMZN'
            df['Company_Name'] = 'Amazon'
            #header = header[-len(row_list[-1]):]
            final_df = pd.concat([final_df, df], axis = 1)
            time.sleep(1)
   
    return final_df
    
    
from selenium.webdriver.chrome.options import Options

options = Options()
options.headless = True

    
def fin_ratios_scrapper(ticker):
    # Initiate browser
    browser = webdriver.Chrome(options = options)
    
    # Base url
    base_url = 'https://www.macrotrends.net/stocks/charts/AMZN/amazon/financial-ratios'
    
    # Go to url
    browser.get(base_url)
    
    search_field = browser.find_element_by_css_selector('#jqxInput')
    search_field.send_keys(ticker+ ' ')
    time.sleep(.5)
    #search_field.send_keys(Keys.DOWN)
    search_field.send_keys(Keys.ENTER)
    
    page_data = browser.page_source
    page_soup = BeautifulSoup(page_data)
    
    page_data = browser.execute_script('return originalData')
    data_size = len(page_data)
    df = pd.DataFrame()
    for i in range(0,data_size):
        temp_data = page_data[i]
        date = [*temp_data.keys()][:-1]
        values = [*temp_data.values()][:-1]
        values[-1] = values[-1].split('>')[1].split('<')[0]
        temp_df = pd.DataFrame(values).T
        temp_df.columns = date
        df = df.append(temp_df)
    return df



def all_companies(list_of_tickers):
    
    final_df = pd.DataFrame()
    for ticker in list_of_tickers:
        ticker_df = fin_ratios_scrapper(ticker)
        ticker_df['ticker'] = ticker
        final_df = final_df.append(ticker_df)
        time.sleep(3)
    return final_df
        
    
list_of_tickers = ['AMZN','BAC']  






browser.get('https://www.macrotrends.net/stocks/stock-screener')

links = []
temp_soup = page_soup.find_all('table')
temp_soup
for link in page_soup.find_all('div', id = 'jqxGrid').find('a'):
    links.append(link['href'])

page_soup.find_all('a')

temp_soup

page_soup.find_all('a')


def get_ticker_links():
    url = 'https://www.macrotrends.net/stocks/stock-screener'
    browser = webdriver.Chrome()
    browser.get(url)
    page_data = browser.execute_script('return originalData')
    
    data_size = len(page_data)
    links = []
    tickers = []
    for i in range(0,data_size):
        temp_link = page_data[i]['name_link']
        tickers.append(page_data[i]['ticker'])
        temp_link = temp_link.split("href=\'")[1].split("'")[0]
        temp_link = temp_link.split('/')
        temp_link[-1] = 'financial-ratios'
        temp_link = '/'.join(temp_link)
        link = 'https://www.macrotrends.net' + temp_link
        links.append(link)
        
    df = pd.DataFrame()
    for link in links[:2]:
        browser.get(link)
        page_data = browser.execute_script('return originalData')
        data_size = len(page_data)
        for i in range(0,data_size):
            temp_data = page_data[i]
            date = [*temp_data.keys()][:-1]
            date = [x.split('-')[0] for x in date]
            values = [*temp_data.values()][:-1]
            values[-1] = values[-1].split('>')[1].split('<')[0]
            temp_df = pd.DataFrame(values).T
            temp_df.columns = date
            temp_df['Ticker'] = tickers[links.index(link)]
            df = df.append(temp_df)
        
    return df
    

    
    
    
