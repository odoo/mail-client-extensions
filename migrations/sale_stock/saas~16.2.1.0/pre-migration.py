from odoo.upgrade import util


def migrate(cr, version):
    util.rename_xmlid(cr, "sale_stock.view_quotation_tree", "sale_stock.sale_order_tree")
