from odoo.upgrade import util


def migrate(cr, version):

    cr.execute(
        """
            UPDATE payment_provider
               SET code='custom', custom_mode='onsite'
             WHERE is_onsite_acquirer IS TRUE
        """,
    )
    util.remove_field(cr, "payment.provider", "is_onsite_acquirer")

    util.rename_xmlid(
        cr, "website_sale_picking.payment_acquirer_onsite", "website_sale_picking.payment_provider_onsite"
    )
