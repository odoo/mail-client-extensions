from odoo.upgrade import util


def migrate(cr, version):
    cr.execute(
        """
        DELETE
          FROM payment_method_payment_provider_rel r
         USING payment_provider p
         WHERE r.payment_provider_id = p.id
           AND p.code = 'worldline'
        """
    )
    xmlid = "payment.payment_provider_worldline"
    util.update_record_from_xml(cr, xmlid)

    provider_id = util.ref(cr, xmlid)
    cr.execute(
        """
        SELECT ARRAY_AGG(o.id)
          FROM payment_provider p
          JOIN payment_provider o
            ON p.code = 'worldline'
           AND o.code = p.code
           AND o.id != p.id
         WHERE p.id = %s
        """,
        [provider_id],
    )
    dup_ids = cr.fetchone()[0]
    PaymentProvider = util.env(cr)["payment.provider"]
    if dup_ids:
        cr.execute(
            """
            INSERT INTO payment_method_payment_provider_rel (payment_method_id, payment_provider_id)
            SELECT r.payment_method_id, UNNEST(%s)
              FROM payment_method_payment_provider_rel r
             WHERE r.payment_provider_id = %s
            """,
            [dup_ids, provider_id],
        )
        updated_provider = PaymentProvider.browse(provider_id)
        PaymentProvider.browse(dup_ids).write(
            {
                "image_128": updated_provider.image_128,
                "module_id": updated_provider.module_id,
                "redirect_form_view_id": updated_provider.redirect_form_view_id,
            }
        )

    domain = [("state", "!=", "disabled"), ("code", "=", "worldline")]
    PaymentProvider.search(domain)._activate_default_pms()

    if util.module_installed(cr, "account_payment"):
        cr.execute(
            """
            UPDATE account_payment_method
               SET code = 'worldline',
                   name = jsonb_build_object('en_US', 'Worldline')
             WHERE code = 'ogone'
            """
        )
