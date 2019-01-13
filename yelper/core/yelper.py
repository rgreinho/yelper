"""Define the core functions."""
import asyncio
import csv
import dataclasses
import os
import re
import urllib
import urllib3

import aiohttp
from lxml import html
# import request
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


async def deep_link(url, session):
    """Retrieve the URL from the business detail page."""
    if not url:
        return f'\u274C'

    try:
        async with session.get(url, headers=HEADERS, ssl=False) as request:
            response = await request.text()
            parser = html.fromstring(response)
            raw_website_link = parser.xpath("//span[contains(@class,'biz-website')]/a/@href")
    except Exception:
        return f'\U0001F611'

    if not raw_website_link:
        return f'\u274C'

    decoded_raw_website_link = urllib.parse.unquote(raw_website_link[0])
    website = re.findall(r"biz_redir\?url=(.*)&website_link", decoded_raw_website_link)[0]
    return website


async def deep_emails(url, session):
    """Retrieve the email addresses on the main page."""
    if not url:
        return f'\u274C'

    try:
        async with session.get(url, headers=HEADERS, ssl=False) as request:
            response = await request.text()
            emails = re.findall(r"[\w\.\+\-]+\@[\w]+\.[a-z]{2,4}", response)
    except Exception:
        return f'\U0001F611'

    return ', '.join(set(emails)) if emails else f'\U0001F611'


async def deep_entry_parsing(business, counter):
    """."""
    # Prepare the new entry.
    try:
        entry = YelpBusiness.from_dict(business)
    except Exception:
        print(f'{counter:04} Skipped due to error.')
    print(f'{counter:04} {entry.name}')

    # Dig deeper.
    async with aiohttp.ClientSession() as session:
        entry.link = await deep_link(business.get('url'), session)
        entry.emails = await deep_emails(entry.link, session)
    return entry


async def async_deep_query(terms, location, offset=0, limit=20, radius=40000, output='yelper.csv', pages=-1):
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
            if (params['offset'] / params['limit']) >= pages > 0:
                break

            # Process the results.
            tasks = [
                deep_entry_parsing(business, params['offset'] + i)
                for i, business in enumerate(search_results['businesses'])
            ]
            page_results = await asyncio.gather(*tasks)

            # Write the entries to the file and flush.
            for entry in page_results:
                writer.writerow(dataclasses.asdict(entry))
            csvfile.flush()

            # Update the offset before looping again.
            params['offset'] += params['limit']


def deep_query(terms, location, offset, limit, radius, output, pages):
    """."""
    asyncio.run(
        async_deep_query(terms, location, offset=offset, limit=limit, radius=radius, output=output, pages=pages))
