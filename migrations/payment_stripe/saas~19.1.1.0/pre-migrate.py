from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "payment_stripe.no_pms_available_warning")
