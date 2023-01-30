# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "industry_fsm_sale.view_task_form2_inherit_sale_timesheet")
    util.remove_view(cr, "industry_fsm_sale.project_task_view_form_quotation")
