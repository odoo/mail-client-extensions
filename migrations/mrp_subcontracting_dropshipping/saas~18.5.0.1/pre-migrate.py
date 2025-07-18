from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "stock.warehouse", "subcontracting_dropshipping_to_resupply")
    util.remove_view(cr, "mrp_subcontracting_dropshipping.view_warehouse_inherit_mrp_subcontracting_dropshipping")
