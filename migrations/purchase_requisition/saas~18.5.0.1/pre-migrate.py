from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "purchase_requisition.purchase_order_tree_inherit_purchase_requisition")
