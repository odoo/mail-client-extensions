from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "mrp_workorder", "sequence", "int4", default=100)
    query = """
        UPDATE mrp_workorder o
           SET sequence = COALESCE(NULLIF(w.sequence, 0), 100)
          FROM mrp_routing_workcenter w
         WHERE w.id = o.operation_id
    """
    util.explode_execute(cr, query, table="mrp_workorder", alias="o")
