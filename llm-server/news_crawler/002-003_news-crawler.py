import requests
from urllib.parse import urlparse, urlencode, urlunparse, quote_plus
from datetime import datetime, timedelta
from bs4 import BeautifulSoup as bs
from pymongo import MongoClient
import argparse
import time
import random


def parse_args():
    parser = argparse.ArgumentParser(description="MongoDB connection parameters")
    parser.add_argument('--host', type=str, required=True, help='MongoDB host address')
    parser.add_argument('--port', type=int, required=False, help='MongoDB port number')
    parser.add_argument('--username', type=str, required=True, help='MongoDB username')
    parser.add_argument('--password', type=str, default='financial', required=True, help='MongoDB password')
    parser.add_argument('--database', type=str, required=True, help='MongoDB database name')
    parser.add_argument('--query', type=str, required=True, help='검색 쿼리')
    parser.add_argument('--ds', type=str, default=datetime.now().strftime("%Y.%m.%d"), help='시작 일시')
    parser.add_argument('--de', type=str, default=datetime.now().strftime("%Y.%m.%d"), help='종료 일시')
    return parser.parse_args()

def make_url(base_url, params):
    parts = urlparse(base_url)
    parts = parts._replace(query=urlencode(params, doseq=True))
    return urlunparse(parts)

def fetch_news_data(params, headers, url, db):
    flag = 0
    while flag < 30:
        print(flag)
        naver_news_links = []
        batch = []

        new_url = make_url(url, params)
        response = requests.get(new_url, headers=headers)
        if response.status_code != 200:
            print("Connection Issue")
            time.sleep(float(random.uniform(0.3, 0.4)))
            continue

        soup = bs(response.content, 'html.parser')
        naver_news_links = [a['href'][2:-2] for a in soup.find_all('a', string='네이버뉴스') if a['href']]

        if not naver_news_links:
            params['start'] = str(int(params['start']) + 10)
            print("No NAVER NEWS Platforms")
            time.sleep(float(random.uniform(0.3, 0.4)))
            flag += 1
            continue

        for link in naver_news_links:
            print("link: ", link)

            if 'sports' in link or 'entertain' in link:
                continue

            article_res = requests.get(link)

            if article_res.status_code != 200:
                print("Connection Issue")
                time.sleep(float(random.uniform(0.3, 0.4)))
                continue

            article_soup = bs(article_res.content, 'html.parser')

            try:
                title = article_soup.select_one('#title_area > span').get_text(strip=True)
            except:
                print(article_soup.select_one('#title_area > span'))
                article_res = requests.get(link)
                article_soup = bs(article_res.content, 'html.parser')
                title = article_soup.select_one('#title_area > span').get_text(strip=True)

            if params['query'] not in title:
                print("Query is not in the Title")
                time.sleep(float(random.uniform(0.3, 0.4)))
                continue

            print("==========================================")
            print("query: ", args.query)
            print("title: ", title)
            press_select = article_soup.select_one('#ct > div.media_end_head.go_trans > div.media_end_head_top._LAZY_LOADING_WRAP > a > img.media_end_head_top_logo_img.light_type._LAZY_LOADING._LAZY_LOADING_INIT_HIDE')
            press = press_select['title'] if 'title' in press_select.attrs else 'Title attribute not found'
            print("link: ", link)
            print("press: ", press)
            date = article_soup.select_one('#ct > div.media_end_head.go_trans > div.media_end_head_info.nv_notrans > div.media_end_head_info_datestamp > div:nth-child(1) > span')['data-date-time']
            print("date: ", date)
            summary = article_soup.select_one('#dic_area > strong').get_text(strip=True) if article_soup.select_one('#dic_area > strong') else None
            print("summary: ", summary)

            for span in article_soup.find_all('span', class_='end_photo_org'):
                span.decompose()

            content = article_soup.select_one('#dic_area').get_text(strip=True).replace("\n\n\n", "")

            if summary is not None:
                index = content.find(summary)
                content = content[index + len(summary):] if index != -1 else content

            print("content: ", content)

            print("==========================================")
            tmp = {
                'news_date': date.split(" ")[0],
                'news_time': date.split(" ")[1],
                'query': params['query'],
                'title': title,
                'press': press,
                'summary': summary,
                'content': content,
                'url': link,
            }
            batch.append(tmp)
            time.sleep(float(random.uniform(0.3, 0.4)))

        if batch:
            urls = [news['url'] for news in batch]
            existing_news = db.news.find({"url": {"$in": urls}, "query": params['query']})
            existing_urls = {news['url'] for news in existing_news}

            new_batch = [news for news in batch if news['url'] not in existing_urls]

            if new_batch:
                db.news.insert_many(new_batch)
                flag = 0
            else:
                print("All batch data is Duplicated")
                flag += 1

        print("start: ", params['start'])
        params['start'] = str(int(params['start']) + 10)
        time.sleep(float(random.uniform(0.3, 0.4)))

def main(args):
    start_date = datetime.strptime(args.ds, "%Y.%m.%d")
    end_date = datetime.strptime(args.de, "%Y.%m.%d") + timedelta(days=1)

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    }

    if args.port == '':
        client = MongoClient(args.host, username=args.username, password=args.password)
    else:
        client = MongoClient(args.host, args.port, username=args.username, password=args.password)

    db = client[args.database]

    current_date = start_date
    while current_date < end_date:
        next_date = current_date + timedelta(days=1)
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
            'nso': f'so:dd,p:from{current_date.strftime("%Y%m%d")}to{current_date.strftime("%Y%m%d")}',
            'ds': current_date.strftime("%Y.%m.%d"),
            'de': current_date.strftime("%Y.%m.%d")
        }

        url = 'https://s.search.naver.com/p/newssearch/search.naver'
        fetch_news_data(params, headers, url, db)
        current_date = next_date

if __name__ == "__main__":
    args = parse_args()
    start = time.time()
    main(args)
    print("Execution time: ", time.time() - start)
