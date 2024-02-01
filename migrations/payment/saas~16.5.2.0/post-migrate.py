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


def copy_payment_methods_to_duplicated_providers(cr, xmlid, *, custom_mode=None):
    provider = util.ref(cr, xmlid)
    assert provider

    args = {"provider": provider}
    custom_mode_filter = "true"

    if custom_mode:
        custom_mode_filter = "o.custom_mode = %(custom_mode)s"
        args["custom_mode"] = custom_mode

    cr.execute(
        f"""
        SELECT ARRAY_AGG(o.id)
          FROM payment_provider p
          JOIN payment_provider o
            ON o.code = p.code
           AND o.module_id = p.module_id
           AND o.id != p.id
         WHERE p.id = %(provider)s
           AND {custom_mode_filter}
        """,
        args,
    )
    dup_ids = cr.fetchone()[0]
    if not dup_ids:
        return
    args["ids"] = dup_ids
    cr.execute(
        """
        DELETE FROM payment_method_payment_provider_rel r
              WHERE r.payment_provider_id = ANY(%(ids)s);

        INSERT INTO payment_method_payment_provider_rel (payment_method_id, payment_provider_id)
        SELECT r.payment_method_id, UNNEST(%(ids)s)
          FROM payment_method_payment_provider_rel r
         WHERE r.payment_provider_id = %(provider)s
        """,
        args,
    )
