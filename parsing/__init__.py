from .wellknown import *
from .meta import *
from .ccfree import *

from .ranking import *

def generate_names(sites):
    names = {}
    for engine in sites:
        names[engine.name] = engine
    return names

sites = (
    CDBaby, Bandcamp, DuckDuckGo, StartPage, Qwant, SearxBalancer,
)

names = generate_names(sites)

def is_balancer(site_class):
    return hasattr(site_class, 'balance')

def can_suggest(site_class):
    return hasattr(site_class, 'suggest')

def can_search(site_class):
    return hasattr(site_class, 'search')
