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


def json_rpc_body_matcher(r1, r2):
    """Matcher that detects jsonrpc calls and ignores id parameter (used for sequencing calls)"""
    transformer = matchers._get_transformer(r1)
    r2_transformer = matchers._get_transformer(r2)
    if transformer != r2_transformer:
        transformer = matchers._identity
    body_r1, body_r2 = transformer(matchers.read_body(r1)), transformer(matchers.read_body(r2))
    if "jsonrpc" in body_r2 and "jsonrpc" in body_r1:
        body_r1.pop("id", None)
        body_r2.pop("id", None)
        assert body_r1 == body_r2, f"Different jsonrpc calls {body_r1} != {body_r2}"
    else:
        assert body_r1 == body_r2


def pytest_recording_configure(config, vcr):
    vcr.register_matcher("uri_regex", uri_regex_matcher)
    vcr.register_matcher("json_rpc_body", json_rpc_body_matcher)
