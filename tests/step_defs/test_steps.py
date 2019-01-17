"""Define the feature test steps."""
import asyncio
import json
import os

from faker import Faker
import pytest
from pytest_bdd import given
from pytest_bdd import scenario
from pytest_bdd import then
from yelpapi import YelpAPI

from yelper.core.yelper import async_deep_query
from tests import mock_data


# The scenario MUST be defined here, otherwise it does not find the steps.
@scenario('../features/collect.feature', 'Collect information')
def test_collect_information():
    """Ensure a user retrieves correct information."""


def async_mock(result):
    """Create an awaitable object to simplify mocking awaitable functions."""
    f = asyncio.Future()
    f.set_result(result)
    return f


@given('the user wants to store the results in a CSV file')
def create_tmp_csv_file(tmp_path, scope='session'):
    d = tmp_path / 'sub'
    d.mkdir()
    output = d / "test-output.csv"

    return output


# Note: If this step is made as a `when`, the `create_tmp_csv_file` does not behave properly or is not found and the
# test will break.
@given('the user research for "bike shops" in "Austin, TX"')
@pytest.mark.asyncio
async def research(mocker, create_tmp_csv_file):
    fake = Faker()
    mocker.patch.dict(os.environ, {"YELP_API_KEY": fake.pystr()})
    mocker.patch.object(YelpAPI, '_query', side_effect=[json.loads(mock_data.YELP_SEARCH_RESULTS), {}])
    mocker.patch('yelper.core.yelper.deep_link', return_value=async_mock(None), autospec=True)

    await async_deep_query('bike shops', 'Austin, TX', output=create_tmp_csv_file)


@then('the generated file contains the collected data')
def ensure_results(create_tmp_csv_file):
    output = create_tmp_csv_file
    actual = output.read_text()
    expected = mock_data.MOCKED_CSV_FILE_CONTENT
    assert actual == expected
