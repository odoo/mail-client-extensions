from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "payment_acquirer", "is_published", "boolean", default=True)
    util.rename_field(cr, "payment.acquirer", "country_ids", "available_country_ids")
    util.rename_field(cr, "payment.token", "name", "payment_details")
    util.parallel_execute(
        cr,
        util.explode_query_range(
            cr,
            """
                UPDATE payment_token
                   SET payment_details = RIGHT(payment_details, 4)
                 WHERE payment_details IS NOT NULL
            """,
            table="payment_token",
        ),
    )

    util.rename_xmlid(cr, "payment.payment_acquirer_test", "payment.payment_acquirer_demo")
    util.remove_field(cr, "payment.acquirer", "description")
    util.remove_field(cr, "payment.link.wizard", "access_token")

    eb = util.expand_braces
    for provider in {"alipay", "ogone", "payulatam", "payumoney"}:
        if util.module_installed(cr, f"payment_{provider}"):
            util.rename_xmlid(
                cr, f"payment.payment_acquirer_{provider}", f"payment_{provider}.payment_provider_{provider}"
            )
        else:
            util.remove_record(cr, f"payment.payment_acquirer_{provider}")

    util.rename_model(cr, "payment.acquirer", "payment.provider")
    util.rename_model(cr, "payment.acquirer.onboarding.wizard", "payment.provider.onboarding.wizard")

    util.rename_field(cr, "payment.icon", "acquirer_ids", "provider_ids")
    cr.execute(
        """
        ALTER TABLE payment_acquirer_payment_icon_rel
          RENAME TO payment_provider_payment_icon_rel
    """
    )
    cr.execute(
        """
        ALTER TABLE payment_provider_payment_icon_rel
      RENAME COLUMN payment_acquirer_id
                 TO payment_provider_id
    """
    )

    util.rename_field(cr, "payment.provider", "provider", "code")

    util.rename_field(cr, "payment.token", "acquirer_id", "provider_id")
    util.rename_field(cr, "payment.token", "acquirer_ref", "provider_ref")
    util.rename_field(cr, "payment.token", "provider", "provider_code")

    util.rename_field(cr, "payment.transaction", "acquirer_id", "provider_id")
    util.rename_field(cr, "payment.transaction", "provider", "provider_code")
    util.rename_field(cr, "payment.transaction", "acquirer_reference", "provider_reference")

    util.rename_field(cr, "res.company", "payment_acquirer_onboarding_state", "payment_provider_onboarding_state")

    util.rename_field(cr, "payment.link.wizard", "available_acquirer_ids", "available_provider_ids")
    util.rename_field(cr, "payment.link.wizard", "has_multiple_acquirers", "has_multiple_providers")
    util.rename_field(cr, "payment.link.wizard", "payment_acquirer_selection", "payment_provider_selection")

    for provider in (
        "adyen",
        "authorize",
        "buckaroo",
        "demo",  # actually renamed from `test` above
        "flutterwave",
        "mollie",
        "paypal",
        "sepa_direct_debit",
        "sips",
        "stripe",
        "transfer",
    ):
        util.rename_xmlid(cr, *eb(f"payment.payment_{{acquirer,provider}}_{provider}"))

    util.rename_xmlid(cr, "payment.payment_acquirer_search", "payment.payment_provider_search")
    util.rename_xmlid(cr, "payment.payment_acquirer_kanban", "payment.payment_provider_kanban")
    util.rename_xmlid(cr, "payment.payment_acquirer_list", "payment.payment_provider_list")
    util.rename_xmlid(cr, "payment.payment_acquirer_form", "payment.payment_provider_form")
    util.rename_xmlid(
        cr, "payment.payment_acquirer_onboarding_wizard_form", "payment.payment_provider_onboarding_wizard_form"
    )

    util.rename_xmlid(cr, *eb("payment.payment_{acquirer,provider}_company_rule"))
    util.rename_xmlid(cr, *eb("payment.payment_{acquirer,provider}_onboarding_wizard"))
    util.rename_xmlid(cr, *eb("payment.payment_{acquirer,provider}_system"))

    util.rename_xmlid(cr, "payment.action_payment_acquirer", "payment.action_payment_provider")
