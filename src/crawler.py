import requests
from bs4 import BeautifulSoup
import scrapy

from pandas import DataFrame
from numpy import std, median, NaN
from matplotlib import pyplot as plt

def combine_search_url(search, place=None):
    search = '_'.join(search.split(' '))
    if place:
        url_combine = 'https://www.ebay-kleinanzeigen.de' + '/' 's0-' + place + '/' + search + '/k0'
    else:
        url_combine = 'https://www.ebay-kleinanzeigen.de' + '/' + search + '/k0'
    return url_combine

def get_ebay_page(search_url):

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.125 Safari/537.36 Edg/84.0.522.59',
    }
    # Gibt den HTML text der Website in eine Variable wieder.
    response = requests.get(url=search_url, headers=headers)
    #response = requests.get(ebay_url)
    return response