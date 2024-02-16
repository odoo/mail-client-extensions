from odoo.upgrade import util


def migrate(cr, version):
    util.remove_record(cr, "stock_account.inventory_aging_action")
    util.remove_record(cr, "stock_account.menu_inventory_aging")
