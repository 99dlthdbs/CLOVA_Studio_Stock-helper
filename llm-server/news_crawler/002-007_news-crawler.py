import requests
from urllib.parse import urlparse, urlencode, urlunparse, quote_plus, urljoin
from datetime import datetime, timedelta
from bs4 import BeautifulSoup as bs
from pymongo import MongoClient
import argparse
import time
import random
import pandas as pd
from fake_useragent import UserAgent
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

def parse_args():
    parser = argparse.ArgumentParser(description="MongoDB connection parameters")
    parser.add_argument('--host', type=str, required=True, help='MongoDB host address')
    parser.add_argument('--port', type=int, required=False, default=27017, help='MongoDB port number')
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

def create_session(headers):
    """
    세션을 생성하고 재시도 전략을 설정합니다.
    """
    session = requests.Session()
    retry_strategy = Retry(
        total=5,  # 총 재시도 횟수
        status_forcelist=[429, 500, 502, 503, 504],  # 재시도할 HTTP 상태 코드
        allowed_methods=["HEAD", "GET", "OPTIONS"],  # 재시도할 HTTP 메서드
        backoff_factor=1  # 재시도 간 대기 시간 (초)
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount('https://', adapter)
    session.mount('http://', adapter)
    session.headers.update(headers)
    return session

def fetch_news_data(params, session, url, db, query):
    duplicate_flag = 0
    no_news_flag = 0

    while duplicate_flag < 10:
        naver_news_links = []
        batch = []

        new_url = make_url(url, params)
        print(f"Fetching news list from: {new_url}")

        try:
            response = session.get(new_url, timeout=10)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching {new_url}: {e}")
            time.sleep(random.uniform(1, 3))
            continue

        soup = bs(response.content, 'html.parser')

        # URL을 절대 경로로 올바르게 구성
        naver_news_links = [a['href'][2:-2] for a in soup.find_all('a', string='네이버뉴스') if a['href']]

        if not naver_news_links:
            params['start'] = str(int(params['start']) + 10)
            print("No NAVER NEWS Platforms", no_news_flag)
            time.sleep(random.uniform(0.6, 1.0))
            no_news_flag += 1
            if no_news_flag > 2:
                break
            else:
                continue

        for link in naver_news_links:
            print("Processing link:", link)

            if 'sports' in link or 'entertain' in link:
                print("Skipping sports/entertainment link.")
                continue

            try:
                print(f"Fetching article from: {link}")
                article_res = session.get(link, timeout=10)
                article_res.raise_for_status()
            except requests.exceptions.RequestException as e:
                print(f"Error fetching {link}: {e}")
                time.sleep(random.uniform(1, 3))
                continue

            article_soup = bs(article_res.content, 'html.parser')

            # 제목 추출
            try:
                title = article_soup.select_one('#title_area > span').get_text(strip=True)
            except AttributeError:
                print("Title not found.")
                continue

            if query not in title:
                print("Query is not in the Title")
                time.sleep(random.uniform(0.6, 1.0))
                continue

            print("==========================================")
            print("query:", query)
            print("title:", title)

            # 언론사 추출
            press_select = article_soup.select_one('#ct > div.media_end_head.go_trans > div.media_end_head_top._LAZY_LOADING_WRAP > a > img.media_end_head_top_logo_img.light_type._LAZY_LOADING._LAZY_LOADING_INIT_HIDE')
            press = press_select['title'] if press_select and 'title' in press_select.attrs else 'Title attribute not found'
            print("press:", press)

            # 원문 URL 추출
            origin = article_soup.find("a", string='기사원문')
            origin_url = origin['href'] if origin and origin.has_attr('href') else 'No original URL'
            print("origin:", origin_url)

            # 날짜 추출
            date_tag = article_soup.select_one('#ct > div.media_end_head.go_trans > div.media_end_head_info.nv_notrans > div.media_end_head_info_datestamp > div:nth-child(1) > span')
            date = date_tag['data-date-time'] if date_tag and date_tag.has_attr('data-date-time') else 'No date found'
            print("date:", date)

            # 요약 추출
            summary_tag = article_soup.select_one('#dic_area > strong')
            summary = summary_tag.get_text(strip=True) if summary_tag else None
            print("summary:", summary)

            # 사진 관련 태그 제거
            for span in article_soup.find_all('span', class_='end_photo_org'):
                span.decompose()

            # 내용 추출
            content_tag = article_soup.select_one('#dic_area')
            content = content_tag.get_text(strip=True).replace("\n\n\n", "") if content_tag else 'No content found'

            if summary:
                index = content.find(summary)
                content = content[index + len(summary):] if index != -1 else content

            print("content:", content)
            print("==========================================")

            tmp = {
                'timestamp': datetime.strptime(date, "%Y-%m-%d %H:%M:%S") if date != 'No date found' else None,
                'query': query,
                'title': title,
                'press': press,
                'summary': summary,
                'content': content,
                'url': link,
                'origin': origin_url
            }
            batch.append(tmp)
            time.sleep(random.uniform(0.6, 1.0))

        if batch:
            urls = [news['url'] for news in batch]
            existing_news = db.news.find({"url": {"$in": urls}, "query": query})
            existing_urls = {news['url'] for news in existing_news}

            new_batch = [news for news in batch if news['url'] not in existing_urls]

            if new_batch:
                db.news.insert_many(new_batch)
                duplicate_flag = 0
                print(f"Inserted {len(new_batch)} new articles.")
            else:
                print("All batch data is duplicated", duplicate_flag)
                duplicate_flag += 1

        print("start:", params['start'])
        params['start'] = str(int(params['start']) + 10)
        time.sleep(random.uniform(0.6, 1.0))

def main(args):
    start_date = datetime.strptime(args.ds, "%Y.%m.%d")
    end_date = datetime.strptime(args.de, "%Y.%m.%d") + timedelta(days=1)
    ua = UserAgent()
    headers = {
        "User-Agent": ua.random
    }

    # 세션 생성
    session = create_session(headers)

    if args.port:
        client = MongoClient(args.host, args.port, username=args.username, password=args.password)
    else:
        client = MongoClient(args.host, username=args.username, password=args.password)

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
        fetch_news_data(params, session, url, db, args.query)
        current_date = next_date

    client.close()

if __name__ == "__main__":
    args = parse_args()
    start_time = time.time()

    jongmok = pd.read_csv('./set.csv')
    jongmok_list = jongmok['종목명']
    for j in jongmok_list:
        args.query = j
        main(args)

    print("Execution time: ", time.time() - start_time)
