import streamlit as st
import requests, json
from bs4 import BeautifulSoup

from pandas import DataFrame
from numpy import std, median, NaN
import plotly.express as px
#import code.crawler

def combine_search_url(search, place=None):
    search = '-'.join(search.split(' '))
    if place:
        url_combine = 'https://www.ebay-kleinanzeigen.de' + '/s-' + place + '/' + search + '/k0'
    else:
        url_combine = 'https://www.ebay-kleinanzeigen.de' + '/s-' + search + '/k0'
    return url_combine

def get_ebay_page(search_url):

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.125 Safari/537.36 Edg/84.0.522.59',
    }
    # Gibt den HTML text der Website in eine Variable wieder.
    response = requests.get(url=search_url, headers=headers)
    #response = requests.get(ebay_url)
    return response

def get_ebay_page(search_url):

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.125 Safari/537.36 Edg/84.0.522.59',
    }
    # Gibt den HTML text der Website in eine Variable wieder.
    response = requests.get(url=search_url, headers=headers)
    #response = requests.get(ebay_url)
    if response.ok:
        print ('OK!')
    else:
        print ('Boo!')
    return response

def extract_search_results(soup):
    titles = []
    urls = []
    images = []
    places = []
    prices = []
    shipping = []
    srch = soup.find_all('li', class_="ad-listitem lazyload-item")
    for s in srch:
        #export titles
        try:
            title = s.find('a', class_="ellipsis")
            titles.append(title.text)
        except:
            titles.append('no title')

        #export links
        try:
            link = s.find('div', class_="aditem-image")
            urls.append(ebay_url + str(link.a['href']))
        except:
            urls.append(NaN)

        #export images
        #image = s.find('div', class_="imagebox srpimagebox" )
        #print(image)

        #export places
        try:
            place = s.find('div', class_="aditem-main--top--left")
            place_s = str(place.text).replace('\n', '')
            places.append(place_s)
        except:
            places.append(NaN)

        #export prices
        try:
            price = s.find('p', class_="aditem-main--middle--price-shipping--price")
            for p in price.text.split('\n'):
                if p != '':
                    prices.append(p.strip())
        except:
            prices.append(NaN)

        #export shipping prices
        try:
            ship = s.find('p', class_="aditem-main--middle--price-shipping--shipping")
            shipping.append(str(ship.text).replace('\n', ''))
        except:
            shipping.append(NaN)
    return titles, urls, images, places, prices, shipping


st.set_page_config(page_title='Kleinanzeigen crawler', page_icon='🖖')

st.sidebar.markdown("# Kleinanzeigen Crawler")
st.sidebar.markdown('After you type in the search string the crawler will show \
    a summary of results from ebay-kleinanzeigen and calculate the statistics of \
    prices for your search.')


search_string = st.text_input('Please input the search word(s)')

search_url = combine_search_url(search_string)

response = get_ebay_page(search_url)
soup = BeautifulSoup(response.text, "html.parser")

ebay_url = 'https://www.ebay-kleinanzeigen.de'
pagination = [search_url]
titles = []
urls = []
images = []
places = []
prices = []
shipping = []
VB_sign = []

titles_temp = []
urls_temp = []
images_temp = []
places_temp = []
prices_temp = []
shipping_temp = []
VB_sign_temp = []

if st.button('Search ebay-kleinanzeigen'):
    if search_string == '':
        st.write('Please, provide some words to search for.')
        st.stop()
    
    if soup.find('div', class_='outcomemessage-warning'):
        if 'Es wurden leider keine Ergebnisse' in soup.find('div', class_='outcomemessage-warning').text:
            st.write('No search results found. Please adjust your search.')
            st.stop()

    for s in soup.findAll('div', class_='pagination-pages'):
        pages = s.findAll('a', attrs={'class':"pagination-page"}, href=True)
        for a in pages:
            pagination.append(ebay_url+str(a["href"]))
    st.write('The crawler found {} pages'.format(len(pagination)+1))
    my_bar = st.progress(0)
    percent_complete = 100 // len(pagination)
    total_progress = 100 % len(pagination)
    
    for page in pagination:
        total_progress += percent_complete
        my_bar.progress(total_progress)
        response_page = get_ebay_page(page)
        #if response.ok:
        #    st.write('Search running for {}...'.format(page))
        soup_temp = BeautifulSoup(response_page.text, "html.parser")
        #print(soup_temp)
        titles_temp, urls_temp, images_temp, places_temp, prices_temp, shipping_temp = extract_search_results(soup_temp)
        #print(titles_temp)
        titles.extend(titles_temp)
        urls.extend(urls_temp)
        images.extend(images_temp)
        places.extend(places_temp)
        prices.extend(prices_temp)
        shipping.extend(shipping_temp)

    df = DataFrame(list(zip(titles, urls, prices, places, shipping)),
                    columns =['Title', 'URL', 'Price', 'Place', 'Shipping possible'])
    df['VB possible'] = [1 if 'VB' in x else 0 for x in df['Price'].astype('str')]

    replace_dic = {' € VB': '', 
            'Zu verschenken':'0', 
            ' €': '',
            'VB': '0'}

    df['Price_int'] = df['Price'].replace(replace_dic, regex=True).astype('Int64')

    fig = px.histogram(
        df,
        x="Price_int",
        labels={'Price_int': 'Prices, €'}
        )
    fig.update_layout(yaxis_title="Number of articles found") 
    fig.update_traces(xbins_size = 10)
    

    tab1, tab2 = st.tabs(["Result statistics", "Distribution of prices"])
    with tab1:
        st.write('Among {} prices the lowest price is {}, the highest price is {}.'.format(len(df), df.Price_int.min(), df.Price_int.max()))
        st.write('Average price for the search is {:.2f} +- {:.2f}'.format(df['Price_int'].mean(), df['Price_int'].std()))
        st.write('Median price for the search is {}'.format(df['Price_int'].median()))
        st.write('All results:')
        st.dataframe(df)
        
    with tab2:
        st.plotly_chart(fig, theme='streamlit', use_container_width=True)


