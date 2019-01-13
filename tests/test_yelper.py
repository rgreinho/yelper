"""Test the Yelper module."""
import asyncio
import json
import os

from faker import Faker
import pytest
from yelpapi import YelpAPI

from yelper.core.yelper import async_deep_query


def async_mock(result):
    """Create an awaitable object to simplify mocking awaitable functions."""
    f = asyncio.Future()
    f.set_result(result)
    return f


class TestYelpBusiness:
    """Test the YelpBusiness class."""


class TestYelper:
    """Tests for `yelper` module."""
    fake = Faker()

    @pytest.mark.asyncio
    async def test_async_deep_query_00(self, mocker, tmp_path):
        """Ensure a deepquery executes correctly."""
        d = tmp_path / "test-output.csv"
        d.mkdir()
        output = d / "test-output.csv"
        mocker.patch.dict(os.environ, {"YELP_API_KEY": self.fake.pystr()})
        mocker.patch.object(YelpAPI, '_query', side_effect=[json.loads(YELP_SEARCH_RESULTS), {}])
        mocker.patch('yelper.core.yelper.deep_link', return_value=async_mock(None), autospec=True)
        await async_deep_query('bike shops', 'Austin, TX', output=output)
        actual = output.read_text()
        expected = 'name,phone,address,zipcode,link,emails\n'
        expected += 'Monkey Wrench Bicycles,+15124672453,"5555 N Lamar Ste L131 Austin, TX 78751",78751,,❌\n'
        expected += 'Bicycle Sport Shop,+15124773472,"517 S Lamar Blvd Austin, TX 78704",78704,,❌\n'
        assert actual == expected


# Search results for "Bike shops in Austin, TX".
YELP_SEARCH_RESULTS = """
{
  "businesses": [
    {
      "id": "WT_d47o-V5xlMNx8trI0-A",
      "alias": "monkey-wrench-bicycles-austin",
      "name": "Monkey Wrench Bicycles",
      "image_url": "https://s3-media3.fl.yelpcdn.com/bphoto/a4Tl6tvBcmXsdAM5Paq7FA/o.jpg",
      "is_closed": false,
      "url": "https://www.yelp.com/biz/monkey-wrench-bicycles-austin?adjust_creative=TbA-w_CgKdY8RAZLNl6BZA&utm_campaign=yelp_api_v3&utm_medium=api_v3_business_search&utm_source=TbA-w_CgKdY8RAZLNl6BZA",
      "review_count": 85,
      "categories": [
        {
          "alias": "bikes",
          "title": "Bikes"
        },
        {
          "alias": "bike_repair_maintenance",
          "title": "Bike Repair/Maintenance"
        }
      ],
      "rating": 5,
      "coordinates": {
        "latitude": 30.3224761537188,
        "longitude": -97.7254818941176
      },
      "transactions": [],
      "price": "$$",
      "location": {
        "address1": "5555 N Lamar",
        "address2": "Ste L131",
        "address3": "",
        "city": "Austin",
        "zip_code": "78751",
        "country": "US",
        "state": "TX",
        "display_address": [
          "5555 N Lamar",
          "Ste L131",
          "Austin, TX 78751"
        ]
      },
      "phone": "+15124672453",
      "display_phone": "(512) 467-2453",
      "distance": 3645.0000325093783
    },
    {
      "id": "wfKxBxJ8RFZj8jOB6Lpn-Q",
      "alias": "bicycle-sport-shop-austin-2",
      "name": "Bicycle Sport Shop",
      "image_url": "https://s3-media3.fl.yelpcdn.com/bphoto/d3F2l_l2O-idm3TMUMgWNQ/o.jpg",
      "is_closed": false,
      "url": "https://www.yelp.com/biz/bicycle-sport-shop-austin-2?adjust_creative=TbA-w_CgKdY8RAZLNl6BZA&utm_campaign=yelp_api_v3&utm_medium=api_v3_business_search&utm_source=TbA-w_CgKdY8RAZLNl6BZA",
      "review_count": 230,
      "categories": [
        {
          "alias": "bikes",
          "title": "Bikes"
        },
        {
          "alias": "bikerentals",
          "title": "Bike Rentals"
        },
        {
          "alias": "bike_repair_maintenance",
          "title": "Bike Repair/Maintenance"
        }
      ],
      "rating": 4.5,
      "coordinates": {
        "latitude": 30.25964,
        "longitude": -97.758156
      },
      "transactions": [],
      "price": "$$",
      "location": {
        "address1": "517 S Lamar Blvd",
        "address2": "",
        "address3": "",
        "city": "Austin",
        "zip_code": "78704",
        "country": "US",
        "state": "TX",
        "display_address": [
          "517 S Lamar Blvd",
          "Austin, TX 78704"
        ]
      },
      "phone": "+15124773472",
      "display_phone": "(512) 477-3472",
      "distance": 5061.350203710105
    }
  ],
  "total": 87,
  "region": {
    "center": {
      "longitude": -97.75772094726562,
      "latitude": 30.305156315977833
    }
  }
}
"""
