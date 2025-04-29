from odoo.upgrade import util


def migrate(cr, version):
    def is_done_adapter(leaf, _or, _neg):
        _, op, right = leaf
        if op == "!=":
            right = not right
        new_op = "in" if right else "not in"
        return [("state", new_op, ("done", "cancel"))]

    util.update_field_usage(cr, "stock.move", "is_done", "state", domain_adapter=is_done_adapter)
    util.remove_field(cr, "stock.move", "is_done")
    util.remove_field(cr, "mrp.bom.line", "allowed_uom_ids")
    util.convert_m2o_field_to_m2m(cr, "mrp.production", "lot_producing_id")
    util.rename_field(cr, "mrp.workorder", "finished_lot_id", "finished_lot_ids")
    util.remove_field(cr, "stock.move", "order_finished_lot_id")
    util.remove_model(cr, "mrp.batch.produce")
    util.remove_field(cr, "stock.warehouse.orderpoint", "manufacturing_visibility_days")
    util.remove_field(cr, "res.company", "manufacturing_lead")
    util.remove_field(cr, "res.config.settings", "manufacturing_lead")
    util.remove_field(cr, "res.config.settings", "use_manufacturing_lead")
    cr.execute("DELETE FROM ir_config_parameter WHERE key='mrp.use_manufacturing_lead'")
    util.create_column(cr, "mrp_bom", "enable_batch_size", "boolean", default=False)
    util.create_column(cr, "mrp_bom", "batch_size", "numeric", default=1.0)
