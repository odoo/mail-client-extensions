# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "helpdesk_timesheet.project_project_view_form_inherit_helpdesk_timesheet")
    util.remove_field(cr, "helpdesk.ticket", "analytic_tag_ids")
