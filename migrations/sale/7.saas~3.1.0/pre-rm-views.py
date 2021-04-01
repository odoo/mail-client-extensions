from openerp.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.remove_view(cr, "sale.view_order_product_tree")
