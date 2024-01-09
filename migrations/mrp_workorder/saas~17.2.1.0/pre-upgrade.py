from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "mrp_workorder.mrp_bom_form_view_inherit")
    util.remove_field(cr, "stock.picking.type", "prefill_lot_tablet")
    util.remove_view(cr, "mrp_workorder.view_picking_type_form_inherit_mrp_workorder")
