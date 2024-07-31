from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "mrp.workcenter", "allow_employee")
    util.remove_field(cr, "mrp.workorder", "allow_employee")
    if not util.column_exists(cr, "mrp_workcenter_productivity", "employee_id"):
        # mrp_workorder_hr was merged into mrp_workorder in this version
        util.create_column(cr, "mrp_workcenter_productivity", "employee_id", "int4")
    util.explode_execute(
        cr,
        """
        UPDATE mrp_workcenter_productivity mwp
           SET employee_id = emp.id
          FROM hr_employee emp
         WHERE mwp.user_id = emp.user_id
           AND mwp.company_id = emp.company_id
           AND mwp.employee_id IS NULL
        """,
        table="mrp_workcenter_productivity",
        alias="mwp",
    )
    util.remove_view(cr, "mrp_workorder.mrp_routing_workcenter_form_view_inherit")
    util.remove_view(cr, "mrp_workorder.mrp_workcenter_tree_view_inherit")
    util.remove_view(cr, "mrp_workorder.mrp_production_workorder_tree_editable_view_connect")
    util.remove_view(cr, "mrp_workorder.mrp_production_workorder_tree_editable_view_inherit_workorder_hr")
    util.remove_view(cr, "mrp_workorder.mrp_workorder_view_kanban")
    util.remove_view(cr, "mrp_workorder.mrp_workorder_view_form_inherit_workorder_hr")
    util.remove_view(cr, "mrp_workorder.mrp_workorder_view_tablet_form_inherit_workorder_hr")
