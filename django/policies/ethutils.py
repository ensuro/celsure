# Copied from ens-offchain repo - TODO: create a library
import os
from contextlib import contextmanager
from datetime import datetime
from decimal import Decimal

from django.utils.timezone import get_current_timezone
from environs import Env
from ethproto import defender_relay
from ethproto.wadray import make_integer_float

env = Env()

USDC = make_integer_float(env.int("AMOUNT_DECIMALS", 6), env.str("AMOUNT_CLASSNAME", "USDC"))

_A = USDC.from_value

MAX_UINT = 2**256 - 1


def to_decimal(value, decimals=6) -> Decimal:
    return Decimal(value) / Decimal(10**decimals)


def to_float(value, decimals=6) -> float:
    return float(value / 10**decimals)


def to_datetime(timestamp: int) -> datetime:
    return datetime.fromtimestamp(timestamp, tz=get_current_timezone())


def to_epoch(value: datetime) -> int:
    return int(value.timestamp())


def to_bytes32(value: int) -> str:
    ret = hex(value)
    if len(ret) < 66:
        ret = "0x" + "0" * (66 - len(ret)) + ret[2:]
    return ret


@contextmanager
def replace_defender_credentials(credentials_name):
    """
    Context manager that replaces temporarily the defender credentials_name

    Expects environment variables DEFENDER_API_KEY_{credentials_name} and
    DEFENDER_SECRET_KEY_{credentials_name} to be defined

    NOT thread-safe
    """
    secret_key = env.str(f"DEFENDER_SECRET_KEY_{credentials_name}")
    api_key = env.str(f"DEFENDER_API_KEY_{credentials_name}")

    # Backup old values
    token, token_expires = defender_relay.token, defender_relay.token_expires
    defender_relay.token = defender_relay.token_expires = None
    DEFENDER_API_KEY = os.environ.get("DEFENDER_API_KEY", None)
    DEFENDER_SECRET_KEY = os.environ.get("DEFENDER_SECRET_KEY", None)
    os.environ["DEFENDER_API_KEY"] = api_key
    os.environ["DEFENDER_SECRET_KEY"] = secret_key
    try:
        yield
    finally:
        defender_relay.token = token
        defender_relay.token_expires = token_expires
        os.environ["DEFENDER_API_KEY"] = DEFENDER_API_KEY
        os.environ["DEFENDER_SECRET_KEY"] = DEFENDER_SECRET_KEY
