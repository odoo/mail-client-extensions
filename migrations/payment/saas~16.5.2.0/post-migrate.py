import logging

from odoo import Command
from odoo.osv import expression

from odoo.upgrade import util

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    # Payment methods that existed prior to saas-16.5 have noupdate=1.
    existing_pms = [
        "visa",
        "mastercard",
        "amex",
        "discover",
        "diners",
        "rupay",
        "jcb",
        "maestro",
        "cirrus",
        "unionpay",
        "paypal",
        "apple_pay",
        "bancontact",
        "western_union",
        "sepa_direct_debit",
        "ideal",
        "giropay",
        "eps",
        "p24",
        "mpesa",
        "mada",
        "kbc_cbc",
        "codensa",
    ]
    for pm in existing_pms:
        util.update_record_from_xml(cr, f"payment.payment_method_{pm}")

    # Bypass the noupdate=1 on providers to re-assign their new payment methods.
    provider_xmlids = [
        f"payment.payment_provider_{name}"
        for name in (
            "adyen",
            "aps",
            "asiapay",
            "authorize",
            "buckaroo",
            "demo",
            "flutterwave",
            "mercado_pago",
            "mollie",
            "paypal",
            "razorpay",
            "sepa_direct_debit",
            "sips",
            "stripe",
            "transfer",
        )
    ]
    for xmlid in provider_xmlids:
        util.update_record_from_xml(cr, xmlid)

    # Copy the payment methods of providers with the xmlid to their duplicates (same code).
    for xmlid in provider_xmlids:
        if xmlid == "payment.payment_provider_transfer":  # Transfer is handled in payment_custom.
            continue
        copy_payment_methods_to_duplicated_providers(cr, xmlid)

    # Now unsupported or user-created payment methods are used for only cosmetic purposes and will
    # not be shown anywhere anymore. As the 'code' field is created in saas-16.5, the payment
    # methods that do not have a code are the ones to be deleted.
    cr.execute("DELETE FROM payment_method WHERE code IS NULL")

    # Set the payment method "Unknown" on existing payment.transaction and payment.token records.
    unknown_pm_id = util.ref(cr, "payment.payment_method_unknown")
    util.explode_execute(
        cr,
        cr.mogrify("UPDATE payment_transaction SET payment_method_id=%s", [unknown_pm_id]).decode(),
        table="payment_transaction",
    )
    util.explode_execute(
        cr, cr.mogrify("UPDATE payment_token SET payment_method_id=%s", [unknown_pm_id]).decode(), table="payment_token"
    )
    # TODO: include link to documentation in migration report after it is written.


def copy_payment_methods_to_duplicated_providers(cr, xmlid, extra_domain=None):
    env = util.env(cr)
    base_provider = env.ref(xmlid)
    if not base_provider:
        msg = f"Base provider with xmlid {xmlid} not found."
        _logger.critical(msg)
        return
    domain = [("code", "=", base_provider.code), ("id", "!=", base_provider.id)]
    if extra_domain:
        expression.AND([domain, extra_domain])
    duplicated_providers = env["payment.provider"].search(domain)
    for duplicate in duplicated_providers:
        duplicate.payment_method_ids = [
            Command.set(base_provider.with_context(active_test=False).payment_method_ids.ids)
        ]
