from odoo.upgrade import util


def migrate(cr, version):
    if util.module_installed(cr, "stock_maintenance"):
        util.move_field_to_module(cr, "maintenance.equipment", "match_serial", "maintenance", "stock_maintenance")
    else:
        util.remove_field(cr, "maintenance.equipment", "match_serial")
