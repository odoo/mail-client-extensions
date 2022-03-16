from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.ENVIRON["__fix_fk_allowed_cascade"].append(("stock_inventory_line", "product_id"))
