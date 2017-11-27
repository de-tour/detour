from network import get, post, Result
import json

class ArchiveOrg:
    home = 'https://archive.org/'
    name = 'Internet Archive'

    def decode_results(self, j, curr_url):
        pass

    def search(self, keyword, page=1, options = None):
        url = 'https://archive.org/advancedsearch.php'
        params = {
            'q': keyword.replace(' TO ', ' to '), 'rows': '50', 'page': page,
            'output': 'json', 'callback': '', 'save': 'yes',
            'fl[]': ['creator', 'description', 'identifier', 'licenseurl', 'source', 'subject', 'title'],
            'sort[]': ['downloads desc', 'stars desc', 'avg_rating desc'],
        }

    req = get(url, params=params)
    try:
        return self.decode_results(req.json(), url)
    except (KeyError, AttributeError, TypeError) as e:
        raise ValueError('Internet Archive returned unexpected results')
