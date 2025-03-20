from odoo.upgrade import util


def migrate(cr, version):
    provider_xmlids = [
        (f"payment.payment_provider_{name}", f"payment_{name}")
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
    for xmlid, payment_module in provider_xmlids:
        util.update_record_from_xml(cr, xmlid)
        if util.module_installed(cr, payment_module):
            util.update_record_from_xml(cr, xmlid, from_module=payment_module)

        if xmlid == "payment.payment_provider_transfer":  # Transfer is handled in payment_custom.
            continue
        copy_payment_methods_to_duplicated_providers(cr, xmlid)

    # Now unsupported or user-created payment methods are used for only cosmetic purposes and will
    # not be shown anywhere anymore. As the 'code' field is created in saas-16.5, the payment
    # methods that do not have a code are the ones to be deleted.
    cr.execute("DELETE FROM payment_method WHERE code IS NULL")

    # Activate default pms for active providers, specific codes need to be done at end- of their modules
    activate_default_pms(cr, exclude_codes=["alipay", "custom", "ogone", "payulatam", "payumoney"])


def activate_default_pms(cr, *, code=None, exclude_codes=None):
    assert bool(code) ^ bool(exclude_codes)
    domain = [("state", "!=", "disabled")]
    if exclude_codes:
        domain.append(("code", "not in", exclude_codes))
    else:
        domain.append(("code", "=", code))
    util.env(cr)["payment.provider"].search(domain)._activate_default_pms()


def copy_payment_methods_to_duplicated_providers(cr, xmlid, *, custom_mode=None):
    provider = util.ref(cr, xmlid)
    assert provider

    args = {"provider": provider}
    custom_mode_filter = "true"

    if custom_mode:
        custom_mode_filter = "o.custom_mode = %(custom_mode)s"
        args["custom_mode"] = custom_mode

    query = util.format_query(
        cr,
        """
        SELECT ARRAY_AGG(o.id)
          FROM payment_provider p
          JOIN payment_provider o
            ON (  -- dedicated module installed -> code != none -> match by code
                  (p.code != 'none' AND o.code = p.code)
                  -- dedicated module is not installed -> code = none -> match by module
               OR (p.code = 'none' AND o.module_id = p.module_id)
               )
           AND o.id != p.id
         WHERE p.id = %(provider)s
           AND {}
        """,
        util.SQLStr(custom_mode_filter),
    )
    cr.execute(query, args)
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
