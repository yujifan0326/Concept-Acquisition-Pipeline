import sqlite3
import requests
from bs4 import BeautifulSoup
import re
import time
import random
import urllib
import config
import json
import os

sess = requests.Session()
if config.snippet_source == 'google':
    sess.proxies.update(config.proxy)
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36'
tot_crawl = 0

def db_init():
    conn = sqlite3.connect(config.db)
    cursor = conn.cursor()
    cursor.execute('CREATE TABLE IF NOT EXISTS baidu (concept TEXT PRIMARY KEY NOT NULL, snippet TEXT NOT NULL)')
    cursor.execute('CREATE TABLE IF NOT EXISTS google (concept TEXT PRIMARY KEY NOT NULL, snippet TEXT NOT NULL)')
    cursor.execute('CREATE TABLE IF NOT EXISTS bing (concept TEXT PRIMARY KEY NOT NULL, snippet TEXT NOT NULL)')
    conn.commit()
    conn.close()
db_init()

def load_cookie():
    for cookie_path in config.cookie_paths:
        with open(cookie_path, 'r', encoding='utf-8') as f:
            cookie = json.load(f)
            for i in range(len(cookie)):
                sess.cookies.set(cookie[i]['name'], cookie[i]['value'])
load_cookie()

def update_cookie(cookie):
    for c in cookie.split('; '):
        c = c.split('=', 1)
        if len(c) == 2:
            sess.cookies.set(c[0], c[1])

def sleep(t):  # randomize the sleep time in [t, 1.5t)
    time.sleep(t+random.random()*t*0.5)

def clean(text):
    text = re.sub(r'\n|\r', '', text).strip()
    return text

def crawl_snippet_google(concept):
    res = []
    url = 'https://www.google.com/search?gws_rd=cr&q={}'.format(concept)
    headers = {'user-agent': USER_AGENT, 'referer': 'https://www.google.com/'}
    page = sess.get(url, headers=headers)
    if 'Set-Cookie' in page.headers:
        update_cookie(page.headers['Set-Cookie'])
    soup = BeautifulSoup(page.text, 'html.parser')
    block = soup.find('div', class_='ifM9O')
    if block is not None:
        title, snippet = '', ''
        t = block.find('div', class_='r')
        s = block.find('div', class_='LGOjhe')
        if t and t.find('a') and t.find('h3') and s:
            title = clean(t.find('a').find('h3').text)
            snippet = clean(s.text)
            res.append('{} {}'.format(title, snippet))
    for block in soup.find_all('div', class_='g'):
        title, snippet = '', ''
        t = block.find('div', class_='r')
        s = block.find('span', class_='st')
        if t and t.find('a') and t.find('h3') and s:
            title = clean(t.find('a').find('h3').text)
            snippet = clean(s.text)
            res.append('{} {}'.format(title, snippet))
    return res

def crawl_snippet_baidu(concept):
    res = []
    url = 'http://www.baidu.com/s?wd={}'.format(concept)
    headers = {'user-agent': USER_AGENT, 'referer': url}
    page = sess.get(url, headers=headers)
    soup = BeautifulSoup(page.text, 'html.parser')
    block = soup.find('div', class_='result-op c-container xpath-log')
    if block is not None:
        title, snippet = '', ''
        t = block.find('h3', class_='t')
        s = block.find('div', class_='c-span18 c-span-last')
        if t and t.find('a') and s and s.find('p'):
            title = clean(t.find('a').text)
            snippet = clean(s.find('p').text)
            res.append('{} {}'.format(title, snippet))
    for block in soup.find_all('div', class_='result c-container' + (' ' if os.name == 'nt' else '')):
        title, snippet = '', ''
        t = block.find('h3', class_='t')
        s = block.find('div', class_='c-abstract')
        if t and t.find('a') and s:
            title = clean(t.find('a').text)
            snippet = clean(s.text)
            res.append('{} {}'.format(title, snippet))
    return res

def crawl_snippet_bing(concept):
    res = []
    url = 'https://cn.bing.com/search?q={}'.format(concept)
    headers = {'user-agent': USER_AGENT, 'referer': url}
    page = sess.get(url, headers=headers)
    soup = BeautifulSoup(page.text, 'html.parser')
    if 'cookie' in page.headers:
        update_cookie(page.headers['cookie'])
    block = soup.find('div', class_='b_subModule')
    if block is not None:
        title, snippet = '', ''
        t = block.find('h2', class_='b_entityTitle')
        s = block.find('div', class_='b_lBottom')
        if t and s:
            title = clean(t.text)
            snippet = clean(t.text)
            res.append('{} {}'.format(title, snippet))
    for block in soup.find_all('li', class_='b_algo'):
        title, snippet = '', ''
        t = block.find('h2')
        if t and t.find('a'):
            title = clean(t.find('a').text)
        s = block.find('div', class_='b_caption')
        if s and s.find('p'):
            snippet = clean(s.find('p').text)
        s = block.find('div', class_='tab-content')
        if s and s.find('div'):
            snippet = s.find('div').text
        if title and snippet:
            res.append('{} {}'.format(title, snippet))
    return res

def crawl_snippet(concept):
    global tot_crawl
    tot_crawl += 1
    if tot_crawl % 100 == 0:
        print('sleep 60s~90s after crawl 100 times')
        sleep(60)
    concept = urllib.parse.quote_plus(concept)
    sleep(2)  # sleep 2s~3s
    if config.snippet_source == 'baidu':
        res = crawl_snippet_baidu(concept)
    if config.snippet_source == 'google':
        res = crawl_snippet_google(concept)
    if config.snippet_source == 'bing':
        res = crawl_snippet_bing(concept)
    return '\n'.join(res)

def get_snippet(concept):
    conn = sqlite3.connect(config.db)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM {} WHERE concept=?'.format(config.snippet_source), (concept, ))
    res = cursor.fetchall()
    if not res:
        snippet = crawl_snippet(concept)
        print('get snippet {} from source {}'.format(concept, config.snippet_source))
        cursor.execute('INSERT INTO {} (concept, snippet) VALUES (?,?)'.format(config.snippet_source), (concept, snippet, ))
        conn.commit()
    else:
        snippet = res[0][1]
    conn.close()
    return snippet