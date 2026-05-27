import json

class RelevanceFilter:
    """
    Scores and filters academic papers based on keyword relevance.

    Each keyword is assigned a weight, and a paper's score is the sum of weights
    for all keywords found in its title and summary. Papers scoring below the
    threshold are discarded; those above are returned in descending score order.

    Attributes:
        __keyword_scores (dict[str, int]): A mapping of lowercase keywords to their relevance weights.
        __threshold (int): The minimum score a paper must achieve to be considered relevant.
    """
    def __init__(self, keyword_scores: dict, threshold: int = 10):
        """
        Initialises the RelevanceFilter with a keyword-weight mapping and a score threshold.

        Args:
            keyword_scores (dict[str, int]): A mapping of keywords to their integer relevance weights.
            threshold (int): Minimum score required for a paper to pass the filter. Defaults to 10.
        """
        self.__keyword_scores = keyword_scores
        self.__threshold = threshold

    def __score_paper(self, paper: dict) -> int:
        """
        Computes the relevance score for a single paper.

        Concatenates the paper's title and summary, converts to lowercase, then sums
        the weights of all keywords found in that text.

        Args:
            paper (dict): A paper dict containing at least 'title' and 'summary' string fields.

        Returns:
            int: The total relevance score for the paper.
        """
        text = (paper["title"] + " " + paper["summary"]).lower()
        return sum(weight for term, weight in self.__keyword_scores.items() if term in text)

    def filter_relevant(self, papers: list):
        """
        Sorts a list of papers by relevance score and removes all irrelevant papers.

        Papers are scored using keyword matching against their title and summary.
        Only papers meeting or exceeding the threshold are returned, in descending
        order of relevance score.

        Args:
            papers (list[dict]): A list of paper dicts, each containing 'title' and 'summary' fields.

        Returns:
            list[dict]: The filtered and sorted list of relevant papers.
        """
        scored = [(p, self.__score_paper(p)) for p in papers]
        scored.sort(key=lambda x: x[1], reverse=True)
        return [p for p, score in scored if score >= self.__threshold]

def load_relevance_filter_from_json(filepath: str):
    """
    Constructs a RelevanceFilter from a JSON config file after validating its contents.

    The config file must contain:
        - "threshold" (int): The minimum relevance score for a paper to pass the filter.
        - "scores" (dict[str, int]): A mapping of keyword strings to integer relevance weights.

    Args:
        filepath (str): Path to the JSON config file.

    Returns:
        RelevanceFilter: A fully initialised RelevanceFilter instance.

    Raises:
        KeyError: If "threshold" or "scores" keys are missing from the config.
        TypeError: If "threshold" is not an int, "scores" is not a dict, or any
                    keyword is not a str or any weight is not an int.
    """
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