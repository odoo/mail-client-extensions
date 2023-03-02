from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "event_booth_category", "price_incl", "int4")
