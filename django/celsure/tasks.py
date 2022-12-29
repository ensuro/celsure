import logging

import ensuro.wrappers as wrappers
from celery import shared_task
from environs import Env
from ethproto.wadray import _W
from ethproto.wrappers import get_provider

from policies.ethutils import _A
from policies.quote import get_quote

env = Env()

logger = logging.getLogger()


@shared_task
def new_policy(rm_address, model, expiration):
    get_provider()
    quote = get_quote(model=model, expiration=expiration, signed=True)
    eth_rm = wrappers.SignedQuoteRiskModule.connect(rm_address)
    customer = env.str("CUSTOMER_ADDRESS")
    from_address = env.str("REPLICATOR_ADDRESS")

    with eth_rm.as_(from_address):
        receipt = eth_rm.new_policy_(
            _A(model.fix_price),
            _A(quote["premium"]) if quote["premium"] is not None else None,
            _W(quote["loss_prob"]),
            quote["expiration"],
            customer,
            quote["data_hash"],
            quote["signature"]["r"],
            quote["signature"]["vs"],
            quote["valid_until"],
        )

    logger.info(f"Policy created, receipt: {receipt}")
    return receipt
