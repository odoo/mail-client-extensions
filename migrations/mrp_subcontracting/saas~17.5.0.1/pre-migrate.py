from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "stock.return.picking", "subcontract_location_id")
    util.remove_view(cr, "mrp_subcontracting.view_stock_return_picking_form_subcontracting")
