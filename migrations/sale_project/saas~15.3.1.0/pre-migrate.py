# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    if util.module_installed(cr, "industry_fsm_sale"):
        util.move_field_to_module(cr, "project.task", "invoice_count", "sale_project", "industry_fsm_sale")
    else:
        util.remove_field(cr, "project.task", "invoice_count")
