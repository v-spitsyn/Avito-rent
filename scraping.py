from bs4 import BeautifulSoup
import requests
from fake_useragent import UserAgent
import time
import math
from scipy.stats import expon
import pickle
import datetime



search = 'https://www.avito.ru/moskva/kvartiry/sdam/na_dlitelnyy_srok?p={}&f=550_5702-5703'
first_page = search.format('1')
first_response = requests.get(first_page, 
                              headers={'User-Agent': UserAgent().chrome})
first_source = first_response.content
first_soup = BeautifulSoup(first_source)
num_offers_text = first_soup.find('span', {'class': "page-title-count-2MiSQ"}).text
num_offers = int(num_offers_text.replace(' ', ''))
OFFERS_PER_PAGE = 50
num_pages = math.ceil(num_offers/OFFERS_PER_PAGE)

flat_links = []
for page_iter in range(1, num_pages+1):
    page = search.format(str(page_iter))
    page_response = requests.get(page,
                                 headers={'User-Agent': UserAgent().chrome})
    print(page_iter, page, page_response)
    page_source = page_response.content
    page_soup = BeautifulSoup(page_source)
    page_links_soup = page_soup.find_all('a', 
                                         {'class': "js-item-slider item-slider"})
    page_links = [it['href'] for it in page_links_soup]
    print(len(page_links))
    flat_links.extend(page_links)
    print(len(flat_links), len(set(flat_links)))
flat_links = list(set(flat_links))

price_tags = {'rent': ('span',
                        {'class': "js-item-price"}),
              'currency': ('span',
                           {'itemprop': "priceCurrency"}),
}
seller_tags = {'landlord': ('div',
                            {'class': 'seller-info-name js-seller-info-name'}),
               'landlord_type': ('div',
                                 {'class': None})
}
place_tags = {'stations': ('span',
                            {'class': 'item-address-georeferences-item__content'}),
              'distances': ('span',
                            {'class': 'item-address-georeferences-item__after'}),
              'main_params': ('li',
                              {'class': 'item-params-list-item'}),
              'extra_params': ('li',
                               {'class': 'advanced-params-param-item'})                            
}
rest_tags = {'date': ('div',
                      {'class': "title-info-metadata-item-redesign"}),
             'address': ('span',
                          {'class': "item-address__string"}),
             'deal': ('div',
                      {'class': 'item-price-sub-price'})
}

flats = {}
count = 0
for link in flat_links[:100]:
    flat_id = link
    flat_response = requests.get('http://avito.ru'+link, 
                                 headers={'User-Agent': UserAgent().chrome})
    flat_source = flat_response.content
    flat_soup = BeautifulSoup(flat_source)
    print(count, 'avito.ru'+link, flat_response)
    header = flat_soup.find('span',
                            {'class': 'title-info-title-text'})
    try:
        print(header.text)
    except:
        print(None)
    flat_dict = {}
    try:
        flat_dict['header'] = header.text
    except:
        flat_dict['header'] = None
    for key in price_tags:
        soup = flat_soup.find(price_tags[key][0],
                              price_tags[key][1])
        try:
            flat_dict[key] = soup['content']
        except:
            flat_dict[key] = None
    seller_soup = flat_soup.find('div',
                                {'class': 'seller-info js-seller-info'})
    for key in seller_tags:
        try:
            flat_dict[key] = seller_soup.find(seller_tags[key][0],
                                              seller_tags[key][1]
                                             ).text      
        except:
            flat_dict[key] = None
    for key in place_tags:
        soup = flat_soup.find_all(place_tags[key][0],
                                  place_tags[key][1])
        try:
            flat_dict[key] = [it.text for it in soup]
        except:
            flat_dict[key] = None
    for key in rest_tags:
        soup = flat_soup.find(rest_tags[key][0],
                              rest_tags[key][1])
        try:
            flat_dict[key] = soup.text
        except:
            flat_dict[key] = None
    flats[flat_id] = flat_dict
    count = count + 1 
    time.sleep(expon.rvs(30, 10))
    
date = datetime.date.today()
with open('1room_flats_{}.pickle'.format(date.strftime('%d-%m-%y')), 'wb') as f:
    pickle.dump(flats, f)