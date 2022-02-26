#!/usr/bin/env python
# coding: utf-8

# In[47]:


import requests
from bs4 import BeautifulSoup
from time import sleep
import re
import boto3
import json
from botocore.config import Config

headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:94.0) Gecko/20100101 Firefox/94.0',
           'Accept-Language': 'en-US, en;q=0.5'}

# search_query = 'iphone'.replace(' ','+')
# base_url = 'https://www.amazon.in/s?k={0}'.format(search_query)


# Create a kinesis client
my_config = Config(  # Kinesis client configuration
    region_name='us-east-1',
    signature_version='v4',
    retries={
        'max_attempts': 10,
        'mode': 'standard'
    }
)
client = boto3.client('kinesis', config=my_config)  # Global kinesis client
counter = 0  # Global counter to count submitted records


def stream_records(items):
    for i in range(len(items)):
        record = dict()
        record["product_name"] = items[i][0]
        record["rating"] = items[i][1]
        record["total_rating_count"] = items[i][2]
        record["actual_price"] = items[i][3]
        record["product_url"] = items[i][4]

        response = client.put_record(
            StreamName="Ec2-Stream-Firehose",
            Data=json.dumps(record),  # dictionary as json convert to base64 encoded string
            PartitionKey=str(hash(record['product_name']))  # haser string upto 128 characters for
            # unique identification of each data blob
        )
        global counter
        counter = counter + 1

        print('Message sent #' + str(counter))

        # If the message was not sucssfully sent print an error message
        if response['ResponseMetadata']['HTTPStatusCode'] != 200:
            print('Error!')
            print(response)


def Scraper(base_url):
    total_pages = 1
    next_page = "Next"
    while next_page != "":
        response = requests.get(base_url + '&page={0}'.format(total_pages), headers=headers)
        soup = BeautifulSoup(response.content, 'html.parser')
        try:
            next_page = soup.find('a', {
                'class': 's-pagination-item s-pagination-next s-pagination-button s-pagination-separator'}).text
        except AttributeError:
            break
        total_pages += 1

    for page in range(1, total_pages + 1):
        # print('Processing {0}...'.format(base_url + '&page={0}'.format(page)))
        response = requests.get(base_url + '&page={0}'.format(page), headers=headers)
        soup = BeautifulSoup(response.content, 'html.parser')

        results = soup.find_all('div', {'class': 's-result-item', 'data-component-type': 's-search-result'})

        items = []  # collecting list of records in this list
        for result in results:
            product_name = result.h2.text
            # creating record of each product
            try:
                rating = result.find('i', {'class': 'a-icon'}).text
                total_rating_count = result.find('span', {'class': 'a-size-base'}).text
            except AttributeError:
                continue

            try:
                current_price = result.find('span', {'class': 'a-price-whole'}).text
                actual_price = result.find('span', {'class': 'a-price a-text-price'}).text
                actual_price = re.sub("^₹.*₹", "_", actual_price).strip("_")
                product_url = 'https://amazon.com' + result.h2.a['href']
                items.append([product_name, rating, total_rating_count, current_price, actual_price, product_url])
            except AttributeError:
                continue
        stream_records(items)  # calling function to push records to kinesis streams
        sleep(1.5)


# df = pd.DataFrame(items, columns=['product', 'rating', 'rating count', 'price1', 'price2', 'product url'])
# df.to_csv('{0}.csv'.format(search_query), index=False)


def itemlist(search_list):
    product_list = []
    for i in search_list:
        search_query = i.replace(' ', '+')
        base_url = 'https://www.amazon.in/s?k={0}'.format(search_query)
        Scraper(base_url)


if __name__ == '__main__':
    lst = open('itemlist.txt', "r", encoding='utf-8').readlines()
    list1 = []

    for i in lst:
        list1.append(i.strip())

    print(type(list1))
    X = itemlist(list1)





