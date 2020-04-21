# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.create_column(cr, "project_project", "is_fsm", "boolean")
    util.create_column(cr, "project_project", "allow_material", "boolean")
    util.create_column(cr, "project_project", "allow_quotations", "boolean")
    util.create_column(cr, "project_task", "fsm_done", "boolean")

    util.remove_field(cr, "project.project", "product_template_ids")
    util.remove_field(cr, "project.task", "material_line_ids")
    util.remove_field(cr, "project.task", "product_template_ids")
    util.remove_field(cr, "project.task", "fsm_state")
    util.remove_model(cr, "product.task.map")

    cr.execute("UPDATE ir_ui_menu SET action=NULL WHERE id=%s", (util.ref(cr, "industry_fsm.fsm_tasks_menu"),))
