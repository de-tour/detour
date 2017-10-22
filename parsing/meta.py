from .network import get, post, Result
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from urllib.parse import urljoin
from urllib.parse import parse_qsl
from random import SystemRandom

domains = {
    'bandcamp.com': 'Bandcamp',
    'cdbaby.com': 'CD Baby',

    'altermusique.org': 'Altermusique.org',
    'ccmixter.org': 'ccMixter',

    'archive.org': 'Internet Archive',
}

def match_host(yours):
    for (prefix, name) in domains.items():
        if yours == prefix or yours.endswith('.' + prefix):
            return name

def match_urlobj(o):
    site_name = match_host(o.hostname)
    if site_name:
        return (site_name, o.geturl())
    else:
        return (None, None)

def match_url(curr_url, rel_url):
    o = urlparse(urljoin(curr_url, rel_url))
    return match_urlobj(o)


class DuckDuckGo:
    home = 'https://duckduckgo.com/'
    name = 'DuckDuckGo'

    def suggest(self, keyword):
        url = 'https://duckduckgo.com/ac/'
        params = {'q': keyword}

        req = get(url, params=params)
        json_resp = req.json()
        try:
            return [str(j['phrase']) for j in json_resp]
        except (KeyError, AttributeError, TypeError) as e:
            raise ValueError('') from e

    def site_filter(self, keyword, hostname):
        return 'site:' + hostname + ' ' + keyword

    def decode_results(self, curr_url, html_resp):
        soup = BeautifulSoup(html_resp, 'html.parser')
        results = []
        div_results = soup.find_all('div', class_='result__body')
        for div in div_results:
            a_title = div.find('a', class_='result__a')
            title = a_title.get_text(' ', strip=True)
            desc = div.find(class_='result__snippet').get_text(' ', strip=True)

            urllist = []
            urlobj = urlparse(urljoin(curr_url, a_title['href']))
            urllist.append(urlobj)
            for (k, v) in parse_qsl(urlobj.query):
                hidden_link = urlparse(urljoin(curr_url, v))
                urllist.append(hidden_link)

            for o in urllist:
                site_name, new_url = match_urlobj(o)
                if site_name:
                    r = Result(new_url, title, desc, source=site_name + ' via ' + self.name)
                    results.append(r)

        return results

    def search(self, keyword, page=1, options = None):
        if page != 1:
            return []

        url = 'https://duckduckgo.com/html/'
        params = {'q': keyword}

        req = get(url, params=params)
        try:
            return self.decode_results(url, req.text)
        except (KeyError, AttributeError, TypeError) as e:
            raise ValueError('DuckDuckGo server returned unexpected results') from e



class StartPage:
    home = 'https://www.startpage.com/'
    name = 'StartPage'

    def __init__(self):
        self.search_url = self.home + 'do/search'
        self.qid = ''

    def next_page_info(self, curr_url, soup):
        form = soup.find('form', id='pnform')
        o = urlparse(urljoin(curr_url, form['action']))
        if o.scheme == 'https' and ('.' + o.hostname).endswith('.startpage.com'):
            self.search_url = o.geturl()

        qid_input = form.find(lambda tag: tag.name == 'input' and tag.get('name', '') == 'qid')
        self.qid = qid_input['value']

    def suggest(self, keyword):
        return []

    def site_filter(self, keyword, hostname):
        return keyword + ' site:' + hostname

    def decode_results(self, curr_url, html_resp):
        soup = BeautifulSoup(html_resp, 'html.parser')
        results = []
        div_results = soup.find_all('div', class_='result')

        for div in div_results:
            a_link = div.find(lambda tag: tag.name == 'a' and tag.get('id', '').startswith('title_'))
            p_desc = div.find('p', class_='desc')

            title = a_link.get_text(' ', strip=True)
            desc = p_desc.get_text(' ', strip=True)

            site_name, new_url = match_url(curr_url, a_link['href'])
            if site_name:
                r = Result(new_url, title, desc, source=site_name + ' via ' + self.name)
                results.append(r)
        try:
            self.next_page_info(curr_url, soup)
        except (KeyError, AttributeError, TypeError) as e:
            pass

        return results

    def search(self, keyword, page=1, options = None):
        params = {
            'query': keyword, 'startat': 10 * (page - 1), 'qid': self.qid,
            'cmd': 'process_search', 'language': 'english', 'rcount': '',
            'rl': 'NONE', 'abp': '-1', 't': '', 'cat': 'web',
        }

        req = post(self.search_url, data=params)
        try:
            return self.decode_results(self.search_url, req.text)
        except (KeyError, AttributeError, TypeError) as e:
            raise ValueError('StartPage server returned unexpected results') from e



