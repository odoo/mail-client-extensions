from odoo.upgrade import util


def migrate(cr, version):

    cr.execute(
        """
            UPDATE payment_acquirer
               SET provider='custom', custom_mode='onsite'
             WHERE is_onsite_acquirer IS TRUE
        """,
    )
    util.remove_field(cr, "payment.acquirer", "is_onsite_acquirer")
