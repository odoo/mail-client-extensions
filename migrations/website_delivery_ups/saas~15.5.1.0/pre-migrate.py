from odoo.upgrade import util


def migrate(cr, version):
    util.rename_xmlid(
        cr,
        "website_delivery_ups.payment_acquirer_ups_cod",
        "website_delivery_ups.payment_provider_ups_cod",
    )

    cod_acquirer_id = util.ref(cr, "website_delivery_ups.payment_provider_ups_cod")
    cr.execute(
        """
            UPDATE payment_provider
               SET custom_mode = 'cash_on_delivery'
             WHERE id = %s
        """,
        [cod_acquirer_id],
    )
