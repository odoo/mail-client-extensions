from odoo.upgrade import util


def migrate(cr, version):
    util.move_field_to_module(cr, "maintenance.equipment", "match_serial", "maintenance", "stock_maintenance")
