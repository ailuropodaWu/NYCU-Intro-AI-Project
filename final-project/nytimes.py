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

def get_data():
    api_key = '7WbEbXuv03iEqV787tweGzUqZXXgtHDg'
    data = []
    for year in tqdm(range(2020, 2021)):
        for month in tqdm(range(1, 2)):
            req = rq.get(f"https://api.nytimes.com/svc/archive/v1/{year}/{month}.json?api-key={api_key}")
            sleep(12)
            data += req.json()["response"]["docs"]
    
    pd.DataFrame(data).to_pickle('./nytimes-dataset/test.pkl')

def get_train_data(data_path = './nytimes-dataset/nytimes.pkl', num_train_data = 100):

    print('Access data from pickle')
    data = pd.read_pickle(data_path)
    pick_rate = num_train_data / len(data)
    print(f'Pick Rate : {pick_rate}')

    print('Pick the data to train')
    train_data = []
    for i, row in tqdm(data.iterrows()):
        if random.uniform(0,1) < pick_rate:
            train_data.append(row)
    train = pd.DataFrame(train_data)
    train = train.reset_index().drop(columns=['index'])
    print(f'Get {len(train)} Train Data')

    print('Proccess the pub data')
    pub_year = []
    pub_month = []
    pub_day = []
    pub_weekday = []
    pub_time = []
    for i in tqdm(train['pub_date']):
        i = pd.to_datetime(i)
        pub_year.append(i.year)
        pub_month.append(i.month)
        pub_day.append(i.day)
        pub_weekday.append(i.weekday())
        pub_time.append(i.hour)

    print('Proccess the abstract')
    abstract = []
    abstract_len = []
    abstract_dup = []
    dup = train[train['abstract'].duplicated()]['abstract'].value_counts()
    for i in tqdm(train['abstract']):
        try:
            abstract_dup.append(dup[i])
        except:
            abstract_dup.append(0)
        abstract.append(i)
        abstract_len.append(len(i.split(' ')))

    print('Proccess the headline')
    headline = []
    headline_len = []
    headline_dup = []
    headline_kicker = []
    for i in tqdm(train['headline']):
        headline.append(i['main'])
        headline_len.append(len(i['main'].split(' ')))
        headline_kicker.append(i['kicker'])
    train['headline'] = headline

    dup = train[train['headline'].duplicated()]['headline'].value_counts()
    for i in tqdm(train['headline']):
        try:
            headline_dup.append(dup[i])
        except:
            headline_dup.append(0)

    print('Proccess the lead_paragraph')
    len_lead = [len(i.split(' ')) for i in tqdm(train['lead_paragraph'])]

    print('Proccess the keywords')
    keywords = []
    for i in tqdm(train['keywords']):
        keywords.append([k['value'] for k in i])
    
    print('Proccess the authors')
    authors = []
    for i in tqdm(train['byline']):
        try :
            authors.append([p['firstname'] + ' ' + p['middlename'] + ' ' + p['lastname'] for p in i['person']])
        except:
            authors.append([p['firstname'] + ' ' + p['lastname'] for p in i['person']])

    train = train.drop(columns=['abstract', 'snippet', 'lead_paragraph', 'source', 'pub_date',\
        'multimedia', 'headline', 'keywords','document_type', 'byline', '_id', 'uri'])
    train = train.assign(pub_year = pub_year, pub_month = pub_month, pub_day = pub_day, pub_weekday = pub_weekday, pub_time = pub_time, \
        abstract = abstract,  abstract_len  = abstract_len,  abstract_dup  = abstract_dup, headline  = headline, headline_len  = headline_len,  \
        headline_dup  = headline_dup,  headline_kicker  = headline_kicker, len_lead  = len_lead,  keywords  = keywords,  authors  = authors)

    return train

def get_comment_num(train):
    
    print('Proccess the comment numbers')
    urls = train['web_url']
    n_comment = []
    for i in tqdm(range(len(urls))):
        
        try:
            n_comment.append(rq.get(
                    url='https://www.nytimes.com/svc/community/V3/requestHandler',
                    params={
                        'cmd': 'GetCommentsAll',
                        'url': urls[i],
                        'limit': 100,
                        'sort': 'oldest',
                        'offset': 0
                    },
                ).json()['results']['totalParentCommentsFound'])
        except:
            n_comment.append(-1)
    train = train.assign(n_comment= n_comment)
    # train.drop(train.iloc(train['n_comment'] == -1))

    return train

if __name__ == '__main__':
    data_src = 'nytimes'
    data_dst = 'train_v2'
    data_path = f'./nytimes-dataset/{data_src}.pkl'
    train_data_path = f'./nytimes-dataset/{data_dst}.pkl'
    #get_data()
    
    train = get_train_data(data_path, 40000)

    #train = pd.read_pickle(train_data_path)
    train = get_comment_num(train)

    train.to_pickle(train_data_path)