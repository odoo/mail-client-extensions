import logging

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
        "bancontact",
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
    cr.execute(
        """
            DELETE FROM payment_method_payment_provider_rel r
                  USING ir_model_data m
                  WHERE m.model = 'payment.provider'
                    AND m.res_id = r.payment_provider_id
                    AND CONCAT(m.module, '.', m.name) = ANY(%s)
        """,
        [provider_xmlids],
    )

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

    gone = """
        payment_method_airtel_money
        payment_method_apple_pay
        payment_method_barter_by_flutterwave
        payment_method_bbva_bancomer
        payment_method_citibanamex
        payment_method_mtn_mobile_money
        payment_method_sadad
        payment_method_webmoney
        payment_method_western_union
    """
    util.delete_unused(cr, *[f"payment.{pm}" for pm in util.splitlines(gone)])
