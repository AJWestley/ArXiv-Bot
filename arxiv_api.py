import urllib.request as libreq
import urllib.error as urlerror
import xml.etree.ElementTree as ET
from time import sleep
import logging
from time_utils import last_weekday, yesterday, arxiv_str
from relevance_filtering import filter_relevant
from arxiv_categories import categories, code_map

BASE_URL = 'https://export.arxiv.org/api'

logger = logging.getLogger(__name__)


# ----- Paper Retrieval -----

def get_papers(start_date, end_date, category=None, max_results=1000, retries=10):

    date_range = f"[{arxiv_str(start_date)}0000+TO+{arxiv_str(end_date)}2359]"
    query = f"submittedDate:{date_range}"
    if category:
        if isinstance(category, list):
            cat_filter = "+OR+".join(f"cat:{c}" for c in category)
            query = f"({cat_filter})+AND+submittedDate:{date_range}"
        else:
            query = f"cat:{category}+AND+submittedDate:{date_range}"

    url = (
        f"{BASE_URL}/query"
        f"?search_query={query}"
        f"&sortBy=submittedDate&sortOrder=descending"
        f"&start=0&max_results={max_results}"
    )

    for attempt in range(retries):
        try:
            with libreq.urlopen(url, timeout=30) as response:
                raw = response.read()

        except urlerror.HTTPError as e:
            if e.code in (429, 503):
                wait = 2 ** attempt
                logger.warning(f"HTTP {e.code}. Retrying in {wait}s... (attempt {attempt + 1}/{retries})")
                sleep(wait)
                continue
            else:
                logger.error(f"HTTP error {e.code}: {e.reason}")
                raise

        except urlerror.URLError as e:
            wait = 2 ** attempt
            logger.warning(f"URL error: {e.reason}. Retrying in {wait}s... (attempt {attempt + 1}/{retries})")
            sleep(wait)
            continue

        try:
            root = ET.fromstring(raw)
        except ET.ParseError as e:
            logger.error(f"Failed to parse XML: {e}\nResponse: {raw[:200]}")
            raise

        ns = {"atom": "http://www.w3.org/2005/Atom"}
        papers = []
        for entry in root.findall("atom:entry", ns):
            cats = [tag.get("term") for tag in entry.findall("atom:category", ns)]
            papers.append({
                "title": entry.find("atom:title", ns).text.strip(),
                "summary": entry.find("atom:summary", ns).text.strip(),
                "id": entry.find("atom:id", ns).text.strip(),
                "authors": [a.find("atom:name", ns).text for a in entry.findall("atom:author", ns)],
                "categories": cats,
            })

        return papers

    raise RuntimeError(f"Failed to fetch papers after {retries} attempts")

def get_all_papers(field, start_date=None, end_date=None):
    if start_date is None:
        start_date = last_weekday()
    if end_date is None:
        end_date = yesterday()
    
    cats = get_valid_categories(field)
    
    papers = get_papers(start_date, end_date, cats)
    papers = filter_relevant(papers)
    papers = group_by_category(papers, set(cats))
    
    return papers


# ----- Category Grouping -----

def group_by_category(papers, requested_categories=None, max_per_category=5):
    
    for paper in papers:
        primary_category = [category for category in paper['categories'] if category in requested_categories][0]
        del paper['categories']
        paper['category'] = primary_category
    
    grouped = dict()

    for paper in papers:
        topic, subtopic = code_map[paper['category']]
        if topic not in grouped:
            grouped[topic] = dict()
        if subtopic not in grouped[topic]:
            grouped[topic][subtopic] = []
        if len(grouped[topic][subtopic]) < max_per_category:
            grouped[topic][subtopic].append(paper)

    return grouped

def get_valid_categories(field=None):
    if field is None:
        cats = [categories[topic][subtopic] for topic in categories for subtopic in categories[topic]]
    else:
        cats = [categories[field][subtopic] for subtopic in categories[field]]
    return cats


# ----- Main for Testing -----

if __name__ == '__main__':
    papers = get_all_papers()
    for c in papers:
        for p in papers[c]:
            print(p['title'])
            print(p['categories'])
            print()
