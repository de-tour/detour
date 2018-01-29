from pathlib import Path
from fuzzywuzzy.fuzz import token_sort_ratio
from configparser import ConfigParser

def parse_url_keywords():
    path = str(Path(__file__).parent.absolute()) + '/url_rank.ini'
    config_parser = ConfigParser()
    config_parser.read(path)
    return {int(k): v.split() for k, v in config_parser['contains'].items()}

score_dict = parse_url_keywords()
slash_range = (2, 5)

def score_url(url):
    total_score = 0
    url = url.lower()
    for score, keywords in score_dict.items():
        keyword_iter = iter(keywords)
        try:
            while True:
                word = next(keyword_iter)
                if word in url:
                    total_score += score
                    raise StopIteration()
        except StopIteration:
            pass
    return total_score

def score_result(result, keyword):
    ratio = token_sort_ratio(str(result), keyword)
    url = score_url(getattr(result, 'url', None))
    return (ratio * 0.7) + (url * 0.3)

def rank_list(results, keyword):
    ranked_results = [(score_result(r, keyword), r) for r in results]
    list.sort(ranked_results, reverse=True)
    return [x[1] for x in ranked_results]
