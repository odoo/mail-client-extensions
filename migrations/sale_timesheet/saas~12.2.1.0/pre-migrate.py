# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.remove_view(cr, "sale_timesheet.qunit_suite")
    util.remove_record(cr, "sale_timesheet.project_timesheet_action_client_timesheet_plan")
