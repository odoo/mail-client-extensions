from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "pos.order", "origin_table_id")
