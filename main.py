import sys
import time
import json
import requests
from bs4 import BeautifulSoup
import io
import csv

amz_base = "https://www.amazon.com"
# convert whitespace w/ `+` (urlencode)
search = sys.argv[1].replace(' ', '+')
amz_search = amz_base + "/s?k=" + search
amz_hdrs = {'User-agent': 'Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2062.120 Safari/537.36'}

r = requests.get(amz_search, headers=amz_hdrs)
soup = BeautifulSoup(r.text, 'lxml')

result_urls = []
for a in soup.findAll('a', class_='a-link-normal a-text-normal', href=True):
  if a.text:
    result_urls.append(a['href'])

books = []

with requests.Session() as s:
  for url in result_urls:
    full_url = amz_base + url
    print('results: item url', full_url)
    r = s.get(full_url, headers=amz_hdrs)
    soup = BeautifulSoup(r.text, 'lxml')

    book = {}
    book['title'] = soup.find('h1', id='title').contents[1].text.strip()
    book['url'] = amz_base + url
    author = soup.find('span', class_='author notFaded').find('a').text.strip()

    if 'Visit' in author:
      sentence = author.split()
      stop = ["Visit", "Amazon's", "Page"]
      resultwords = [word for word in sentence if word not in stop]
      author = ' '.join(resultwords)
      book['author'] = author
    else:
      book['author'] = author

    # print(book)

    # -- 'also bought' section

    # check if page has 'other users also bought' section
    try:
      similar = soup.find('div', id='p13n-m-desktop-dp-sims_purchase-similarities-sims-feature-1')
      similar = similar.find('div', class_='a-carousel-container').get('data-a-carousel-options')
      similar = json.loads(similar)

      url_bought_list = amz_base + similar['ajax']['url'] + '?' + 'asinMetadataKeys=' + similar['ajax']['params']['asinMetadataKeys'] + '&widgetTemplateClass=' + similar['ajax']['params']['widgetTemplateClass'] + '&linkGetParameters=' + similar['ajax']['params']['linkGetParameters'] + '&productDetailsTemplateClass=' + similar['ajax']['params']['productDetailsTemplateClass'] + '&forceFreshWin=' + str(similar['ajax']['params']['forceFreshWin']) + '&featureId=' + similar['ajax']['params']['featureId'] + '&reftagPrefix=' + str(similar['ajax']['params']['reftagPrefix']) + '&imageHeight=' + str(similar['ajax']['params']['imageHeight']) + '&faceoutTemplateClass=' + similar['ajax']['params']['faceoutTemplateClass'] + '&imageWidth=' + str(similar['ajax']['params']['imageWidth']) + '&auiDeviceType=' + similar['ajax']['params']['auiDeviceType'] + '&schemaVersion=' + str(similar['ajax']['params']['schemaVersion']) + '&relatedRequestID=' + similar['ajax']['params']['relatedRequestID'] + '&productDataFlavor=' + similar['ajax']['params']['productDataFlavor'] + '&maxLineCount=' + str(similar['ajax']['params']['maxLineCount']) + '&faceoutArgs=' + similar['ajax']['params']['faceoutArgs'] + '&count=' + '5' + '&offset=' + str(similar['set_size']) + '&asins=' + ','.join(similar['ajax']['id_list']) + '&_='

      # get json data from url
      rr = s.get(url_bought_list, headers=amz_hdrs)
      suggested_list = json.loads(rr.text)
      suggested_books = []

      def also_bought(data):
        for item in data.values():
          book = {}
          soup = BeautifulSoup(item[0], 'lxml')
          title_link = soup.find('a', href=True)
          book['title'] = title_link.contents[-2].text.strip()
          book['url'] = amz_base + title_link['href']
          book['author'] = soup.findAll('div', class_='a-row a-size-small')[0].contents[0].text.strip()
          suggested_books.append(book)

      also_bought(suggested_list)
      book['also-bought'] = suggested_books

    except Exception as e:
      print('suggested books, error:', e)
      book['also-bought'] = 'empty'

    # print(book)
    books.append(book)


def write_to_csv(fn, data):
  timestamp = time.strftime("%Y-%m-%d-%H%M%S")
  filename = fn + '_' + timestamp

  output = io.StringIO()
  f = csv.writer(open('dump/%s.csv' % filename, 'w'))
  f.writerow(['title', 'url', 'author', 'also-bought'])
  csv.writer(output, quoting=csv.QUOTE_NONNUMERIC)

  for item in data:
    f.writerow(item.values())


def write_to_json(fn, data):
  timestamp = time.strftime("%Y-%m-%d-%H%M%S")
  filename = fn + '_' + timestamp

  with open('dump/%s.json' % filename, 'w') as fp:
    json.dump(data, fp)


write_to_csv(search, books)
write_to_json(search, books)
