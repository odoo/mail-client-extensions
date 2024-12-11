from odoo.upgrade import util


def migrate(cr, version):
    # column created by mistake in #3234
    util.remove_column(cr, "loyalty_card", "active")
