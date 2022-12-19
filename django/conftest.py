import re

import pytest
from rest_framework.test import APIClient
from vcr import matchers


@pytest.fixture
def api_client():
    return APIClient()


def uri_regex_matcher(r1, r2):
    if r2.uri.startswith("/"):
        assert re.match(r2.uri[1:], r1.uri), f"'{r1.uri}' doesn't match regex {r2.uri}"
    else:
        return matchers.uri(r1, r2)


def api_body_matcher(r1, r2):
    """Matcher that detects MotionsCloud API calls (used for sequencing calls)"""
    transformer = matchers._get_transformer(r1)
    r2_transformer = matchers._get_transformer(r2)
    if transformer != r2_transformer:
        transformer = matchers._identity
    body_r1, body_r2 = transformer(matchers.read_body(r1)), transformer(matchers.read_body(r2))
    assert body_r1 == body_r2


def pytest_recording_configure(config, vcr):
    vcr.register_matcher("uri_regex", uri_regex_matcher)
    vcr.register_matcher("api_body", api_body_matcher)
