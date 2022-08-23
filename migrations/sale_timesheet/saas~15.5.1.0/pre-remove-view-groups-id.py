# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "sale_timesheet.project_project_view_form_salesman")
    util.remove_view(cr, "sale_timesheet.project_task_view_form_inherit_sale_timesheet_editable")
