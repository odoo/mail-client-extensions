from odoo.upgrade import util


def migrate(cr, version):
    util.remove_menus(cr, [util.ref(cr, "planning.planning_menu_settings_tag")])
    util.remove_record(cr, "planning.planning_tag_action")
    util.remove_view(cr, "planning.planning_tags_view_tree")
    util.remove_field(cr, "planning.analysis.report", "tag_ids")
    util.remove_field(cr, "planning.slot", "tag_ids")
    util.remove_model(cr, "planning.tag")
    util.create_m2m(cr, "resource_resource_planning_role_rel", "resource_resource", "planning_role")
    cr.execute(
        """
            INSERT INTO resource_resource_planning_role_rel(resource_resource_id, planning_role_id)
                 SELECT E.resource_id, EPR.planning_role_id
                   FROM hr_employee_planning_role_rel EPR
             INNER JOIN hr_employee E ON EPR.hr_employee_id = E.id
        """
    )
    cr.execute("DROP TABLE hr_employee_planning_role_rel")
    util.remove_field(cr, "planning.role", "employee_ids")
