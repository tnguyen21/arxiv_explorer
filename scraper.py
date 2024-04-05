"""
A python program to retreive recrods from ArXiv.org in given
categories and specific date range.

based off of https://github.com/Mahdisadjadi/arxivscraper
"""
from __future__ import print_function
import xml.etree.ElementTree as ET
import datetime
import time
import sys
from typing import Dict, List
from urllib.parse import urlencode
from urllib.request import urlopen
from urllib.error import HTTPError
import json

OAI = "{http://www.openarchives.org/OAI/2.0/}"
ARXIV = "{http://arxiv.org/OAI/arXiv/}"
BASE = "http://export.arxiv.org/oai2?verb=ListRecords&"

# go to this URL if you want to see all valid `setSpec`s
# what's a setSpec? look here: https://info.arxiv.org/help/oa/index.html
LIST_SETSPECS_URL = "http://export.arxiv.org/oai2?verb=ListSets"

class Record(object):
    """
    A class to hold a single record from ArXiv
    Each records contains the following properties:

    object should be of xml.etree.ElementTree.Element.
    """
    def __init__(self, xml_record):
        """if not isinstance(object,ET.Element):
        raise TypeError("")"""
        self.xml = xml_record
        self.id = self._get_text(ARXIV, "id")
        self.url = "https://arxiv.org/abs/" + self.id
        self.title = self._get_text(ARXIV, "title")
        self.abstract = self._get_text(ARXIV, "abstract")
        self.cats = self._get_text(ARXIV, "categories")
        self.created = self._get_text(ARXIV, "created")
        self.updated = self._get_text(ARXIV, "updated")
        self.doi = self._get_text(ARXIV, "doi")
        self.authors = self._get_authors()
        self.affiliation = self._get_affiliation()

    def _get_text(self, namespace: str, tag: str) -> str:
        """Extracts text from an xml field"""
        try:
            return self.xml.find(namespace + tag).text.strip().lower().replace("\n", " ")
        except:
            return ""

    def _get_name(self, parent, attribute) -> str:
        """Extracts author name from an xml field"""
        try:
            return parent.find(ARXIV + attribute).text.lower()
        except:
            return "n/a"

    def _get_authors(self) -> List:
        """Extract name of authors"""
        authors_xml = self.xml.findall(ARXIV + "authors/" + ARXIV + "author")
        last_names = [self._get_name(author, "keyname") for author in authors_xml]
        first_names = [self._get_name(author, "forenames") for author in authors_xml]
        full_names = [a + " " + b for a, b in zip(first_names, last_names)]
        return full_names

    def _get_affiliation(self) -> str:
        """Extract affiliation of authors"""
        authors = self.xml.findall(ARXIV + "authors/" + ARXIV + "author")
        try:
            affiliation = [author.find(ARXIV + "affiliation").text.lower() for author in authors]
            return affiliation
        except:
            return []

    def output(self) -> Dict:
        """Data for each paper record"""
        d = {
            "title": self.title,
            "id": self.id,
            "abstract": self.abstract,
            "categories": self.cats,
            "doi": self.doi,
            "created": self.created,
            "updated": self.updated,
            "authors": self.authors,
            "affiliation": self.affiliation,
            "url": self.url,
        }
        return d


class Scraper(object):
    """
    A class to hold info about attributes of scraping,
    such as date range, categories, and number of returned
    records. If `from` is not provided, the first day of
    the current month will be used. If `until` is not provided,
    the current day will be used.

    Paramters
    ---------
    category: str
        The category of scraped records
    data_from: str
        starting date in format 'YYYY-MM-DD'. Updated eprints are included even if
        they were created outside of the given date range. Default: first day of current month.
    date_until: str
        final date in format 'YYYY-MM-DD'. Updated eprints are included even if
        they were created outside of the given date range. Default: today.
    t: int
        Waiting time between subsequent calls to API, triggred by Error 503.
    timeout: int
        Timeout in seconds after which the scraping stops. Default: 300s

    Example:
    Returning all eprints from `stat` category:

    ```
        scraper = ax.Scraper(category='stat',date_from='2017-12-23',date_until='2017-12-25',t=10)
        output = scraper.scrape()
    ```
    """
    def __init__(
        self,
        category: str,
        date_from: str = None,
        date_until: str = None,
        t: int = 30,
        timeout: int = 300,
    ):
        self.cat = str(category)
        self.t = t
        self.timeout = timeout
        DateToday = datetime.date.today()
        if date_from is None:
            self.f = str(DateToday.replace(day=1))
        else:
            self.f = date_from
        if date_until is None:
            self.u = str(DateToday)
        else:
            self.u = date_until
        self.url = f"{BASE}from={self.f}&until={self.u}&metadataPrefix=arXiv&set={self.cat}"

    def scrape(self) -> List[Dict]:
        t0 = time.time()
        tx = time.time()
        elapsed = 0.0
        ds = []
        while True:
            print("fetching records...")
            try:
                response = urlopen(self.url)
            except HTTPError as e:
                if e.code == 503:
                    to = int(e.hdrs.get("retry-after", 30))
                    print("Got 503. Retrying after {0:d} seconds.".format(self.t))
                    time.sleep(self.t)
                    continue
                else:
                    raise
            xml = response.read()
            root = ET.fromstring(xml)
            records = root.findall(OAI + "ListRecords/" + OAI + "record")
            for record in records:
                meta = record.find(OAI + "metadata").find(ARXIV + "arXiv")
                record = Record(meta).output()
                ds.append(record)

            try:
                token = root.find(OAI + "ListRecords").find(OAI + "resumptionToken")
            except:
                return 1
            if token is None or token.text is None:
                break
            else:
                self.url = BASE + "resumptionToken=%s" % token.text

            ty = time.time()
            elapsed += ty - tx
            if elapsed >= self.timeout:
                break
            else:
                tx = time.time()

        t1 = time.time()
        print(f"Fetching completed in {t1 - t0:.1f} seconds")
        print(f"Total number of records {len(ds)}")
        return ds

if __name__ == "__main__":
    # scraper = Scraper(category='cs', date_from="2012-01-01", t=10, timeout=6000)
    # scraper = Scraper(category='cs', date_from="2017-03-08", t=7, timeout=(60 * 120))
    scraper = Scraper(category='cs', date_from="2024-04-01", t=7, timeout=(60 * 120))
    output = scraper.scrape()
    # have to run it again since we didnt get all papers during the first run
    with open("out3.json", "w") as f:
        json.dump(output, f, indent=2)