#t_26.4_v1

import sys
import re
from urllib.request import urlopen
from collections import Counter

P_ENC = r'\bcharset=(?P<ENC>.+)\b'
P_HEADER = r'<div class="article_header">.*?<a[^>]*>(?P<TITLE>.*?)</a>'
P_WORD = r'\b[А-ЯІЇЄҐ][а-яіїєґ]+\b'

def getencoding(http_file):
    headers = http_file.getheaders()
    dct = dict(headers)
    content = dct.get('Content-Type','')
    mt = re.search(P_ENC, content)
    if mt:
        enc = mt.group('ENC').lower().strip()
    elif 'html' in content:
        enc = 'utf-8'
    else:
        enc = None
    return enc

def extract_titles(html):
    titles = []
    for match in re.finditer(P_HEADER, html, re.DOTALL):
        title = match.group('TITLE').strip()
        if title:
            titles.append(title)
    return titles

def get_proper_nouns(text):
    return re.findall(P_WORD, text)

if __name__ == '__main__':
    if len(sys.argv) == 1:
        print("Використання: python script.py <дата у форматі ddmmyyyy>")
        print("Приклад: python script.py 01012024")
        sys.exit(1)

    date_str = sys.argv[1]
    url = f'http://www.pravda.com.ua/news/date_{date_str}/'

    http_file = urlopen(url)
    print("Status:", http_file.status)

    enc = getencoding(http_file)
    if not enc:
        enc = 'utf-8'

    html = http_file.read().decode(enc)

    titles = extract_titles(html)
    print(f"Знайдено {len(titles)} заголовків")

    all_words = []
    for title in titles:
        words = get_proper_nouns(title)
        all_words.extend(words)

    counter = Counter(all_words)
    print("\nНайчастіші теми / особистості:")
    for word, freq in counter.most_common(10):
        print(f"{word}: {freq}")
      
