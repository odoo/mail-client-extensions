from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "mrp.view_production_gantt")
    util.remove_act_window_view_mode(cr, "mrp.production", "gantt")

    cr.execute("DELETE FROM mrp_routing_workcenter WHERE bom_id IS NULL")

    util.remove_column(cr, "mrp_routing_workcenter", "company_id")
    util.remove_column(cr, "mrp_workorder", "consumption")

    util.explode_execute(
        cr,
        """
        UPDATE stock_move AS sm
           SET picking_type_id = mp.picking_type_id
          FROM mrp_production AS mp
         WHERE COALESCE(sm.raw_material_production_id, sm.production_id) = mp.id
        """,
        table="stock_move",
        alias="sm",
    )
