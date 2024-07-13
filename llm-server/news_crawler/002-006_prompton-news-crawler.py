import requests
from urllib.parse import urlparse, urlencode, urlunparse
from datetime import datetime, timedelta
from bs4 import BeautifulSoup as bs
import argparse
import time
import random
import pandas as pd
import csv
import os


def parse_args():
    parser = argparse.ArgumentParser(description="News crawling parameters")
    parser.add_argument('--query', type=str, required=True, help='검색 쿼리')
    parser.add_argument('--ds', type=str, default=datetime.now().strftime("%Y.%m.%d"), help='시작 일시')
    parser.add_argument('--de', type=str, default=datetime.now().strftime("%Y.%m.%d"), help='종료 일시')
    return parser.parse_args()


def make_url(base_url, params):
    parts = urlparse(base_url)
    parts = parts._replace(query=urlencode(params, doseq=True))
    return urlunparse(parts)


def fetch_response(url, headers, retries=3):
    for _ in range(retries):
        try:
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                return response
            print(f"Connection Issue, status code: {response.status_code}")
        except requests.exceptions.Timeout:
            print("Timeout occurred, retrying...")
    return None


def parse_news_links(soup):
    return [a['href'][2:-2] for a in soup.find_all('a', string='네이버뉴스') if a['href']]


def split_after_200_chars(input_string):
    if len(input_string) <= 200:
        return input_string
    
    period_index = input_string.find('.', 200)
    
    if period_index == -1:
        return input_string
    
    return input_string[:period_index + 1]


def parse_article(article_res, query):
    article_soup = bs(article_res.content, 'html.parser')
    title = article_soup.select_one('#title_area > span').get_text(strip=True)

    if query not in title:
        return None

    if '부고' in title or '부음' in title or '인사' in title:
        return None

    press_select = article_soup.select_one(
        '#ct > div.media_end_head.go_trans > div.media_end_head_top._LAZY_LOADING_WRAP > a > img.media_end_head_top_logo_img.light_type._LAZY_LOADING._LAZY_LOADING_INIT_HIDE')
    press = press_select['title'] if 'title' in press_select.attrs else 'Title attribute not found'
    origin = article_soup.find("a", string='기사원문')['href']
    date = article_soup.select_one(
        '#ct > div.media_end_head.go_trans > div.media_end_head_info.nv_notrans > div.media_end_head_info_datestamp > div:nth-child(1) > span')['data-date-time']
    summary = article_soup.select_one('#dic_area > strong').get_text(strip=True) if article_soup.select_one(
        '#dic_area > strong') else None

    for span in article_soup.find_all('span', class_='end_photo_org'):
        span.decompose()

    content = article_soup.select_one('#dic_area').get_text(strip=True).replace("\n\n\n", "")

    if summary is not None:
        index = content.find(summary)
        content = content[index + len(summary):] if index != -1 else content

    content = split_after_200_chars(content)

    return {
        'timestamp': datetime.strptime(date, "%Y-%m-%d %H:%M:%S"),
        'query': query,
        'title': title,
        'press': press,
        'summary': summary,
        'content': content,
        'url': article_res.url,
        'origin': origin
    }


def fetch_news_data(params, headers, url, csv_writer, existing_titles, id_counter):
    duplicate_flag = 0
    no_news_flag = 0

    while duplicate_flag < 10:
        new_url = make_url(url, params)
        response = fetch_response(new_url, headers)

        if response is None:
            time.sleep(float(random.uniform(0.3, 0.4)))
            continue

        soup = bs(response.content, 'html.parser')
        naver_news_links = parse_news_links(soup)

        if not naver_news_links:
            params['start'] = str(int(params['start']) + 10)
            no_news_flag += 1
            if no_news_flag > 2:
                break
            else:
                continue

        batch = []
        for link in naver_news_links:
            if 'sports' in link or 'entertain' in link:
                continue

            article_res = fetch_response(link, headers)
            if article_res is None:
                continue
            
            try:
                news_data = parse_article(article_res, params['query'])
            except:
                news_data = None

            if news_data is None or (news_data['query'], news_data['title']) in existing_titles:
                continue
            
            print(news_data)

            news_data['ID'] = id_counter
            id_counter += 1
            batch.append(news_data)

        if batch:
            for news in batch:
                csv_writer.writerow(news)
                existing_titles.add((news['query'], news['title']))
            duplicate_flag = 0
        else:
            duplicate_flag += 1

        params['start'] = str(int(params['start']) + 10)
        time.sleep(float(random.uniform(0.3, 0.4)))
    
    return id_counter


def initialize_csv(csv_file):
    existing_titles = set()
    file_exists = os.path.isfile(csv_file)
    id_counter = 1

    if file_exists:
        with open(csv_file, mode='r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            for row in reader:
                existing_titles.add((row['query'], row['title']))
                id_counter = max(id_counter, int(row['ID']) + 1)

    f = open(csv_file, mode='a', newline='', encoding='utf-8-sig')
    fieldnames = ['ID', 'timestamp', 'query', 'title', 'press', 'summary', 'content', 'url', 'origin']
    csv_writer = csv.DictWriter(f, fieldnames=fieldnames)

    if not file_exists:
        csv_writer.writeheader()

    return csv_writer, existing_titles, f, id_counter


def main(args):
    start_date = datetime.strptime(args.ds, "%Y.%m.%d")
    end_date = datetime.strptime(args.de, "%Y.%m.%d") + timedelta(days=1)
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    }

    csv_file = 'news_data.csv'
    csv_writer, existing_titles, csv_file_handle, id_counter = initialize_csv(csv_file)

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
        id_counter = fetch_news_data(params, headers, url, csv_writer, existing_titles, id_counter)
        current_date = next_date

    csv_file_handle.close()


if __name__ == "__main__":
    args = parse_args()
    start_time = time.time()

    jongmok = pd.read_csv('./set.csv')
    jongmok_list = jongmok['종목명']
    for j in jongmok_list:
        args.query = j
        main(args)

    print("Execution time: ", time.time() - start_time)
