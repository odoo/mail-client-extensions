# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "res.config.settings", "module_hr_org_chart")
    util.rename_xmlid(cr, "hr.open_module_tree_department", "hr.hr_department_kanban_action")
