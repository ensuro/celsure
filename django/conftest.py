import re

import pytest
from rest_framework.test import APIClient
from vcr import matchers


@pytest.fixture(autouse=True)
def mock_register_contract_path(mocker):
    mocker.patch("policies.apps", "register_contract_path", lambda: None)


@pytest.fixture
def api_client():
    return APIClient()


def uri_regex_matcher(r1, r2):
    if r2.uri.startswith("/"):
        assert re.match(r2.uri[1:], r1.uri), f"'{r1.uri}' doesn't match regex {r2.uri}"
    else:
        return matchers.uri(r1, r2)


def pytest_recording_configure(config, vcr):
    vcr.register_matcher("uri_regex", uri_regex_matcher)
