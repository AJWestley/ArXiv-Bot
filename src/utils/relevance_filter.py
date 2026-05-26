import json

class RelevanceFilter:
    def __init__(self, keyword_scores: dict, threshold: int = 10):
        self.__keyword_scores = keyword_scores
        self.__threshold = threshold

    def __score_paper(self, paper: dict) -> int:
        text = (paper["title"] + " " + paper["summary"]).lower()
        return sum(weight for term, weight in self.__keyword_scores.items() if term in text)

    def filter_relevant(self, papers: list):
        '''
        Sorts a list of paper by relevance and removes all irrelevant papers.
        '''
        scored = [(p, self.__score_paper(p)) for p in papers]
        scored.sort(key=lambda x: x[1], reverse=True)
        return [p for p, score in scored if score >= self.__threshold]

def load_relevance_filter_from_json(filepath: str):
    '''
    Constructs a relevance filter from a json config file after checking the config for errors.
    '''
    with open(filepath) as file:
        config = json.load(file)
    if 'threshold' not in config:
        raise KeyError('Key "threshold" not found in config file.')
    if 'scores' not in config:
        raise KeyError('Key "scores" not found in config file.')
    
    threshold = config['threshold']
    scores = config['scores']

    if not isinstance(threshold, int):
        raise TypeError(f'"threshold" field should be an int, but its type is {type(threshold)}.')
    if not isinstance(scores, dict):
        raise TypeError(f'"scores" field should be a dict, but its type is {type(scores)}.')
    
    for keyword, weight in scores.items():
        if not isinstance(keyword, str):
            raise TypeError(f'{keyword} is of type {type(keyword)}, when it should be a str.')
        if not isinstance(weight, int):
            raise TypeError(f'{weight} is of type {type(weight)}, when it should be an int.')
    
    return RelevanceFilter(scores, threshold)