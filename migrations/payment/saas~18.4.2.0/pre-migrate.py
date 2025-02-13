from odoo.upgrade import util


def migrate(cr, version):
    giropay_id = util.ref(cr, "payment.payment_method_giropay")
    if giropay_id:
        provider_xids = (
            "payment.payment_provider_adyen",
            "payment.payment_provider_buckaroo",
            "payment.payment_provider_mollie",
            "payment.payment_provider_stripe",
        )

        provider_ids = list(filter(None, (util.ref(cr, xid) for xid in provider_xids)))

        if provider_ids:
            cr.execute(
                """
                DELETE FROM payment_method_payment_provider_rel
                 WHERE payment_method_id = %s
                   AND payment_provider_id IN %s
                """,
                [giropay_id, tuple(provider_ids)],
            )

        # Rename and archive the method
        util.delete_unused(cr, "payment.payment_method_giropay", deactivate=True)
        util.replace_in_all_jsonb_values(
            cr,
            "payment_method",
            "name",
            util.PGRegexp("(.+)"),
            "\1 (deprecated)",
            extra_filter=cr.mogrify("id = %s", [giropay_id]).decode(),
        )
