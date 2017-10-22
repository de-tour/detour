import json
from base64 import urlsafe_b64encode
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from .network import get, post, Result

class CDBaby:
    home = 'https://www.cdbaby.com/'
    name = 'CD Baby'

    def suggest(self, keyword):
        url = 'https://store.cdbaby.com/SearchResults.aspx/GetAutoSuggest'
        payload = json.dumps({'query': keyword})
        headers = {
            'Content-Type': 'application/json; charset=utf-8',
            'X-Requested-With': 'XMLHttpRequest',
            'Referer': 'https://store.cdbaby.com/',
        }

        req = post(url, payload, headers)
        json_resp = req.json()
        try:
            return json_resp['d'].split('||')
        except (KeyError, AttributeError, TypeError) as e:
            raise ValueError('CD Baby server returned unexpected results') from e


    def decode_results(self, curr_url, html_resp):
        soup = BeautifulSoup(html_resp, 'html.parser')
        elements = soup.find_all('div', class_='carousel-album-container')

        results = []
        for div in elements:
            a = div.find('a')
            try:
                link = urljoin(curr_url, a['href'])
                thumbnail = a.find('img').get('data-original')
                if thumbnail:
                    thumbnail = urljoin(curr_url, thumbnail)

                span_title = div.find('span', class_='album-title')
                span_artist = div.find('span', class_='carousel-album-artist-name')

                title, artist = (None, None)
                if span_title:
                    title = span_title.get_text(strip=True)
                if span_artist:
                    artist = span_artist.get_text(strip=True)

                r = Result(link, title, artist, thumbnail=thumbnail)
                # r = Result(link, title, artist, thumbnail=None)
                results.append(r)
            except (KeyError, AttributeError, TypeError) as e:
                raise ValueError('') from e

        return results


    def search(self, keyword, page=1, options = None):
        b64_word = urlsafe_b64encode(keyword.encode('utf-8'))
        url = 'https://store.cdbaby.com/Search/' + b64_word.decode('ascii') + '/0/pg' + str(page)

        req = get(url)
        return self.decode_results(url, req.text)



class Bandcamp:
    home = 'https://bandcamp.com/'
    name = 'Bandcamp'

    def decode_suggest(self, json_resp):
        results = json_resp['auto']['results']
        words = []
        for info in results:
            segments = (
                info.get('name', ''),
                info.get('band_name', ''),
            )
            segments = (x.strip() for x in segments if x.strip())
            if segments:
                words.append(', '.join(segments))
        return words


    def suggest(self, keyword):
        url = 'https://bandcamp.com/api/fuzzysearch/1/autocomplete'
        params = {'q': keyword}
        headers = {
            'Accept': '*/*',
            'X-Requested-With': 'XMLHttpRequest',
            'Referer': 'https://bandcamp.com/',
        }

        req = get(url, params, headers)
        try:
            return self.decode_suggest(req.json())
        except (KeyError, AttributeError, TypeError) as e:
            raise ValueError('Bandcamp server returned unexpected results') from e


    def search(self, keyword, page=1, options = None):
        return []

__all__ = ('CDBaby', 'Bandcamp')
