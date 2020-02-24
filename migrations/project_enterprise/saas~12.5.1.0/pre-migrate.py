# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.remove_field(cr, "project.project", "allow_planning")
    util.remove_field(cr, "project.task", "allow_planning")

    util.remove_view(cr, "project_enterprise.project_view_kanban_inherit")
    util.remove_view(cr, "project_enterprise.project_task_view_form_allow_planning_domain")
    util.remove_view(cr, "project_enterprise.project_view_form_simplified_inherit")
    util.remove_view(cr, "project_enterprise.project_view_form_inherit")

    for pf in {"email", "phone", "mobile", "zip"}:
        util.move_field_to_module(cr, "project.task", f"partner_{pf}", "industry_fsm", "project_enterprise")
