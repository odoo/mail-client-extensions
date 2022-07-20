from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "payment_acquirer", "is_published", "boolean", default=True)
    util.rename_field(cr, "payment.acquirer", "country_ids", "available_country_ids")
