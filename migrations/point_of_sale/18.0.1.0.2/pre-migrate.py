from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "pos_order", "email", "varchar")
    util.create_column(cr, "pos_order", "mobile", "varchar")
