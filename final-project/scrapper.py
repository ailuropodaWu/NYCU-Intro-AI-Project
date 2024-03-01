import requests as rq
import json
import numpy as np
import pickle
import pandas as pd
import datetime as dt
import random
from tqdm import tqdm
from time import sleep
from bs4 import BeautifulSoup
import argparse

def get_data(start_year, duration=2, start_month=1, end_month=12):
    api_key = '7WbEbXuv03iEqV787tweGzUqZXXgtHDg' # NYTimes API key
    train_test_split = 0.8 # ratio of train data and test data
    full_data = [] 
    path = './dataset' # folder to save the datasets
    data_scrap = False

    if data_scrap:
        print("##### Data Scrapping #####")
        for year in tqdm(range(start_year, start_year + duration)):
            for month in tqdm(range(start_month, end_month+1)):
                req = rq.get(f"https://api.nytimes.com/svc/archive/v1/{year}/{month}.json?api-key={api_key}")
                sleep(12)
                full_data += req.json()["response"]["docs"]
        full_data = pd.DataFrame(full_data)
        full_data.to_pickle(f'{path}/full_nytimes.pkl')
    else:
        full_data = pd.read_pickle(f'{path}/full_nytimes.pkl')



    print('##### Train-Test Splitting #####')
    print(f'Train-test split rate: {train_test_split}')
    train_data = []
    test_data = []
    train_cnt = full_data.size * train_test_split // 1

    for _, row in tqdm(full_data.iterrows()):
        if random.uniform(0, 1) < train_test_split and train_cnt > 0:
            train_data.append(row)
            train_cnt -= 1
        else:
            test_data.append(row)
    
    train_data = pd.DataFrame(train_data)
    test_data = pd.DataFrame(test_data)
    train_data = train_data.reset_index().drop(columns=['index'])
    test_data = test_data.reset_index().drop(columns=['index'])
    print(f'##### Get {len(train_data)} Train Data #####')
    print(f'##### Get {len(test_data)} Test Data #####')

    train_data = process(train_data)
    test_data = process(test_data)
    train_data.to_pickle(f'{path}/train.pkl')
    test_data.to_pickle(f'{path}/test.pkl')
    return train_data, test_data

def process(data):
    
    print('##### Proccessing the Data #####')

    print("Pub date...")
    pub_year = []
    pub_month = []
    pub_date = []
    pub_weekday = []
    pub_time = []
    for date in tqdm(data['pub_date']):
        date = pd.to_datetime(date)
        pub_year.append(date.year)
        pub_month.append(date.month)
        pub_date.append(date.day)
        pub_weekday.append(date.weekday())
        pub_time.append(date.hour)

    print('Abstract...')
    abstract = []
    abstract_len = []
    abstract_dup = []
    dup = data[data['abstract'].duplicated()]['abstract'].value_counts()
    for abs in tqdm(data['abstract']):
        try:
            abstract_dup.append(dup[abs])
        except:
            abstract_dup.append(0)
        abstract.append(abs)
        abstract_len.append(len(abs.split(' ')))

    print('Headline...')
    headline = []
    headline_len = []
    headline_dup = []
    headline_kicker = []
    for i in tqdm(data['headline']):
        headline.append(i['main'])
        headline_len.append(len(i['main'].split(' ')))
        headline_kicker.append(i['kicker'])
    data['headline'] = headline

    dup = data[data['headline'].duplicated()]['headline'].value_counts()
    for i in tqdm(data['headline']):
        try:
            headline_dup.append(dup[i])
        except:
            headline_dup.append(0)

    print('Lead paragraph...')
    len_lead = [len(i.split(' ')) for i in tqdm(data['lead_paragraph'])]

    print('Keywords...')
    keywords = []
    for i in tqdm(data['keywords']):
        keywords.append([k['value'] for k in i])
    
    print('Author...')
    authors = []
    for i in tqdm(data['byline']):
        try :
            authors.append([p['firstname'] + ' ' + p['middlename'] + ' ' + p['lastname'] for p in i['person']])
        except:
            authors.append([p['firstname'] + ' ' + p['lastname'] for p in i['person']])

    data = data.drop(columns=['abstract', 'snippet', 'lead_paragraph', 'source', 'pub_date',\
        'multimedia', 'headline', 'keywords','document_type', 'byline', '_id', 'uri'])
    data = data.assign(pub_year = pub_year, pub_month = pub_month, pub_date = pub_date, pub_weekday = pub_weekday, pub_time = pub_time, \
        abstract = abstract,  abstract_len  = abstract_len,  abstract_dup  = abstract_dup, headline  = headline, headline_len  = headline_len,  \
        headline_dup  = headline_dup,  headline_kicker  = headline_kicker, len_lead  = len_lead,  keywords  = keywords,  authors  = authors)

    return data

def get_comment_num(data): # use nums of comment as label
    
    print('##### Scrapping Nums of Comment #####')
    urls = data['web_url']
    n_comment = []
    for url in tqdm(range(len(urls))):
        
        try:
            n_comment.append(rq.get(
                    url='https://www.nytimes.com/svc/community/V3/requestHandler',
                    params={
                        'cmd': 'GetCommentsAll',
                        'url': urls[url],
                        'limit': 100,
                        'sort': 'oldest',
                        'offset': 0
                    },
                ).json()['results']['totalParentCommentsFound'])
        except:
            n_comment.append(-1)
    data = data.assign(n_comment= n_comment)
    data.drop(data.iloc(data['n_comment'] == -1))

    return data

if __name__ == '__main__':
    label_path = './dataset/label'
    train_data, test_data = get_data(2021)
    train_data = get_comment_num(train_data)
    test_data = get_comment_num(test_data)
    train_data.to_pickle(f'{label_path}/train.pkl')
    test_data.to_pickle(f'{label_path}/test.pkl')