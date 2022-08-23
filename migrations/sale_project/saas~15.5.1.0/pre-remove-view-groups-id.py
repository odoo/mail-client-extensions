# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "sale_project.project_task_view_form_inherit_sale_line_editable")
    util.remove_view(cr, "sale_project.project_milestone_view_tree_salesman")
    util.remove_view(cr, "sale_project.project_milestone_view_form_salesman")
