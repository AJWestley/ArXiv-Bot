import json

with open('src/ArXiv_API/taxonomy.json', encoding='utf-8') as taxonomy_file:
    categories = json.load(taxonomy_file)

class Taxonomy:
    """
    Represents a user-defined subset of the ArXiv category taxonomy.

    Built from a config dict that selects which fields and subfields to include,
    validated against the full taxonomy loaded from 'taxonomy.json'. Provides
    lookups for ArXiv category codes and emojis, and utilities for filtering
    and grouping papers by category.

    Attributes:
        __categories (dict): The validated subset of the ArXiv taxonomy.
        __code_map (dict): A mapping from ArXiv category codes to (field, subfield) tuples.
    """
    def __init__(self, config: dict):
        """
        Initialises the Taxonomy from a user-supplied config dict.

        Args:
            config (dict): A dict specifying which fields and subfields to include,
                            validated against the full ArXiv taxonomy.

        Raises:
            KeyError: If any field or subfield in the config does not exist in the full taxonomy.
        """
        self.__categories = _get_custom_taxonomy(config)
        self.__code_map = _get_codemap(self.__categories)
    
    def get_code(self, field: str, subfield: str | None = None) -> str:
        """
        Returns the ArXiv category code for a field or subfield.

        Args:
            field (str): The top-level field to look up (e.g. 'Computer Science').
            subfield (str, optional): The subfield to look up (e.g. 'Machine Learning').
                                        If omitted, returns the code for the top-level field.

        Returns:
            str: The ArXiv category code (e.g. 'cs', 'cs.LG').

        Raises:
            KeyError: If the field or subfield does not exist in the taxonomy.
        """
        if field not in self.__categories:
            raise KeyError(f'Invalid field: {field}')
        if subfield is not None and subfield not in self.__categories[field]['subfields']:
            raise KeyError(f'Invalid subfield: {subfield} does not exist inside {field}.')
        return self.__categories[field]['subfields'][subfield]['code'] if subfield else self.__categories[field]['code']
    
    def get_emoji(self, field: str, subfield: str | None = None) -> str:
        """
        Returns the emoji associated with a field or subfield.

        Args:
            field (str): The top-level field to look up (e.g. 'Computer Science').
            subfield (str, optional): The subfield to look up (e.g. 'Machine Learning').
                                        If omitted, returns the emoji for the top-level field.

        Returns:
            str: The emoji character associated with the field or subfield.

        Raises:
            KeyError: If the field or subfield does not exist in the taxonomy.
        """
        if field not in self.__categories:
            raise KeyError(f'Invalid field: {field}')
        if subfield and subfield not in self.__categories[field]['subfields']:
            raise KeyError(f'Invalid subfield: {subfield} does not exist inside {field}.')
        return self.__categories[field]['subfields'][subfield]['emoji'] if subfield else self.__categories[field]['emoji']
    
    def group_by_category(self, papers: list, field: str | None = None, max_per_category: int = 5):
        """
        Groups a list of papers by their primary ArXiv category.

        Each paper is assigned a primary category — the first of its listed categories
        that appears in the valid category set. Papers are then grouped into a nested
        dict keyed by (field, subfield). At most max_per_category papers are kept per
        subfield, preserving the order of the input list (which is expected to be
        pre-sorted by relevance).

        Args:
            papers (list[dict]): A list of paper dicts, each containing a 'categories' field.
            field (str, optional): If provided, restricts grouping to categories within
                                    this top-level field. Defaults to None (all fields).
            max_per_category (int): Maximum number of papers to include per subfield category.
                                    Defaults to 5.

        Returns:
            dict: A nested dict of the form { field: { subfield: [paper, ...] } }.
        """
        valid_categories = self.get_valid_categories(field)

        for paper in papers:
            primary_category = [category for category in paper['categories'] if category in valid_categories][0]
            paper['category'] = primary_category
        
        grouped = dict()

        for paper in papers:
            topic, subtopic = self.__code_map.get(paper['category'], (None, None))
            if topic not in grouped:
                grouped[topic] = dict()
            if subtopic not in grouped[topic]:
                grouped[topic][subtopic] = []
            if len(grouped[topic][subtopic]) < max_per_category:
                grouped[topic][subtopic].append(paper)

        return grouped

    def get_valid_categories(self, field: str | None = None):
        """
        Returns a list of ArXiv category codes present in the taxonomy.

        Args:
            field (str, optional): If provided, returns only the category codes belonging
                                    to that top-level field. Defaults to None (all fields).

        Returns:
            list[str]: A list of ArXiv category code strings (e.g. ['cs.LG', 'cs.CV']).
        """
        if field is None:
            cats = [self.__categories[topic]['subfields'][subtopic]['code'] for topic in self.__categories for subtopic in self.__categories[topic]['subfields']]
        else:
            cats = [self.__categories[field]['subfields'][subtopic]['code'] for subtopic in self.__categories[field]['subfields']]
        return cats
    
    def __getitem__(self, key):
        """
        Allows direct dict-style access to top-level fields in the taxonomy.

        Args:
            key (str): The top-level field name to retrieve.

        Returns:
            dict: The taxonomy entry for the given field.
        """
        return self.__categories[key]
    
def _get_custom_taxonomy(config: dict) -> dict:
    """
    Builds a validated taxonomy dict from a user config, using the full ArXiv taxonomy as reference.

    Iterates over the fields and subfields specified in the config, raising an error
    if any entry is not found in the full taxonomy loaded from 'taxonomy.json'.

    Args:
        config (dict): A dict mapping field names to lists of subfield names to include.

    Returns:
        dict: A nested taxonomy dict containing only the requested fields and subfields,
                with their associated codes and emojis.

    Raises:
        KeyError: If any field or subfield in the config is absent from the full taxonomy.
    """
    cats = dict()
    for field in config:
        if field not in categories:
            raise KeyError(f'Invalid field: {field}')
        cats[field] = dict()
        cats[field]['code'] = categories[field]['code']
        cats[field]['emoji'] = categories[field]['emoji']
        cats[field]['subfields'] = dict()
        for subfield in config[field]:
            if subfield not in categories[field]['subfields']:
                raise KeyError(f'Invalid subfield: {subfield} does not exist inside {field}.')
            cats[field]['subfields'][subfield] = categories[field]['subfields'][subfield]
    return cats

def _get_codemap(taxonomy: dict) -> dict:
    """
    Builds a reverse-lookup map from ArXiv category codes to (field, subfield) tuples.

    Args:
        taxonomy (dict): A nested taxonomy dict as returned by _get_custom_taxonomy.

    Returns:
        dict[str, tuple[str, str]]: A mapping from category code strings (e.g. 'cs.LG')
                                    to their (field, subfield) tuple (e.g. ('Computer Science', 'Machine Learning')).
    """
    return {
        data['code']: (field, subfield)
        for field, field_data in taxonomy.items()
        for subfield, data in field_data['subfields'].items()
    }

def load_taxonomy_from_json(filepath: str):
    """
    Constructs a Taxonomy instance from a JSON config file.

    The config file should be a dict mapping top-level field names to lists
    of subfield names to include, e.g.:
        { "Computer Science": ["Machine Learning", "Computer Vision"] }

    Args:
        filepath (str): Path to the JSON config file.

    Returns:
        Taxonomy: A fully initialised Taxonomy instance.

    Raises:
        KeyError: If any field or subfield in the config does not exist in the full taxonomy.
    """
    with open(filepath) as file:
        config = json.load(file)
    return Taxonomy(config)
