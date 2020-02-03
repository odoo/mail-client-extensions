# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.remove_record(cr, "sale_timesheet.product_template_action_fixed")
    util.remove_record(cr, "sale_timesheet.product_template_action_milestone")
    util.remove_view(cr, "sale_timesheet.project_project_view_search")
    util.remove_view(cr, "sale_timesheet.project_project_view_form")
    util.remove_view(cr, "sale_timesheet.project_task_view_form_sale_order")
