# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    eb = util.expand_braces
    util.rename_xmlid(cr, *eb("{project_forecast,planning}.planning_view_gantt_no_sample"))
    util.create_column(cr, "planning_slot", "state", "varchar", default="draft")
    cr.execute("UPDATE planning_slot SET state = 'published' where is_published=True")

    def adapter(leaf, _, __):
        left, operator, right = leaf
        operator = "=" if bool(right) else "!="
        return [(left, operator, "published")]

    util.update_field_references(cr, "is_published", "state", only_models=("planning.slot",), domain_adapter=adapter)
    util.remove_field(cr, "planning.slot", "is_published")

    util.rename_xmlid(cr, *eb("planning.planning_menu_schedule_by_{employee,resource}"))
    util.rename_xmlid(cr, *eb("planning.planning_action_schedule_by_{employee,resource}"))
    util.rename_xmlid(cr, *eb("planning.planning_action_schedule_by_{employee,resource}_view_gantt"))

    util.create_column(cr, "planning_slot", "resource_id", "int4")
    cr.execute(
        """
            UPDATE planning_slot AS s
               SET resource_id = e.resource_id
              FROM hr_employee AS e
             WHERE s.employee_id = e.id
               AND s.company_id = e.company_id
        """
    )

    util.create_column(cr, "resource_resource", "color", "int4", default=0)
