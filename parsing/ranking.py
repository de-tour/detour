import pathlib
from fuzzywuzzy.fuzz import token_sort_ratio

def parse_url_keywords(config_dir):
    file_content = None
    with open(config_dir + '/url_rank.cfg', 'r') as f:
        file_content = f.read()

config_dir = pathlib.exec_dir + '/config'
url_keywords = parse_url_keywords(config_dir)
slash_range = (2, 5)

def score_url(url):
    if url and url.startswith('https://'):
        return 1
    return 0

def score_result(result, keyword):
    ratio = token_sort_ratio(str(result), keyword)
    url = score_url(getattr(result, 'url', None))
    return (ratio * 0.7) + (url * 0.3)

def rank_list(results, keyword):
    ranked_results = [(score_result(r, keyword), r) for r in results]
    list.sort(ranked_results, reverse=True)
    return [x[1] for x in ranked_results]
