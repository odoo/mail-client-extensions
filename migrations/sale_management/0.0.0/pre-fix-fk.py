from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.ENVIRON["fix_fk_allowed_cascade"].append(("sale_order_option", "product_id"))
