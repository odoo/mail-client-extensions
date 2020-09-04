# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    if util.has_enterprise():
        util.new_module(cr, "helpdesk_fsm_report", deps={"helpdesk_fsm", "industry_fsm_report"}, auto_install=True)
