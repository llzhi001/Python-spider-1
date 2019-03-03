import requests
from urllib.parse import urlencode
from requests.exceptions import ConnectionError
from pyquery import PyQuery as pq
import pymongo
from lxml.etree import XMLSyntaxError
from config import *

client = pymongo.MongoClient(MONGO_URL)
db = client[MONGO_DB]

base_url = 'http://weixin.sogou.com/weixin?'

headers = {
    'Cookie': 'CXID=8CAF4E587CC17A09DA2145C02577CCB8; SUID=BBE56F713865860A5BA23360000C71F5; IPLOC=CN4401; SUV=1537518650535173; pgv_pvi=8079042560; dt_ssuid=4406938300; ssuid=8448129448; pex=C864C03270DED3DD8A06887A372DA219231FFAC25A9D64AE09E82AED12E416AC; weixinIndexVisited=1; usid=6zjjNTZw68bAoXhd; SNUID=BD0F7F7E1015711DE19AB3C110B76C5A; ABTEST=8|1546065212|v1; JSESSIONID=aaa3asAoLZ-F1_7MfC7Cw; sct=9; ld=6kllllllll2bMlOylllllVZXp69llllltQ@UIlllllwlllll4ylll5@@@@@@@@@@; ppinf=5|1546067914|1547277514|dHJ1c3Q6MToxfGNsaWVudGlkOjQ6MjAxN3x1bmlxbmFtZToxODolRTUlOEYlQjYlRTclOTQlQjB8Y3J0OjEwOjE1NDYwNjc5MTR8cmVmbmljazoxODolRTUlOEYlQjYlRTclOTQlQjB8dXNlcmlkOjQ0Om85dDJsdUFFckNsSkFkWThqRC1wZjNETmh4YU1Ad2VpeGluLnNvaHUuY29tfA; pprdig=NoxIJbbU1lg24hLAXA4i9w4DcBmMm-TLOGbA15t3k791wJLHaHFL4jpyWEbFCRpfWY6_0eElfzCd_1NLlihyIimZb8KqqSzz2I2K48KqKuE_xNmPozyZe8N0IQ4VVnsG8w_facFAul3W-okLV3OafrhKRc9xkaHzQhzIxZrU-U4; sgid=22-38522007-AVwnH8rlgPoziaSzeUkYtxJc; ppmdig=1546067914000000a88033a47430cf625a0514b1bd1a5fec',
    'Host': 'weixin.sogou.com',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36'
}


proxy = None

def get_proxy():
    try:
        response = requests.get(PROXY_POOL_URL)
        if response.status_code == 200:
            return response.text
        return None
    except ConnectionError:
        return None


def get_html(url,count=1):
    print('Crawling',url)
    print('Trying count',count)
    global proxy
    if count >= MAX_COUNT:
        print('Tried too many counts')
        return None
    try:
        if proxy:
            proxies = {
                'http': 'http://' + proxy
            }
            response = requests.get(url, allow_redirects=False,headers=headers,proxies=proxies)
        else:
            response = requests.get(url, allow_redirects=False,headers=headers)
        if response.status_code == 200:
            return response.text
        if response.status_code == 302:
            print('302')
            proxy = get_proxy()
            if proxy:
                print('Using proxy ', proxy)
                count += 1
                return get_html(url,count)
            else:
                print('Get proxy failed')
                return None
    except ConnectionError as e:
        print('Error occurred ', e.args)
        proxy = get_proxy()
        count += 1
        return get_html(url,count)


def get_index(query,page):
    data = {
        'query':query,
        'type':2,
        'page':page,
        'ie':'utf8',
    }
    queries = urlencode(data)
    url = base_url + queries
    html = get_html(url)
    return html


def parse_index(html):
    doc = pq(html)
    items = doc('.news-box .news-list li .txt-box h3 a').items()
    for item in items:
        yield item.attr('href')


def get_detail(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.text
        return None
    except ConnectionError:
        return None


def parse_detail(html):
    try:
        doc = pq(html)
        title = doc('.rich_media_title').text()
        content = doc('.rich_media_content ').text()
        date = doc('#publish_time').text()
        nickname = doc('#js_profile_qrcode > div > strong').text()
        wechat = doc('#js_profile_qrcode > div > p:nth-child(3) > span').text()
        return {
            'title': title,
            'content': content,
            'date': date,
            'nickname': nickname,
            'wechat': wechat
        }
    except XMLSyntaxError:
        return None


def save_to_mongo(data):
    if db['articles'].update({'title': data['title']},{'$set': data},True):
        print('Saved to mongo ', data['title'])
    else:
        print('Saved to mongo failed ', data['title'])



def main():
    for page in range(1,101):
        html = get_index(KEYWORD,page)
        if html:
            article_urls = parse_index(html)
            for article_url in article_urls:
                article_html = get_detail(article_url)
                if article_html:
                    article_data = parse_detail(article_html)
                    print(article_data)
                    if article_data:
                        save_to_mongo(article_data)


if __name__ == '__main__':
    main()




