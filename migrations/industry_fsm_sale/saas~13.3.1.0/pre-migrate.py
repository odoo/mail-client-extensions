# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "project.task", "fsm_to_invoice")
    util.remove_view(cr, "industry_fsm_sale.project_task_view_search")
