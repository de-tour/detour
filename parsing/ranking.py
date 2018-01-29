from pathlib import Path
from fuzzywuzzy.fuzz import token_sort_ratio

def parse_url_keywords():
    file_content = None
    path = str(Path(__file__).parent.absolute()) + '/url_rank.ini'
    with open(path, 'r') as f:
        file_content = f.read()
        # ?????

url_keywords = parse_url_keywords()
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