class Qwant:
    home = 'https://www.qwant.com/'
    name = 'Qwant'

    def suggest(self, keyword):
        return []

    def site_filter(self, keyword, hostname):
        return keyword + ' site:' + hostname

    def search(self, keyword, page=1, options = None):
        return []


class Searx:
    class_result = 'result'
    class_header = 'result_header'
    class_content = 'result-content'

    def suggest(self, keyword):
        url = self.home.rstrip('/') + '/autocompleter'
        params = {'q': keyword}

        req = get(url, params=params)
        resp_json = req.json()

        if not isinstance(resp_json, list):
            raise ValueError('Suggestion of %s cannot be decoded' % self.name)
        return [str(x) for x in resp_json]


    def site_filter(self, keyword, hostname):
        return keyword + ' inurl:' + hostname

    def decode_results(self, curr_url, html_resp):
        soup = BeautifulSoup(html_resp, 'html.parser')
        results = []
        div_results = soup.find_all('div', class_=self.class_result)
        for div in div_results:
            wrapper = div.find(class_=self.class_header)
            a = wrapper.find('a')
            title = a.get_text(' ', strip=True)

            p_desc = div.find(class_=self.class_content)
            desc = None
            if p_desc:
                desc = p_desc.get_text(' ', strip=True)

            site_name, new_url = match_url(curr_url, a['href'])
            if site_name:
                r = Result(new_url, title, desc, source=site_name + ' via ' + self.name)
                results.append(r)

        return results


    def search(self, keyword, page=1, options = None):
        url = self.home
        data = {
            'q': keyword, 'pageno': page,
            'category_general': '1', 'time_range': '', 'language': 'all',
        }

        req = post(url, data=data)
        try:
            return self.decode_results(url, req.text)
        except (KeyError, AttributeError, TypeError) as e:
            raise ValueError(self.name + ' server returned unexpected results') from e


class SearxMe(Searx):
    home = 'https://searx.me/'
    name = 'searx.me'

class SearxDk(Searx):
    home = 'https://www.searx.dk/'
    name = 'searx.dk'

class SearxCh(Searx):
    home = 'https://searx.ch/'
    name = 'searx.ch'

class SearxAt(Searx):
    home = 'https://searx.at/'
    name = 'searx.at'

class SearxInfo(Searx):
    home = 'https://searx.info/'
    name = 'searx.info'

class SearxPotato(Searx):
    home = 'https://searx.potato.hu/'
    name = 'searx.potato.hu'

class SearxAbenthung(Searx):
    home = 'https://searx.abenthung.it/'
    name = 'searx.abenthung.it'

class SearxGotrust(Searx):
    home = 'https://searx.gotrust.de/'
    name = 'searx.gotrust.de'

class SearxPrvcy(Searx):
    home = 'https://searx.prvcy.eu/'
    name = 'searx.prvcy.eu'

class SearxGoodOne(Searx):
    home = 'https://searx.good.one.pl/'
    name = 'searx.good.one.pl'

class SearxNulltime(Searx):
    home = 'https://searx.nulltime.net/'
    name = 'searx.nulltime.net'

class SucheFTP(Searx):
    home = 'https://suche.ftp.sh/'
    name = 'suche.ftp.sh'

class Rubbeldiekatz(Searx):
    home = 'https://search.rubbeldiekatz.info/'
    name = 'search.rubbeldiekatz.info'

class Datensturm(Searx):
    home = 'https://search.datensturm.net/'
    name = 'search.datensturm.net'

class OpenGo(Searx):
    home = 'https://www.opengo.nl/'
    name = 'opengo.nl'


class SearxBalancer:
    home = 'https://github.com/asciimoo/searx/wiki/Searx-instances'
    name = 'Searx'

    @staticmethod
    def balance(concurrent=3):
        instances = [
            SearxMe, SearxDk, SearxCh, SearxAt, SearxInfo, SearxPotato,
            SearxAbenthung, SearxGotrust, SearxPrvcy, SearxGoodOne, SearxNulltime,
            SucheFTP, Rubbeldiekatz, Datensturm, OpenGo,
        ]

        targets = []
        for _ in range(concurrent):
            index = SystemRandom().randint(0, len(instances) - 1)
            targets.append(instances.pop(index))

        return targets
