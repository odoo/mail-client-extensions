from odoo.upgrade import util


def migrate(cr, version):
    util.remove_column(cr, "quality_check", "lot_name")
