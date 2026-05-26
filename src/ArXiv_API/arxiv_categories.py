import json

with open('src/ArXiv_API/taxonomy.json', encoding='utf-8') as taxonomy_file:
    categories = json.load(taxonomy_file)

class Taxonomy:
    def __init__(self, config: dict):
        self.__categories = _get_custom_taxonomy(config)
        self.__code_map = _get_codemap(self.__categories)
    
    def get_code(self, field: str, subfield: str | None = None) -> str:
        '''
        Returns the ArXiv code for a particulat field (and subfield optionally).

        Args:
            field (str)
                The field to find the code of.
            subfield (str) - optional
                The subfield to find the code of.
        Returns:
            (str) - The relevant ArXiv code

        '''
        if field not in self.__categories:
            raise KeyError(f'Invalid field: {field}')
        if subfield is not None and subfield not in self.__categories[field]['subfields']:
            raise KeyError(f'Invalid subfield: {subfield} does not exist inside {field}.')
        return self.__categories[field]['subfields'][subfield]['code'] if subfield else self.__categories[field]['code']
    
    def get_emoji(self, field: str, subfield: str | None = None) -> str:
        '''
        Returns a relevant emoji for a particulat field (and subfield optionally).

        Args:
            field (str)
                The field to find the code of.
            subfield (str) - optional
                The subfield to find the code of.
        Returns:
            (str) - The relevant emoji

        '''
        if field not in self.__categories:
            raise KeyError(f'Invalid field: {field}')
        if subfield and subfield not in self.__categories[field]['subfields']:
            raise KeyError(f'Invalid subfield: {subfield} does not exist inside {field}.')
        return self.__categories[field]['subfields'][subfield]['emoji'] if subfield else self.__categories[field]['emoji']
    
    def group_by_category(self, papers: list, field: str | None = None, max_per_category: int = 5):
        '''
        Groups a list of papers according to the taxonomy.

        Args:
            papers (list)
                The list of paper objects.
            field (str) - optional
                Filter to include only categories within this field.
            max_per_category (int)
                Includes only the top n amount per category. Defaults to 5.
        '''
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
        '''
        Returns a list of valid categories according to the taxonomy.

        Args:
            field (str) - optional
                Allows filtering to categories within a specific field.
        '''
        if field is None:
            cats = [self.__categories[topic]['subfields'][subtopic]['code'] for topic in self.__categories for subtopic in self.__categories[topic]['subfields']]
        else:
            cats = [self.__categories[field]['subfields'][subtopic]['code'] for subtopic in self.__categories[field]['subfields']]
        return cats
    
    def __getitem__(self, key):
        return self.__categories[key]
    
def _get_custom_taxonomy(config: dict) -> dict:
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
    return {
        data['code']: (field, subfield)
        for field, field_data in taxonomy.items()
        for subfield, data in field_data['subfields'].items()
    }

def load_taxonomy_from_json(filepath: str):
    '''
    Constructs a taxonomy from a json config file.
    '''
    with open(filepath) as file:
        config = json.load(file)
    return Taxonomy(config)
