# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.move_field_to_module(cr, "project.task", "invoice_count", "industry_fsm_sale", "sale_project")
    util.move_field_to_module(cr, "project.task", "fsm_to_invoice", "industry_fsm_sale", "sale_project")
    util.rename_field(cr, "project.task", "fsm_to_invoice", "task_to_invoice", update_references=True)
    util.rename_xmlid(
        cr,
        *util.expand_braces(
            "industry_fsm_sale.{project_task_server_action_batch_invoice_fsm,project_task_server_action_batch_invoice}"
        )
    )
    util.rename_xmlid(
        cr, *util.expand_braces("{industry_fsm_sale,sale_project}.project_task_server_action_batch_invoice")
    )
