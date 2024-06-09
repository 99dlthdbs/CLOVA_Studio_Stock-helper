import requests
from urllib.parse import urlparse, urlencode, urlunparse
from datetime import datetime
from bs4 import BeautifulSoup as bs
import json
from pymongo import MongoClient
import argparse

def parse_args():
    parser = argparse.ArgumentParser(description="MongoDB connection parameters")
    parser.add_argument('--host', type=str, required=True, help='MongoDB host address') # 223.130.138.213
    parser.add_argument('--port', type=int, required=True, help='MongoDB port number') # 30001
    parser.add_argument('--username', type=str, required=True, help='MongoDB username') # root
    parser.add_argument('--password', type=str, default='financial', required=True, help='MongoDB password') # financial
    parser.add_argument('--database', type=str, required=True, help='MongoDB database name')
    parser.add_argument('--query', type=str, required=True, help='검색 쿼리')
    parser.add_argument('--ds', type=str, default=datetime.now().strftime("%Y.%m.%d.%H")+".00", help='시작 일시')
    parser.add_argument('--de', type=str, default=datetime.now().strftime("%Y.%m.%d.%H.%M"), help='종료 일시')
    return parser.parse_args()

def make_url(base_url, params):
    parts = urlparse(base_url)
    parts = parts._replace(query=urlencode(params, doseq=True))
    return urlunparse(parts)

def fetch_news_data(params, headers, url):
    total = []
    while True:
        new_url = make_url(url, params)
        response = requests.get(new_url, headers=headers)
        soup = bs(response.content, 'html.parser')
        naver_news_links = [a['href'] for a in soup.find_all('a', string='네이버뉴스') if a['href']]

        if not naver_news_links:
            break

        for link in naver_news_links:
            article_res = requests.get(link[2:-2])
            article_soup = bs(article_res.content, 'html.parser')
            title = article_soup.select_one('#title_area > span').get_text(strip=True)
            press = article_soup.select_one('#\\\"sp_nws23\\\" > div.\\\"news_wrap > div > div.\\\"news_info\\\" > div.\\\"info_group\\\" > a.\\\"info > span').get_text(strip=True)
            time = article_soup.select_one('#ct > div.media_end_head.go_trans > div.media_end_head_info.nv_notrans > div.media_end_head_info_datestamp > div:nth-child(1) > span')['data-date-time']
            summary = article_soup.select_one('#dic_area > strong').get_text(strip=True) if article_soup.select_one('#dic_area > strong') else None
            content = article_soup.select_one('#dic_area').get_text(strip=True).replace("\n\n\n", "")
            tmp = {
                'date_news': time,
                'query': params['query'],
                'title': title,
                'press': press,
                'summary': summary,
                'content': content,
                'url': link[2:-2],
            }
            total.append(tmp)


        params['start'] = str(int(params['start']) + 10)

    return total

def update_mongodb(args, data):
    if port != '':
        client = MongoClient(args.host, args.port, username=args.username, password=args.password)
    else:
        client = MongoClient(hostname, username=username, password=password)
    db = client[args.database]

    db.news.insert_many(data)

def main():
    args = parse_args()
    params = {
        'filed': '0',
        'is_dts': '0',
        'is_sug_officeid': '0',
        'nso': '&nso=so:dd,p:all,a:all',
        'office_category': '0',
        'office_section_code': '0',
        'service_area': '0',
        'query': args.query,
        'sort': '1',
        'start': '1',
        'where': 'news_tab_api',
        'nso': 'so:dd,p:all,a:all',
        'pd': '0',
        'ds': args.ds,
        'de': args.de
    }
    url = 'https://s.search.naver.com/p/newssearch/search.naver'
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    }
    news_data = fetch_news_data(params, headers, url)
    update_mongodb(args.host, args.port, args.username, args.password, args.database, news_data)

if __name__ == "__main__":
    main()
