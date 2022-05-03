# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "industry_fsm_report.portal_my_worksheet")
    util.remove_view(cr, "industry_fsm_report.project_project_view_form_simplified_inherit")
