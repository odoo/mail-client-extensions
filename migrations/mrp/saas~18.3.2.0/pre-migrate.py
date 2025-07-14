from odoo.upgrade import util


def migrate(cr, version):
    util.remove_column(cr, "mrp_workorder", "product_uom_id")
    util.rename_field(cr, "mrp.workcenter", "workorder_pending_count", "workorder_blocked_count")
    util.change_field_selection_values(cr, "mrp.workorder", "state", {"pending": "blocked", "waiting": "blocked"})
    util.remove_field(cr, "mrp.routing.workcenter", "worksheet_type")
    util.remove_field(cr, "mrp.routing.workcenter", "note")
    util.remove_field(cr, "mrp.routing.workcenter", "worksheet", keep_as_attachments=True)
    util.remove_field(cr, "mrp.routing.workcenter", "worksheet_google_slide")
    util.remove_field(cr, "mrp.workorder", "has_worksheet")
    util.remove_field(cr, "mrp.workorder", "worksheet")
    util.remove_field(cr, "mrp.workorder", "worksheet_type")
    util.remove_field(cr, "mrp.workorder", "worksheet_google_slide")
    util.remove_field(cr, "mrp.workorder", "operation_note")
    util.remove_field(cr, "mrp.production.split", "counter")
    util.remove_field(cr, "mrp.bom.line", "manual_consumption")
    util.remove_constraint(cr, "mrp_workcenter_capacity", "mrp_workcenter_capacity_unique_product")
    util.create_column(cr, "mrp_workcenter_capacity", "product_uom_id", "integer")
    query = """
        UPDATE mrp_workcenter_capacity wcc
           SET product_uom_id = pt.uom_id
          FROM product_template pt
          JOIN product_product pp
            ON pp.product_tmpl_id = pt.id
         WHERE wcc.product_id = pp.id
    """
    util.explode_execute(cr, query, table="mrp_workcenter_capacity", alias="wcc")
    unit = util.ref(cr, "uom.product_uom_unit")
    cr.execute("ALTER TABLE mrp_workcenter_capacity ALTER COLUMN product_id DROP NOT NULL")
    cr.execute(
        """
        INSERT INTO mrp_workcenter_capacity
                    (workcenter_id, product_id, product_uom_id, capacity, time_start, time_stop)
             SELECT id, NULL, %s, default_capacity, time_start, time_stop
               FROM mrp_workcenter
              WHERE default_capacity <> 1
        """,
        [unit],
    )
    util.remove_field(cr, "mrp.workcenter", "default_capacity")

    # unlink workorder for the component moves that are not consumed in any operation
    # See https://github.com/odoo/odoo/commit/13939fb793a78f13670ea861037ad7d25098ded1
    util.explode_execute(
        cr,
        """
        UPDATE stock_move
           SET workorder_id = NULL
         WHERE workorder_id IS NOT NULL
           AND operation_id IS NULL
        """,
        table="stock_move",
    )
