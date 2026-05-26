import urllib.request as libreq
import urllib.error as urlerror
import xml.etree.ElementTree as ET
from time import sleep
import logging
from src.utils.time_utils import arxiv_str

BASE_URL = 'https://export.arxiv.org/api'

logger = logging.getLogger(__name__)


# ----- Paper Retrieval -----

def get_papers(date, category=None, max_results=1000, retries=10, polite_delay=3):
    '''
    Finds all papers published on the ArXiv on a provided date within a list of categories
    '''
    sleep(polite_delay)
    date_str = arxiv_str(date)
    date_range = f"[{date_str}0000+TO+{date_str}2359]"
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
            req = libreq.Request(url, headers={"User-Agent": "ArXivistBot/1.0 (alexanderjwestley@gmail.com)"})
            with libreq.urlopen(req, timeout=30) as response:
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

