"""Define the core functions."""
import csv
import dataclasses
import os
import re
import urllib
import urllib3

from lxml import html
import requests
from yelpapi import YelpAPI

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

HEADERS = {
    'User-Agent':
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.90 Safari/537.36'
}


@dataclasses.dataclass
class YelpBusiness:
    """Defines a business from Yelp."""

    name: str
    phone: str = ''
    address: str = ''
    zipcode: str = ''
    link: str = ''
    emails: str = ''

    @classmethod
    def from_dict(cls, other_dict):
        """Create a `YelpBusiness` from a dictionary instance."""
        d = YelpBusiness(other_dict['name'])
        d.phone = other_dict.get('phone', '')
        d.address = ' '.join(other_dict.get('location', {}).get('display_address', []))
        d.zipcode = other_dict.get('location', {}).get('zip_code', '')
        d.link = other_dict.get('link', '')
        d.emails = other_dict.get('emails', '')
        return d


def deep_link(url):
    """Retrieve the URL from the business detail page."""
    if not url:
        return f'\u274C'

    try:
        response = requests.get(url, headers=HEADERS, verify=False).text
        parser = html.fromstring(response)
        raw_website_link = parser.xpath("//span[contains(@class,'biz-website')]/a/@href")
    except Exception:
        return f'\U0001F611'

    if not raw_website_link:
        return f'\u274C'

    decoded_raw_website_link = urllib.parse.unquote(raw_website_link[0])
    website = re.findall(r"biz_redir\?url=(.*)&website_link", decoded_raw_website_link)[0]
    return website


def deep_emails(url):
    """Retrieve the email addresses on the main page."""
    if not url:
        return f'\u274C'

    try:
        response = requests.get(url, headers=HEADERS, verify=False).text
        emails = re.findall(r"[\w\.\+\-]+\@[\w]+\.[a-z]{2,4}", response)
    except Exception:
        return f'\U0001F611'

    return ', '.join(set(emails)) if emails else f'\U0001F611'


def deep_query(terms, location, offset, limit, radius, output):
    """Define the application entrypoint."""
    # Prepare the Yelp client.
    yelp_api = YelpAPI(os.environ['YELP_API_KEY'])
    params = {
        'term': terms,
        'location': location,
        'offset': offset,
        'limit': limit,
        'radius': radius,
    }

    # Prepare the CSV file.
    fieldnames = dataclasses.asdict(YelpBusiness('fake')).keys()
    with open(output, 'w') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

    # Search Yelp.
    while True:
        search_results = yelp_api.search_query(**params)

        # Check whether we need to process further or not.
        if not search_results:
            break
        if not search_results['businesses']:
            break

        # Open the CSV file  to add data.
        with open(output, 'a') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            # Go through each result.
            for i, business in enumerate(search_results['businesses']):
                counter = params['offset'] + i
                try:
                    entry = YelpBusiness.from_dict(business)
                except Exception:
                    print(f'{counter:04} Skipped due to error.')
                    continue

                # Prepare the new entry.
                print(f'{counter:04} {entry.name}')
                entry.link = deep_link(business.get('url'))
                entry.emails = deep_emails(entry.link)
                writer.writerow(dataclasses.asdict(entry))

        # Update the offset before looping again.
        params['offset'] += params['limit']
