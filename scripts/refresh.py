"""Index LAC's featured historic resources and group exact-URL CDX captures by year."""
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from html.parser import HTMLParser
import json
from pathlib import Path
import re
from urllib.parse import urlencode, urlsplit
from urllib.request import Request, build_opener, HTTPRedirectHandler, urlopen
from urllib.error import HTTPError, URLError

ROOT=Path(__file__).resolve().parents[1]
CATALOG='https://webarchiveweb.bac-lac.canada.ca/'
API='https://web.archive.org/cdx/search/cdx?'
DATA=ROOT/'web/data.json'

class Highlights(HTMLParser):
    def __init__(self):
        super().__init__()
        self.heading=None
        self.group=''
        self.href=None
        self.label=[]
        self.records=[]
    def handle_starttag(self,tag,attrs):
        if tag=='h3': self.heading=[]
        if tag=='a':
            self.href=dict(attrs).get('href')
            self.label=[]
    def handle_data(self,text):
        if self.heading is not None:self.heading.append(text)
        if self.href:self.label.append(text)
    def handle_endtag(self,tag):
        if tag=='h3' and self.heading is not None:
            self.group=' '.join(''.join(self.heading).split())
            self.heading=None
        if tag=='a' and self.href:
            match=re.match(r'https://webarchiveweb\.wayback\.bac-lac\.canada\.ca/web/(\d{14})/(https?://.+)',self.href)
            if match and ('Gone from the web' in self.group or 'Federal Royal Commissions' in self.group):
                title=' '.join(''.join(self.label).split())
                stamp,original=match.groups()
                self.records.append({'title':title,'group':'Defunct resources' if 'Gone' in self.group else 'Commission records',
                    'host':urlsplit(original).hostname, 'original':original,'lac':self.href,
                    'date':stamp[:4]+'-'+stamp[4:6]+'-'+stamp[6:8]})
            self.href=None

def fetch(url):
    with urlopen(Request(url,headers={'User-Agent':'CoolCode historical web researcher'}),timeout=30) as r:
        return r.read()

class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self,*args): return None

def published_status(row):
    if not (row['host'].endswith('.gc.ca') or row['host'].endswith('.canada.ca')):
        return {'label':'Archive only'}
    address='https://'+row['original'].split('://',1)[1]
    req=Request(address,method='HEAD',headers={'User-Agent':'CoolCode archive link check'})
    try:
        with build_opener(NoRedirect).open(req,timeout=10) as r:code=r.status; location=''
    except HTTPError as e:
        code=e.code;location=e.headers.get('Location','')
    except (OSError, URLError):
        return {'label':'Check inconclusive'}
    domain=urlsplit(location).hostname or ''
    if 300<=code<400:
        label='Redirect to Canada.ca' if domain=='canada.ca' or domain.endswith('.canada.ca') else 'Redirect response'
    elif code in (404,410):label='Page unavailable'
    elif 200<=code<300:label='Responding'
    else:label='Check inconclusive'
    return {'label':label,'code':code}

def main():
    old=json.loads(DATA.read_text()) if DATA.exists() else {}
    oldrows={r['original']:r for r in old.get('records',[])}
    parser=Highlights();parser.feed(fetch(CATALOG).decode('utf-8'))
    if len(parser.records)<6: raise ValueError('LAC highlighted collection changed format')
    today=datetime.now(timezone.utc).date().isoformat()
    def enrich(row):
        address=API+urlencode({'url':row['original'],'output':'json','filter':'statuscode:200','collapse':'timestamp:4',
                              'fl':'timestamp,original,statuscode','to':row['date'].replace('-','')+'235959','limit':'200'})
        try:
            document=json.loads(fetch(address)) or []
            if document and document[0]!=['timestamp','original','statuscode']:raise ValueError('Unexpected CDX columns')
            years={}
            for stamp,original,code in document[1:]:
                if re.fullmatch(r'\d{14}',stamp) and code=='200' and stamp[:4] not in years:
                    years[stamp[:4]]={'date':stamp[:4]+'-'+stamp[4:6]+'-'+stamp[6:8],
                                     'url':'https://web.archive.org/web/'+stamp+'/'+original}
            row.update(years=years,cdx_checked=today)
        except (OSError,ValueError) as exc:
            print(row['host'],str(exc))
            prior=oldrows.get(row['original'],{});row.update(years=prior.get('years',{}),cdx_checked=prior.get('cdx_checked'))
        row['response']=published_status(row)
        return row
    with ThreadPoolExecutor(4) as pool:records=list(pool.map(enrich,parser.records))
    if not any(r['years'] for r in records):raise ValueError('No validated capture history')
    result={'retrieved':today,'source':CATALOG,'count':len(records),'captures':sum(len(r['years']) for r in records),'records':records}
    target=DATA.with_suffix('.tmp');target.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');target.replace(DATA)
    print(result['count'],result['captures'])
if __name__=='__main__':main()
