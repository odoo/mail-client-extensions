# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.merge_module(cr, "sale_timesheet_edit", "sale_timesheet", without_deps=True)
    if util.has_enterprise():
        util.new_module(cr, "helpdesk_fsm_report", deps={"helpdesk_fsm", "industry_fsm_report"}, auto_install=True)
