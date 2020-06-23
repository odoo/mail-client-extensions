# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.move_field_to_module(cr, "project.project", "timesheet_product_id", "industry_fsm_sale", "sale_timesheet")
    util.create_column(cr, "project_project", "timesheet_product_id", "integer")

    # data
    util.rename_xmlid(cr, "sale_timesheet_enterprise.fsm_time_product", "sale_timesheet.time_product")

    # These two views have been merged. Keep the one with the correct parent (inherit_id) to ensure potential
    # inheriting views still works.
    util.remove_view(cr, "sale_timesheet.project_project_view_form")
    util.rename_xmlid(
        cr, "sale_timesheet.project_view_form_inherit", "sale_timesheet.project_project_view_form", noupdate=False
    )
