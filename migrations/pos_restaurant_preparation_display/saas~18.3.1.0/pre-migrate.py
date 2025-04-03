from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "pos.prep.order", "pos_table_id")
