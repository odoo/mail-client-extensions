# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    eb = util.expand_braces
    util.rename_xmlid(cr, *eb("{industry_fsm_sale,sale_timesheet_enterprise}.fsm_time_product"))

    gone = """
        project_view_form_inherit
        project_project_view_form
        project_task_view_form
    """

    for view in util.splitlines(gone):
        util.remove_view(cr, f"sale_timesheet_enterprise.{view}")
