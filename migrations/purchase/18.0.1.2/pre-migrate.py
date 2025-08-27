from odoo.upgrade import util


def migrate(cr, version):
    util.alter_column_type(cr, "purchase_order", "currency_rate", "numeric")
