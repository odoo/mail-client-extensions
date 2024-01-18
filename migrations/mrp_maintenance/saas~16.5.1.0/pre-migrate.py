# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "maintenance_stage", "create_leaves", "boolean")
    cr.execute("UPDATE maintenance_stage SET create_leaves = true WHERE done is not true")

    util.create_column(cr, "maintenance_request", "maintenance_for", "varchar", default="equipment")
    util.create_column(
        cr, "maintenance_request", "workcenter_id", "int4", fk_table="mrp_workcenter", on_delete_action="RESTRICT"
    )
    query = """
        UPDATE maintenance_request r
           SET workcenter_id = e.workcenter_id
          FROM maintenance_equipment e
         WHERE e.id = r.equipment_id
           AND e.workcenter_id IS NOT NULL
    """
    util.explode_execute(cr, query, table="maintenance_request", alias="r")

    util.create_column(cr, "mrp_workcenter", "effective_date", "date")
    util.create_column(
        cr, "mrp_workcenter", "maintenance_team_id", "int4", fk_table="maintenance_team", on_delete_action="SET NULL"
    )
    util.create_column(
        cr, "mrp_workcenter", "technician_user_id", "int4", fk_table="res_users", on_delete_action="SET NULL"
    )
    util.create_column(cr, "mrp_workcenter", "maintenance_count", "int4", default=0)
    util.create_column(cr, "mrp_workcenter", "maintenance_open_count", "int4", default=0)
    util.create_column(cr, "mrp_workcenter", "expected_mtbf", "int4", default=0)
    query = """
        UPDATE mrp_workcenter
           SET effective_date = create_date
    """
    util.parallel_execute(cr, util.explode_query_range(cr, query, table="mrp_workcenter"))
