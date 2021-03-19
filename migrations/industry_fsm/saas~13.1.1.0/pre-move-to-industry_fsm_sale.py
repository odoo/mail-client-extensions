# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    assert util.module_installed(cr, "industry_fsm_sale")  # should always be true due to dependencies
    eb = util.expand_braces

    renames = util.splitlines(
        """
        # products
        fsm_time_product

        # group
        group_fsm_quotation_from_task

        # views
        assets_backend
        project_task_view_form_quotation
        view_product_product_kanban_material

        # actions
        project_task_action_to_invoice_fsm
        project_task_action_to_invoice_fsm_view_list
        project_task_action_to_invoice_fsm_view_kanban
        project_task_action_to_invoice_fsm_view_calendar
        project_task_action_to_invoice_fsm_view_form
        product_action_fsm
        project_task_server_action_batch_invoice_fsm

        # menus
        fsm_menu_all_tasks_invoice
        fsm_menu_settings_product
    """
    )
    for xid in renames:
        util.rename_xmlid(cr, *eb(f"industry_fsm{{,_sale}}.{xid}"))

    moves = {
        "project.project": {"allow_material", "allow_quotations", "timesheet_product_id"},
        "project.task": {
            "allow_material",
            "allow_quotations",
            "quotation_count",
            "material_line_product_count",
            "material_line_total_price",
            "currency_id",
            "invoice_count",
            "fsm_to_invoice",
        },
        "res.config.settings": {"group_industry_fsm_quotations"},
        "product.product": {"fsm_quantity"},
        "sale.order": {"task_id"},
    }

    for model, fields in moves.items():
        for field in fields:
            util.move_field_to_module(cr, model, field, "industry_fsm", "industry_fsm_sale")
