from odoo.upgrade import util


def migrate(cr, version):
    util.remove_column(cr, "mrp_workcenter_productivity_loss", "loss_type")
    util.remove_column(cr, "mrp_workcenter_productivity", "loss_type")
    util.remove_column(cr, "mrp_workorder", "product_id")
    util.remove_column(cr, "stock_move", "order_finished_lot_id")
    util.remove_record(cr, "mrp.act_product_mrp_production_workcenter")

    util.remove_field(cr, "mrp.production", "product_uom_category_id")
    util.remove_field(cr, "mrp.bom.byproduct", "product_uom_category_id")
    util.remove_field(cr, "mrp.bom.line", "product_uom_category_id")
    util.remove_field(cr, "mrp.bom", "product_uom_category_id")
