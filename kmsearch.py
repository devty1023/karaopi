#-*- coding: utf-8 -*-
import requests
import urllib
from bs4 import BeautifulSoup

def km_search(**kwargs):
    BASE_URL = "http://www.ikaraoke.kr/isong/search_musictitle.asp?page={page}&sch_sel={qtype}&sch_txt={query}"
    url = BASE_URL.format(**kwargs)
    print("getting song list from: {}".format(url))
    r = requests.get(url)
    return _extract_songs(r.text)

def _extract_songs(html):
    soup = BeautifulSoup(html)

    table = soup.find('table', 
                        attrs={'summary':'곡제목 검색 결과 리스트입니다.'})
    table_body = table.find('tbody')
    rows = table_body.find_all('tr', 
                        attrs={"onmouseout":"this.style.backgroundColor=''"})
    songs = []
    for row in rows:
        sid_tag = row.find('td', attrs={'class':'ac'})
        title_tag = row.find('td', attrs={'class':'pl8'})
        singer_tag = row.find('td', attrs={'class':'tit pl8'})

        if sid_tag and title_tag and singer_tag:
            sid = sid_tag.find('em').get_text().strip().replace('undefined','')
            try:
                title = title_tag.find('a')['title']
            except:
                title = title_tag.find('span')['title']
            singer = singer_tag.find('a').get_text().strip().replace('undefined','')
            songs.append({'sid':sid, 'title':title, 'singer':singer})
    return songs

if __name__ == "__main__":
    args = {'page':"1", 'qtype':"7", 'query':(u"아이유").encode('cp949')}
    args = {k:urllib.parse.quote(v) for k,v in args.items()}
    print(km_search(**args))
    #print("DONE")
    #sys.stdout = codecs.getwriter('utf8')(sys.stdout)
    #ret = extract(codecs.open("parsethis.html", encoding='utf8', mode="r").read())
    #print(ret)

