from pathlib import Path
from fuzzywuzzy.fuzz import token_sort_ratio
from configparser import ConfigParser
from re import split
from urllib.parse import parse_qs

def parse_url_keywords():
    config_parser = ConfigParser()
    config_parser.read(Path(__file__).parent / 'url_rank.ini')
    return {int(k): frozenset(v.split()) for k, v in config_parser['contains'].items()}

score_dict = parse_url_keywords()
slash_range = (2, 5)

def score_url(url_object):
    total_score = 0
    tokens = tokenize(url_object)
    for score, keywords in score_dict.items():
        if not keywords.isdisjoint(tokens)
            total_score += score
            # TODO: decrease token size, detect size difference
    return total_score

def score_result(result, keyword):
    ratio = token_sort_ratio(str(result), keyword)
    # url = score_url(getattr(result, 'url', None))
    url = 0
    return (ratio * 0.7) + (url * 0.3)

def rank_list(results, keyword):
    ranked_results = [(score_result(r, keyword), r) for r in results]
    list.sort(ranked_results, reverse=True)
    return [x[1] for x in ranked_results]

def tokenize(url_object):
    s = set(_tokenize_str(url_object.path))
    s.add(url_object.scheme)
    for (k, vlist) in parse_qs(url_object.query).items():
        s.update(_tokenize_str(k))
        for v in vlist:
            s.update(_tokenize_str(v))
    return s

def _tokenize_str(full_str):
    print(repr(full_str))
    return (s.lower() for s in split('[^a-zA-Z]+', full_str) if s)
