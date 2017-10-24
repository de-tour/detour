import requests

proxies = None
default_headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:56.0) Gecko/20100101 Firefox/56.0',
    'DNT': '1',
}

def get(url, params = None, headers = None):
    new_headers = (headers or {}).copy()
    new_headers.update(default_headers)
    r = requests.get(url, params=params, headers=new_headers, proxies=proxies)
    return r

def post(url, data = None, headers = None):
    new_headers = (headers or {}).copy()
    new_headers.update(default_headers)
    r = requests.post(url, data=data, headers=new_headers, proxies=proxies)
    return r

class Result(object):
    __slots__ = ('url', 'title', 'desc', 'thumbnail', 'source', 'album', 'tags', 'license', 'price',)
    def __init__(self, url, title, desc, thumbnail=None, source=None):
        self.url = url
        self.title = title
        self.desc = desc
        self.thumbnail = thumbnail
        self.source = source

        self.album = None
        self.tags = None
        self.license = None
        self.price = None


    def __repr__(self):
        return 'Result(%s)' % (
            ', '.join((x + '=' + repr(getattr(self, x)) for x in self.__slots__))
        )

    def __str__(self):
        s = ''
        for attr in self.__slots__:
            if attr != 'thumbnail':
                val = getattr(self, attr)
                if val:
                    s += str(val) + ', '
        return s

    def __eq__(self, other):
        return self.url == other.url

    def __hash__(self):
        return hash(self.url)

    def __lt__(self, other):
        return 0

    def __gt__(self, other):
        return 0

    def items(self):
        return {x: getattr(self, x) for x in self.__slots__}
