import requests
from urllib.parse import urlparse, urlencode, urlunparse
from datetime import datetime
from bs4 import BeautifulSoup as bs
from pymongo import MongoClient
import argparse
import time
import random


def parse_args():
    parser = argparse.ArgumentParser(description="MongoDB connection parameters")
    parser.add_argument('--host', type=str, required=True, help='MongoDB host address') # 223.130.138.213
    parser.add_argument('--port', type=int, required=False, help='MongoDB port number') # 30001
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

def fetch_news_data(params, headers, url, db):
    total = []
    flag = 0
    while flag < 5:
        new_url = make_url(url, params)
        response = requests.get(new_url, headers=headers)
        soup = bs(response.content, 'html.parser')
        naver_news_links = []
        for a in soup.find_all('a', string='네이버뉴스'):
            if a['href']:
                naver_news_links.append(a['href'])
        if not naver_news_links:
            params['start'] = str(int(params['start']) + 10)
            flag += 1
            continue

        batch = []
        for link in naver_news_links:
            if 'sports' in link or 'entertain' in link:
                continue
            article_res = requests.get(link[2:-2])
            article_soup = bs(article_res.content, 'html.parser')
            title = article_soup.select_one('#title_area > span').get_text(strip=True)
            if params['query'] not in title:
                continue
            press_select = article_soup.select_one('#ct > div.media_end_head.go_trans > div.media_end_head_top._LAZY_LOADING_WRAP > a > img.media_end_head_top_logo_img.light_type._LAZY_LOADING._LAZY_LOADING_INIT_HIDE')
            press = press_select['title'] if 'title' in press_select.attrs else 'Title attribute not found'
            date = article_soup.select_one('#ct > div.media_end_head.go_trans > div.media_end_head_info.nv_notrans > div.media_end_head_info_datestamp > div:nth-child(1) > span')['data-date-time']
            summary = article_soup.select_one('#dic_area > strong').get_text(strip=True) if article_soup.select_one('#dic_area > strong') else None
            for span in article_soup.find_all('span', class_='end_photo_org'):
                span.decompose()
            content = article_soup.select_one('#dic_area').get_text(strip=True).replace("\n\n\n", "")
            if summary is not None:
                index = content.find(summary)
                content = content[index + len(summary):] if index != -1 else content
            tmp = {
                'date': date,
                'query': params['query'],
                'title': title,
                'press': press,
                'summary': summary,
                'content': content,
                'url': link[2:-2],
            }
            batch.append(tmp)
            print(date, link[2:-2])

        # 중복 여부 확인 및 저장
        existing_urls = db.news.find({"url": {"$in": [news['url'] for news in batch]}}).distinct("url")
        if existing_urls:
            batch = [news for news in batch if news['url'] not in existing_urls]
            if not batch:
                flag += 1
                continue
        else:
            flag = 0

        if batch:
            db.news.insert_many(batch)
            total.extend(batch)
        else:
            flag += 1

        params['start'] = str(int(params['start']) + 10)
        time.sleep(float(random.uniform(1, 2)))

    return total

def main(args):

    params = {
        'filed': '0',
        'is_dts': '0',
        'is_sug_officeid': '0',
        'office_category': '0',
        'office_section_code': '0',
        'service_area': '0',
        'query': args.query,
        'sort': '1',
        'start': '1',
        'where': 'news_tab_api',
        # 'nso': 'so:dd,p:all,a:all',
        'nso': f'so:dd,p:from{args.ds.replace(".", "")}to{args.de.replace(".", "")}',
        # 'pd': '0',
        'ds': args.ds,
        'de': args.de
    }
    url = 'https://s.search.naver.com/p/newssearch/search.naver'
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    }

    if args.port == '':
        client = MongoClient(args.host, username=args.username, password=args.password)    
    else:
        client = MongoClient(args.host, args.port, username=args.username, password=args.password)
    db = client[args.database]
    fetch_news_data(params, headers, url, db)

if __name__ == "__main__":
    args = parse_args()
    start = time.time()
    main(args)
    print("time: ", time.time() - start)
