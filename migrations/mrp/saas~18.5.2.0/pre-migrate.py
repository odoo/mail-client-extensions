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

    util.rename_field(cr, "stock.reference", "mrp_production_ids", "production_ids")
    # convert the old procurement group into the new production group then replace procurement group by the reference
    cr.execute(
        """
        CREATE TABLE mrp_production_group (
                        id SERIAL PRIMARY KEY,
                        name varchar NOT NULL,
                        _upg_orig_production_id int
                    );
        """
    )
    util.create_m2m(
        cr,
        "mrp_production_group_rel",
        "mrp_production_group",
        "mrp_production_group",
        "parent_group_id",
        "child_group_id",
    )
    util.create_column(cr, "mrp_production", "production_group_id", "int")
    query_create_group = """
        WITH inserted AS (
            INSERT INTO mrp_production_group (name, _upg_orig_production_id)
                 SELECT name, id
                   FROM mrp_production
                  WHERE procurement_group_id IS NOT NULL
                    AND {parallel_filter}
              RETURNING id group_id, _upg_orig_production_id prod_id
        ) UPDATE mrp_production p
             SET production_group_id = inserted.group_id
            FROM inserted
           WHERE inserted.prod_id = p.id
    """
    util.explode_execute(cr, query_create_group, table="mrp_production")
    util.remove_column(cr, "mrp_production_group", "_upg_orig_production_id")

    util.convert_m2o_field_to_m2m(
        cr,
        "mrp.production",
        "procurement_group_id",
        new_name="reference_ids",
        m2m_table="stock_reference_production_rel",
        col1="production_id",
        col2="reference_id",
    )
    util.make_field_non_stored(cr, "stock.warehouse", "manufacture_to_resupply")
